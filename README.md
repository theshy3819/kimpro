# 김프로 광택 코팅 — 웹사이트 시안

광주광역시 북구 서암대로 113 · 010-6411-4123 · [네이버 블로그](https://blog.naver.com/kimpromall)

어두운 단색 화면에 차 한 대를 두고, **스크롤하면 보닛 흠집으로 다가가 광택 패드가 지나간 자리부터 깨끗해지고 다시 깨끗한 차로 물러나는** 첫 장 → 서비스 → 시공 기록 → 작업 순서 → 휠 컷팅기 → 오시는 길을 보여 주는 한 쪽짜리 사이트예요.

## 보는 법

```bash
cd C:/shy/kimpro
python -m http.server 8790 --bind 127.0.0.1
# 브라우저에서 http://127.0.0.1:8790/
```

`file://`로 열면 프레임 목록(`manifest.json`)을 못 읽어서 정지 사진 모드로 떠요. 꼭 로컬 서버로 여세요.

## 짜임

| 장 | 내용 | 움직임 |
|---|---|---|
| 첫 장 · 광택 장면(560vh, 마지막 22%는 깨끗한 차에 머묾) | "26년 전통 광택 코팅" → "유리 · 도장 · 휠 · 실내, 자동차 관리의 모든 것" → "필요한 곳만, 필요한 만큼" + 전화 단추 | 화면 가득 고정된 캔버스: 정면 → 보닛 잔흠집으로 확대 → 패드가 지나간 자리부터 깨끗해짐 → 줌아웃해 깨끗한 차, 아래 BEFORE → AFTER 막대 |
| 서비스 | 유리 복원 · 광택 · 유리막/언더코팅 · 덴트/판금 · 휠 복원/분체 · 컷팅휠 · 썬팅/PPF/루프스킨 · 실내 · 부분도색 | 왼쪽에 차 고정, 오른쪽 카드가 올라올 때마다 차가 그 부위 쪽으로 돎(카드의 `data-frame` 0~1) |
| 시공 기록 | "김프로의 손을 거쳐간 수많은 자동차", 26년 · 약 3,500대 · 1,020 · 750, 분류별 막대 15줄 — 시공 수는 **목업**([docs/content.md](docs/content.md)) | 숫자 세기, 막대 늘어남 |
| 작업 순서 | 다섯 단계 + 광택 전후 예시 | 나타나기 |
| 휠컷팅기 | 장비 판매 · 설치 안내 | — |
| 오시는 길 | 주소 · 전화 · 블로그 · 네이버/카카오 지도 | — |

- 디자인 기준: 시안 **HX 날렵**(검정 #0a0a0a 단색, 가는 큰 글, 큰 숫자). 괄호 꼬리표는 2026-11-03 요청으로 모두 뺐어요.
- 턴테이블 회전 차는 첫 장에서 빼고(서비스 칸과 겹쳐서) 서비스 칸 왼쪽에만 남겼어요.
- 3D 연출 기준: Awwwards SOTD **Spyker Cars**(2026-10-30) — 분석은 [docs/ref_spyker.md](docs/ref_spyker.md).
- 업체 내용: [docs/content.md](docs/content.md)(블로그에서 확인한 것만 씀).
- 글꼴: Pretendard(본문 · 제목), Barlow Condensed(영문 · 숫자). 부드러운 스크롤: Lenis 1.1.13.

## 3D 자동차 만드는 법

1. **기준 사진**: 로컬 Codex로 턴테이블 위 검은 패스트백 세단(상표 · 번호판 없음) — `_src/codex/brief.txt` → `assets/img/car-base.webp`.
2. **회전 영상**: Newtake MCP, Hailuo 2.3 · 이미지→영상 · 6초 · 1080P · 고정 카메라, "차만 180° 회전" 프롬프트. Newtake 프로젝트 `김프로 웹사이트 - 3D 자동차 턴테이블`. 결과는 배경 · 차 모양이 끝까지 유지됐지만 실제 회전은 앞 3/4 → 옆모습(약 60°)까지였어요. 뒤쪽까지 보이려면 마지막 프레임을 시작으로 한 번 더 생성해 이어 붙이면 돼요.
3. **프레임**: `PYTHONPATH=_tools/pylib python -I _tools/extract_frames.py <영상.mp4> 120` → `assets/turntable/{desktop,mobile}/f_000.webp` + `manifest.json`.
4. **재생**: `js/main.js`가 성긴 프레임부터 받아 캔버스에 스크롤 진행도대로 그려요. 프레임이 없으면 정지 사진을 천천히 움직이는 대체 모드.

## 광택 장면 만드는 법

1. **시작 프레임**: 로컬 Codex(`_src/codex2/brief.txt`, 첫 장 차 사진을 참고로 첨부) — 같은 검은 세단을 같은 어두운 스튜디오에서 정면으로, 보닛이 보이게 살짝 위에서. 보닛 조명 반사 주변에 잔흠집, 사람 없음 → `assets/img/polish-front.webp`(프레임이 없을 때 대체 사진).
2. **다가가기**: Newtake Hailuo 2.3 · `[Push in]` → `_src/newtake/front_polish_hailuo23.mp4`. 패드가 나오기 전인 앞 48프레임(0~2.0초)만 써요.
3. **확대 장면**: 48번 프레임의 보닛 가운데를 2.4배로 잘라 키운 그림(`_src/codex3/close_start.jpg`, 자리는 `crop_box.txt`)으로 Hailuo 2.3 · `[Static shot]`, "회색 패드가 왼쪽에서 오른쪽으로 지나간 자리만 깨끗해짐" → `_src/newtake/close_pad_sweep_hailuo23.mp4`.
4. **깨끗한 차**: 로컬 Codex로 48번 프레임에서 흠집만 지운 정면 사진(`_src/codex3/brief_clean.txt` → `gen/clean_wide.png`).
5. **잇기**: `PYTHONPATH=_tools/pylib python -I _tools/build_polish_v3.py` → `_src/newtake/polish_v3.mp4`
   — 다가가기 48프레임 → 48번 프레임을 2.4배까지 디지털 확대 → 확대 장면 전체 → 깨끗한 사진의 같은 자리로 겹쳐 넘김 → 2.4배에서 1배로 줌아웃 + 잠깐 멈춤.
6. **프레임**: `PYTHONPATH=_tools/pylib python -I _tools/extract_frames.py _src/newtake/polish_v3.mp4 144 polish 60,56` → `assets/polish/`.

(앞선 시도: 김프로 실제 사진 버전(`_src/real/`, 너무 실사), 두 장면 겹쳐 넘김 버전(`_tools/splice_shots.py`, 패드가 끝까지 지나가지 않음). 사이트에선 쓰지 않아요.)

Newtake에는 3D 모델(GLB) 생성 기능이 없어서, Spyker와 같은 "미리 찍은 회전 장면을 프레임으로 넘기는" 방식을 썼어요.

## 주의

- 광택 장면은 AI로 만든 **연출 영상**이에요(화면에 'AI 연출 영상' 표시).
- 그 밖의 사진은 모두 **AI로 만든 예시**예요(화면에 '예시 이미지' 표시). 실제 매장 · 작업 사진을 받으면 `assets/img/`에서 같은 이름으로 바꾸면 돼요.
- 영업시간 · 가격 · 보증 기간은 블로그에 없어서 넣지 않았어요(전화 상담 안내).
- 광고 낱말 규칙(최고 · 완벽 · 보장 · 무료 · 신차급 등 금지)은 H 시리즈 기획과 같아요. ("No.1", "바가지 無"는 "믿고 맡기는 곳", "투명한 견적 · 꼼꼼한 시공"으로 바꿨어요.)
- 시공 수는 **목업**이에요. 실제 수를 받으면 `index.html`의 `#record` 숫자(`data-count`)와 분류별 막대(`--v`)를 바꿔요.

## 상세 페이지(메뉴 대제목 세 묶음)

| 대제목 | 쪽 |
|---|---|
| **김프로** (ABOUT) | `about.html` 매장 소개 · `equipment.html` 휠컷팅기 장비 |
| **시공** (SERVICE) | `services.html` 시공 전체 · `service/{glass,polish,coating,dent,wheel,diamond-cut,film,interior,paint}.html` |
| **예약 · 오시는 길** (CONTACT) | `reserve.html` 예약하기 · `visit.html` 오시는 길 |

- 만들기: `python -I _tools/build_pages.py` — 위 14쪽을 만들고 홈(`index.html`)의 머리 · 꼬리말도 같은 것으로 바꿔요(여러 번 돌려도 같은 결과).
- 내용 고치기: `_tools/site_content.py`(문구) · `content/blog_posts.json`(블로그 분류별 최근 글 8편, 블로그 글 목록 API로 받음). 스타일은 `css/pages.css`, 동작은 `js/site.js`.
- 시공 상세 짜임: 사진 머리(제목 · 한 줄 · 전화/이 시공 예약하기) → 이럴 때 맡겨요 → 작업 순서(옆 사진 고정) → (광택 · 덴트만) 작업 전 · 후 → 김프로 시공 기록(블로그 실제 글 6편, 과장 낱말이 든 제목은 걸러요) → 알아 두면 좋아요(접기) → 함께 많이 맡기는 시공 → 상담 띠 → 이전 · 다음.
- 머리 메뉴: 데스크톱은 대제목에 올리면 판이 내려오고, 대제목을 누르면 그 묶음의 첫 쪽으로 가요(김프로 → 매장 소개, 시공 → 시공 전체, 예약 · 오시는 길 → 예약하기). 1023px까지는 메뉴 단추 → 전체 화면 메뉴(대제목도 같은 링크).
- 머리 오른쪽 위: 네이버 블로그 아이콘(흑백, 새 창) · 예약하기 · 전화 상담.
- 오른쪽 아래 고정: 맨 위로 단추(한 화면쯤 내려가면 나타남, 홈에선 Lenis로 부드럽게). 모바일에선 전화 상담 단추 위에 쌓여요.
- 네이버 지도 링크는 모두 `https://naver.me/GrmFT6SI`(`site_content.py`의 `NAVER_MAP`).
- 예약하기: 서버 없이 동작해요. 보내기를 누르면 입력 내용으로 문자를 만들어 휴대전화의 문자 앱을 열고(김프로 010-6411-4123 앞), 컴퓨터에서는 내용 복사 · 전화하기를 보여 줘요. 사이트에 저장하거나 전송하지 않아요. 상세 쪽의 "이 시공 예약하기"(`reserve.html?service=paint`)로 오면 그 시공이 미리 골라져요.
- 오시는 길 지도는 구글 지도 임베드(키 없음)를 어둡게 보이도록 필터를 씌웠어요. 네이버 · 카카오 지도는 버튼으로 열어요.
- 가격 · 영업시간 · 보증 기간은 블로그에 없어 넣지 않았어요(전화 상담).

## 다음 작업(요청 메모)

깊이(depth) 구현 — 시작함(위 상세 페이지). 남은 것: 실제 매장 · 작업 사진으로 교체, 시공별 가격 안내(받으면), 예약을 실제로 받을 창구(카카오톡 채널 · 네이버 예약 등) 연결.

## 폴더

```
index.html  css/style.css  js/main.js         홈(스크롤 장면)
about.html equipment.html services.html service/*.html reserve.html visit.html   상세 페이지(빌드로 만듦)
css/pages.css  js/site.js                       상세 · 공통 머리/꼬리말 · 예약 폼
content/blog_posts.json                         블로그 분류별 최근 글
assets/img/          사진(WebP)
assets/turntable/    회전 프레임 + manifest.json
assets/polish/       광택 장면 프레임 + manifest.json
docs/                업체 내용 · 참고 분석
_src/codex/          Codex 지시서 · 원본 PNG
_tools/              프레임 추출 · 화면 캡처 스크립트
_research/           블로그 · 참고 사이트 조사 자료(배포 제외)
```
