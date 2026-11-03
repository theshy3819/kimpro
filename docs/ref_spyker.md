# 참고 분석 — Spyker Cars (Awwwards Site of the Day, 2026-10-30)

- 사이트: https://www.spykercars.com (모델 쪽: https://spykercars.com/c8-preliator)
- 상: Awwwards SOTD 2026-10-30 (7.31) · Developer 7.04 · 제작 The Brink Agency
- 분석 도구: rea MCP(`list_browser_targets` · `analyze_web_bundle` · `inspect_web_page`) + CDP 스크롤 캡처(`_research/spyker/scan_deep.mjs`) + 네트워크 기록(`_research/spyker/net_log.mjs`). 코드·이미지는 가져오지 않고 짜임만 봤어요.

## 기술 구성 (rea가 확인한 것)
- Next.js(App Router) + React, webpack 번들 119개. 부드러운 스크롤은 Lenis, 화면 등장은 GSAP.
- 모델 쪽에는 `<canvas data-engine="three.js r183 webgpu">`가 4개 있어요. 장면마다 캔버스 하나.
- **차는 실시간 3D 모델이 아니에요.** 네트워크에 GLB/glTF가 없고, 대신 미리 렌더링한 프레임 묶음을 받아요.
  - `activeframe/samples/morning-orbit-desktop.af` 22MB — 차 주위를 도는 궤도 장면
  - `morning-intro-desktop.af` 7.8MB · `afternoon-desktop.af` 15MB · `evening-desktop.af` 16MB
  - `depth-scan/orbit-start-depth.jpg` — 첫 프레임의 깊이 지도(입체감 · 시차 효과용)
  - `leaves-color.jpg` · `leaves-normals.jpg` — 앞에 떠다니는 잎 효과, `hotspot-marker.svg` — 차 위 설명 점
  - 장면별 소리 `morning.mp3` · `afternoon.mp3`, 로더 · 스크롤 안내는 Lottie JSON
- 결론: "스크롤하면 차가 돌아가는" 효과는 **궤도 영상을 프레임으로 쪼개 캔버스에 스크롤 진행도대로 그리는 방식**이에요. 김프로 사이트도 같은 원리로 만들 수 있어요(Newtake 영상 → 프레임 → 캔버스).

## 장면 짜임 (C8 쪽, 1440×900)
1. 로더(Lottie 원) → 큰 장 제목 "THE MORNING"(좁은 장체 대문자) 위로 장면이 열림.
2. 화면 가득 고정(sticky) 캔버스: 스크롤에 따라 차가 앞 3/4 → 옆 → 뒤 3/4로 돎. 글은 거의 없음.
3. 캔버스가 왼쪽 절반(799px)으로 줄고 계속 고정, 오른쪽 칸에서 설명 카드가 차례로 올라옴(작은 사진 + 장체 제목 + 두세 줄 글). 왼쪽 차는 카드에 맞춰 계속 돎.
4. 화면 가득 사진 + 큰 글 "AIR IN, SOUND OUT." → 흰 바탕 큰 제목 "BUILT FOR THE ROAD / HONED ON THE TRACK".
5. 검은 장 제목 "THE AFTERNOON" → 달리는 장면 → 다시 왼쪽 차 + 오른쪽 큰 숫자(800 · 8.000 · 1.525)와 짧은 설명.
- 글꼴: 제목 futura-pt-condensed(좁은 대문자), 본문 swiss721. 강조색 없이 흑백 + 사진 색.

## 김프로에 가져올 것
- 첫 화면: 어두운 바탕에 차 하나, 스크롤로 차가 돌며 장 제목이 바뀜(고정 캔버스 + 프레임 넘기기).
- 둘째 장: 차를 왼쪽 절반에 고정하고 오른쪽에 서비스 카드(광택 · 유리막 코팅 · 부분도색 · 휠 복원 · 컷팅휠 · 유리 복원)를 하나씩 올림. 카드마다 차의 각도가 바뀌어 "그 부위"를 보여 줌.
- 숫자 장: 큰 숫자 + 짧은 설명(20년 · 블로그 시공 기록 글 수 등).
- 가져오지 않을 것: 소리, 잎 효과, 22MB짜리 큰 파일(김프로는 WebP 프레임 120장 안팎, 모바일은 더 적게).
