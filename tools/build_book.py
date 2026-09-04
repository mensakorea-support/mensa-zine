#!/usr/bin/env python3
"""
회지 PDF → 뷰어용 이미지 묶음(book/) 변환기
사용법:  python3 build_book.py 회지.pdf book --title "멘사코리아 회지 Vol.127" --zine-id mkj_vol127 --page-offset 2 [--toc toc.json] [--utm-campaign mkj_vol127]
필요:   poppler-utils (pdftoppm), pip install pillow pypdf
결과:   book/book.json, book/pages/NNN.webp(1200px), book/hi/NNN.webp(2200px), book/thumbs/NNN.webp(220px), book/cover.jpg
"""
import argparse, json, os, subprocess, sys, glob, shutil, tempfile
from concurrent.futures import ProcessPoolExecutor
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

def render(pdf, outdir, dpi):
    tmp = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', pdf, os.path.join(tmp, 'p')], check=True)
    return sorted(glob.glob(os.path.join(tmp, 'p-*.png')))

def encode(args):
    from PIL import Image
    f, n, out = args
    im = Image.open(f).convert('RGB'); W, H = im.size
    for kind, w, q in (('hi', 2200, 80), ('pages', 1200, 82), ('thumbs', 220, 75)):
        x = im if W <= w else im.resize((w, int(H * w / W)), Image.LANCZOS)
        x.save(os.path.join(out, kind, f'{n:03d}.webp'), 'WEBP', quality=q, method=4)
    if n == 1:
        c = im.resize((1200, int(H * 1200 / W)), Image.LANCZOS); c.save(os.path.join(out, 'cover.jpg'), 'JPEG', quality=85, optimize=True)
    return n

def add_utm(url, campaign, content):
    u = urlsplit(url); q = parse_qsl(u.query, keep_blank_values=True)
    q += [('utm_source', 'zine'), ('utm_medium', 'pdf'), ('utm_campaign', campaign), ('utm_content', content)]
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), u.fragment))

def links(pdf, campaign):
    import pypdf
    r = pypdf.PdfReader(pdf); out = {}
    for i, pg in enumerate(r.pages):
        an = pg.get('/Annots')
        if an is None: continue
        cb = pg.cropbox; x0, y0, x1, y1 = [float(v) for v in cb]; W = x1 - x0; H = y1 - y0
        items = []
        for ref in an.get_object():
            a = ref.get_object()
            if a.get('/Subtype') != '/Link' or a.get('/A') is None: continue
            uri = str(a['/A'].get_object().get('/URI') or '')
            if not uri: continue
            rx0, ry0, rx1, ry1 = [float(v) for v in a['/Rect']]
            items.append({'x': round((min(rx0, rx1) - x0) / W * 100, 2), 'y': round((y1 - max(ry0, ry1)) / H * 100, 2),
                          'w': round(abs(rx1 - rx0) / W * 100, 2), 'h': round(abs(ry1 - ry0) / H * 100, 2), 'uri': uri})
        for k, it in enumerate(items):
            host = urlsplit(it['uri']).hostname or 'link'
            cid = f"p{i+1}_{host.replace('www.', '').split('.')[0]}" + (f"_{k+1}" if sum(1 for x in items if urlsplit(x['uri']).hostname == urlsplit(it['uri']).hostname) > 1 else '')
            has = 'utm_content=' in it['uri']
            it['url'] = it['uri'] if has or not campaign else add_utm(it['uri'], campaign, cid)
            it['id'] = (parse_qsl(urlsplit(it['url']).query)and dict(parse_qsl(urlsplit(it['url']).query)).get('utm_content')) or cid
            del it['uri']
        if items: out[str(i + 1)] = items
    return out, len(r.pages), (float(r.pages[0].cropbox.width) / float(r.pages[0].cropbox.height))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('out')
    ap.add_argument('--title', default='회지'); ap.add_argument('--zine-id', default='zine')
    ap.add_argument('--page-offset', type=int, default=0); ap.add_argument('--toc', help='목차 JSON 파일 (index.html 편집기에서 만든 배열)')
    ap.add_argument('--utm-campaign', default='', help='광고 링크에 붙일 utm_campaign (비우면 링크 그대로)')
    ap.add_argument('--dpi', type=int, default=307)
    a = ap.parse_args()
    for d in ('pages', 'hi', 'thumbs'): os.makedirs(os.path.join(a.out, d), exist_ok=True)
    print('렌더링 중…'); files = render(a.pdf, a.out, a.dpi)
    print(f'{len(files)}쪽 → WebP 인코딩 중…')
    with ProcessPoolExecutor() as ex: list(ex.map(encode, [(f, i + 1, a.out) for i, f in enumerate(files)]))
    lk, n, ratio = links(a.pdf, a.utm_campaign)
    toc = json.load(open(a.toc, encoding='utf-8')) if a.toc else []
    book = {'title': a.title, 'zine_id': a.zine_id, 'pages': n, 'ratio': round(ratio, 5),
            'img': {'pages': f'{os.path.basename(a.out)}/pages/{{n}}.webp', 'hi': f'{os.path.basename(a.out)}/hi/{{n}}.webp', 'thumbs': f'{os.path.basename(a.out)}/thumbs/{{n}}.webp', 'pad': 3},
            'pdf': '', 'page_offset': a.page_offset, 'links': lk, 'toc': toc}
    json.dump(book, open(os.path.join(a.out, 'book.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    shutil.rmtree(os.path.dirname(files[0]), ignore_errors=True)
    print('완료:', a.out, '| 쪽수', n, '| 링크', sum(len(v) for v in lk.values()))

if __name__ == '__main__': main()
