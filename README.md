# 멘사코리아 회지 웹 뷰어

회지를 웹에서 책처럼 넘겨 보는 뷰어. 열람·페이지별 체류·광고 버튼 클릭·목차 이동이 GA4로 기록됩니다.
배포 주소: **https://mensakorea-support.github.io/mensa-zine/**

```
index.html            뷰어 (설정은 파일 맨 위)
book/
  book.json           쪽수·링크 좌표·목차
  pages/NNN.webp      본문 이미지 (1200px)
  hi/NNN.webp         확대용 고해상도 (2200px)
  thumbs/NNN.webp     썸네일
  cover.jpg           카톡 미리보기용 표지
tools/build_book.py   PDF → book/ 변환 스크립트
```

## 왜 이미지로 바꿨나

처음엔 폰이 PDF를 직접 읽어 그리는 방식이었는데, 느리고 일부 폰트·사진이 깨졌습니다. 지금은 PDF를 한 번만 정확히 이미지로 바꿔 두고(헤이진과 같은 방식) 뷰어는 이미지만 보여줍니다. 첫 화면 0.2초, 넘김 즉시, 어떤 기기에서도 똑같이 보입니다.

## 조작

| | PC | 모바일 |
|---|---|---|
| 넘기기 | 모서리 드래그, 페이지 클릭, ←→, 화살표 버튼 | 좌우 스와이프, **화면 오른쪽 30% 탭 = 다음 / 왼쪽 30% = 이전** |
| 메뉴 | 항상 표시 | 가운데 탭으로 숨김/표시 (3초 뒤 자동 숨김) |
| 확대 | 돋보기 버튼, 페이지 더블클릭 | 두 손가락 벌리기, 가운데 두 번 탭 |
| 목차 / 썸네일 | 하단 툴바 | 하단 툴바 |

## 다음 호 올리기

1. 디자이너에게 PDF를 받습니다 (낱장, 광고 버튼에 하이퍼링크 — 아래 규칙).
2. `book/` 폴더를 만듭니다. 두 가지 방법:
   - **클로드에게 PDF를 주고 "회지 변환해줘"** → book 폴더와 목차까지 만들어 깃허브에 올려줍니다.
   - 직접: poppler와 python이 있는 컴퓨터에서
     `python3 tools/build_book.py 회지.pdf book --title "멘사코리아 회지 Vol.127" --zine-id mkj_vol127 --page-offset 2 --utm-campaign mkj_vol127`
3. 깃허브 저장소에서 `book/` 폴더의 파일들을 교체하고(Upload files, 10MB씩 나눠서), `index.html` 은 그대로 둡니다. 제목·목차는 `book.json` 에 들어 있습니다.
4. 지난 호를 남기려면 `vol126/` 폴더를 만들어 그 호의 `index.html` 과 `book/` 을 넣어 두면 `…/mensa-zine/vol126/` 로 계속 열립니다.

## 목차

뷰어 주소 뒤에 `?edit=1` 을 붙여 열면 목차 편집기가 나옵니다. 책을 넘겨 글이 시작하는 쪽에서 제목 입력 → 「현재 쪽에 추가」, 구분은 「구분 추가」, 순서·삭제·쪽번호 수정 가능. 다 만들면 「설정 코드 복사」 → `index.html` 의 `TOC: [ ... ]` 자리에 붙여넣거나, `book.json` 의 `"toc"` 에 넣습니다. `index.html` 의 TOC 가 비어 있으면 `book.json` 의 목차를 씁니다.

`page` 는 회지에 **인쇄된 쪽번호**, `page_offset` 은 "인쇄 1쪽이 PDF 몇 번째 장인지 − 1" (Vol.126 = 2).

## 광고 버튼 링크 규칙 (디자이너 전달용)

```
https://광고주사이트.com/?utm_source=zine&utm_medium=pdf&utm_campaign=mkj_vol127&utm_content=p12_광고주명
```
`utm_content` 가 GA4의 `link_id` 로 기록됩니다. 링크에 utm_content 가 없으면 변환 스크립트가 `p쪽수_도메인` 으로 자동 생성합니다.
**폰트 주의**: 버튼·광고 텍스트는 아웃라인(윤곽선) 처리해서 내보내 달라고 하세요. 일부 폰트(Pretendard SemiBold 등)는 웹에서 글자가 겹칩니다.

## index.html 설정

```js
GA4_ID: "G-QJ7KSL58PQ",     // GA4 측정 ID
BOOK_URL: "book/book.json", // 이미지 묶음 위치
ZINE_ID: "", TITLE: "",     // 비우면 book.json 값 사용
DOWNLOAD_URL: "",           // PDF 저장 버튼에 연결할 파일 (비우면 버튼 숨김)
THEME: "light", ACCENT: "#2f6df6", BACKGROUND: "",
SHOW_EVENT_LOG: false,      // true 면 '추적 로그' 버튼 표시 (테스트용)
PAGE_OFFSET: null, TOC: []  // 비우면 book.json 값 사용
```

## 링크

- 기본: `https://mensakorea-support.github.io/mensa-zine/`
- 특정 쪽부터: `…/mensa-zine/#p=12`
- 유입 경로 구분: `…/mensa-zine/?utm_source=kakao&utm_medium=message&utm_campaign=mkj_vol126`
- 종이 회지 QR은 `go.mensakorea.org/zine` 같은 단축주소를 거치게 하세요.

## GA4

「GA4 세팅 가이드」 문서대로. 맞춤 측정기준(`zine_id`, `page_number`, `link_id`, `link_domain`, `view_mode`, `max_page`)과 맞춤 측정항목(`engagement_seconds`, `total_seconds`, `read_pct`)을 등록해야 보고서에 쪽번호가 보입니다.

| 이벤트 | 언제 | 주요 값 |
|---|---|---|
| `zine_open` | 뷰어 열림 | page_count, mode |
| `zine_page_view` / `zine_page_time` | 쪽이 보일 때 / 떠날 때 | page_number, engagement_seconds, view_mode |
| `zine_link_click` | 광고 버튼 클릭 | page_number, link_id, link_domain |
| `zine_toc_click` | 목차 이동 | to_page, title |
| `zine_zoom` / `zine_thumbs_open` / `zine_toc_open` / `zine_share` / `zine_fullscreen` | 각 기능 | page_number |
| `zine_exit` | 이탈 | last_page, max_page, pages_viewed, total_seconds, read_pct |

## 구성 요소
- 페이지 넘김: StPageFlip 2.0.7 (MIT) — index.html 안에 포함
- 이미지 변환: poppler(pdftoppm) + Pillow
