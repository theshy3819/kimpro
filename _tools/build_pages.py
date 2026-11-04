"""김프로 상세 페이지를 만들어요(머리 · 꼬리말을 모든 쪽에 같게).

    python -I _tools/build_pages.py

만드는 것
  about.html · equipment.html          (김프로)
  services.html · service/<slug>.html  (시공)
  reserve.html · visit.html            (예약 · 오시는 길)
  index.html의 머리 · 꼬리말도 같은 것으로 바꿔요.
내용은 _tools/site_content.py, 블로그 글 목록은 content/blog_posts.json.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_content as C  # noqa: E402

esc = html.escape
SV = {s["slug"]: s for s in C.SERVICES}
POSTS = json.loads((ROOT / "content" / "blog_posts.json").read_text(encoding="utf-8"))
BANNED = re.compile(r"최고|1위|최초|유일|최상|명품|완벽|보장|무료|할인|특가|최저가|이벤트|추천|베스트|영구|평생|무조건|100%|신차급|새 차처럼|새차처럼")
MAPS = {
    "naver": C.NAVER_MAP,
    "kakao": "https://map.kakao.com/?q=%EA%B4%91%EC%A3%BC%EA%B4%91%EC%97%AD%EC%8B%9C%20%EB%B6%81%EA%B5%AC%20%EC%84%9C%EC%95%94%EB%8C%80%EB%A1%9C%20113",
    "embed": "https://maps.google.com/maps?q=%EA%B4%91%EC%A3%BC%EA%B4%91%EC%97%AD%EC%8B%9C%20%EB%B6%81%EA%B5%AC%20%EC%84%9C%EC%95%94%EB%8C%80%EB%A1%9C%20113&z=17&output=embed",
}


def img(base, name, alt="", cls="", eager=False, w=1400, h=933):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{base}assets/img/{name}.webp" alt="{esc(alt)}" {load} width="{w}" height="{h}">'


# ---------------------------------------------------------------- 공통 틀
def head(title, desc, base, og="polish-front"):
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="theme-color" content="#0a0a0a">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{base}assets/img/{og}.webp">
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600&display=swap">
  <link rel="stylesheet" href="{base}css/style.css">
  <link rel="stylesheet" href="{base}css/pages.css">
</head>
<body class="sub">
  <a class="skip" href="#main">본문 바로가기</a>
"""


def nav_groups(base):
    groups = []
    for g in C.NAV:
        items = g["items"] or [(f"service/{s['slug']}.html", s["title"]) for s in C.SERVICES]
        groups.append({**g, "items": items})
    return groups


def header(base, active="", solid=True):
    groups = nav_groups(base)
    desk = []
    for g in groups:
        cur = ' aria-current="true"' if g["key"] == active else ""
        links = "".join(f'<li><a href="{base}{h}">{esc(t)}</a></li>' for h, t in g["items"])
        extra = ""
        if g["key"] == "service":
            extra = f'<a class="gnb__all" href="{base}services.html">시공 전체 보기 →</a>'
        cls = "gnb__panel gnb__panel--wide" if g["key"] == "service" else "gnb__panel"
        # 대제목을 누르면 그 묶음의 첫 쪽으로(시공은 시공 전체), 올리면 아래 판이 펼쳐져요
        top = g.get("href") or g["items"][0][0]
        desk.append(f"""      <li class="gnb__group" data-gnb>
        <a class="gnb__top" href="{base}{top}"{cur}><span class="gnb__en">{g['en']}</span>{esc(g['label'])}</a>
        <div class="{cls}"><ul>{links}</ul>{extra}</div>
      </li>""")
    mob = []
    for g in groups:
        links = "".join(f'<li><a href="{base}{h}">{esc(t)}</a></li>' for h, t in g["items"])
        if g["key"] == "service":
            links = f'<li><a href="{base}services.html">시공 전체</a></li>' + links
        top = g.get("href") or g["items"][0][0]
        mob.append(f'<div class="mnav__group"><a class="mnav__title" href="{base}{top}"><span class="gnb__en">{g["en"]}</span>{esc(g["label"])}</a><ul>{links}</ul></div>')
    return f"""
  <header class="hdr{' is-solid' if solid else ''}" data-hdr>
    <a class="hdr__brand" href="{base}index.html" aria-label="김프로 처음으로">
      <span class="hdr__mark">KIMPRO</span>
      <span class="hdr__name">김프로 광택 코팅</span>
    </a>
    <nav class="gnb" aria-label="주요 메뉴">
      <ul class="gnb__list">
{chr(10).join(desk)}
      </ul>
    </nav>
    <div class="hdr__actions">
      <a class="hdr__blog" href="{C.BLOG}" target="_blank" rel="noopener" aria-label="김프로 네이버 블로그(새 창)" title="네이버 블로그">
        <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true" focusable="false"><rect x="0.75" y="0.75" width="22.5" height="22.5" rx="6" fill="none" stroke="currentColor" stroke-width="1.5"/><path fill="currentColor" d="M7.6 5.8h2.3v4.3c.6-.8 1.6-1.3 2.7-1.3 2.2 0 3.8 1.7 3.8 4.1s-1.6 4.1-3.8 4.1c-1.1 0-2.1-.5-2.7-1.3v1.1H7.6V5.8Zm4.5 5.1c-1.2 0-2.2.9-2.2 2.1s1 2.1 2.2 2.1 2.1-.9 2.1-2.1-.9-2.1-2.1-2.1Z"/></svg>
      </a>
      <a class="btn btn--ghost hdr__reserve" href="{base}reserve.html">예약하기</a>
      <a class="btn btn--light hdr__call" href="{C.TEL}"><span class="hdr__call-label">전화 상담</span> {C.PHONE}</a>
      <button class="hdr__menu" type="button" aria-expanded="false" aria-controls="mnav" data-menu><span></span><span></span><span class="sr-only">메뉴 열기</span></button>
    </div>
  </header>
  <div class="mnav" id="mnav" hidden data-mnav>
    <div class="mnav__inner">
      {''.join(mob)}
      <div class="mnav__cta"><a class="btn btn--light" href="{C.TEL}">전화 상담 {C.PHONE}</a><a class="btn btn--ghost" href="{base}reserve.html">예약하기</a></div>
    </div>
  </div>
"""


def footer(base):
    groups = nav_groups(base)
    cols = []
    for g in groups:
        items = g["items"]
        if g["key"] == "service":
            items = [("services.html", "시공 전체")] + items
        links = "".join(f'<li><a href="{base}{h}">{esc(t)}</a></li>' for h, t in items)
        cols.append(f'<div class="ftr__nav"><p class="ftr__title">{esc(g["label"])}</p><ul>{links}</ul></div>')
    return f"""
  <footer class="ftr wrap">
    <p class="ftr__mark">KIMPRO</p>
    <div class="ftr__grid">
      <div class="ftr__info"><p>김프로 광택 코팅<br>{C.ADDRESS}<br><a href="{C.TEL}">{C.PHONE}</a><br><a href="{C.BLOG}" target="_blank" rel="noopener">네이버 블로그 ↗</a></p></div>
      {''.join(cols)}
    </div>
    <p class="fine ftr__note">사이트의 사진 · 영상은 작업을 설명하기 위한 AI 생성 예시예요. 실제 매장 · 차량 사진이 아니에요.</p>
  </footer>
"""


TOTOP = """  <button class="totop" type="button" aria-label="맨 위로" data-totop><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M12 19V5M5.5 11.5 12 5l6.5 6.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
"""


def tail(base, fab_on=True):
    return f"""
  <a class="fab{' is-on' if fab_on else ''}" href="{C.TEL}" aria-label="김프로에 전화하기 {C.PHONE}">전화 상담</a>
{TOTOP}  <script src="{base}js/site.js" defer></script>
</body>
</html>
"""


def page(path, title, desc, body, active, base, og="polish-front"):
    out = head(title, desc, base, og) + header(base, active) + '\n  <main id="main">\n' + body + "\n  </main>\n" + footer(base) + tail(base)
    (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / path).write_text(out, encoding="utf-8")
    return path


def cta_band(base, title="견적은 차를 보고 알려 드려요", text="사진만으로는 손상 깊이를 알기 어려워요. 전화로 먼저 상담하고 방문 날짜를 잡아요.", reserve_q=""):
    return f"""
    <section class="cta-band">
      <div class="wrap cta-band__in" data-rv>
        <h2 class="h2">{esc(title)}</h2>
        <p class="lede lede--dim">{esc(text)}</p>
        <div class="cta-row"><a class="btn btn--light" href="{C.TEL}">전화 상담 {C.PHONE}</a><a class="btn btn--ghost" href="{base}reserve.html{reserve_q}">예약하기</a></div>
      </div>
    </section>"""


def blog_posts(cats, n=6):
    rows = []
    for c in cats:
        rows += POSTS.get(str(c), {}).get("posts", [])
    clean = [p for p in rows if not BANNED.search(p["title"])]
    use = clean if len(clean) >= 4 else rows
    use = sorted({p["logNo"]: p for p in use}.values(), key=lambda p: p["date"], reverse=True)[:n]
    return use


def posts_block(cats, title="김프로 시공 기록"):
    items = "".join(
        f'<li><a href="{p["url"]}" target="_blank" rel="noopener"><span class="posts__date">{p["date"]}</span><span class="posts__title">{esc(p["title"])}</span><span class="posts__arrow" aria-hidden="true">↗</span></a></li>'
        for p in blog_posts(cats))
    more = f"https://blog.naver.com/PostList.naver?blogId=kimpromall&categoryNo={cats[0]}"
    return f"""
    <section class="sec wrap">
      <div class="sec__head" data-rv><h2 class="h2">{esc(title)}</h2><a class="more" href="{more}" target="_blank" rel="noopener">블로그에서 더 보기 ↗</a></div>
      <ul class="posts" data-rv>{items}</ul>
    </section>"""


def card(base, s):
    return f"""<li class="card" data-rv><a href="{base}service/{s['slug']}.html">
          <figure class="card__fig">{img(base, s['hero'], '')}</figure>
          <p class="card__no">{s['no']} · {s['en']}</p>
          <h3 class="card__title">{esc(s['title'])}</h3>
          <p class="card__txt">{esc(s['short'])}</p>
        </a></li>"""


# ---------------------------------------------------------------- 시공 상세
def service_page(s, i):
    b = "../"
    when = "".join(f'<li data-rv><span class="when__no">{k+1:02d}</span><p>{esc(t)}</p></li>' for k, t in enumerate(s["when"]))
    steps = "".join(f'<li class="flow__step" data-rv><span class="flow__no">{k+1:02d}</span><div><h3>{esc(a)}</h3><p>{esc(t)}</p></div></li>' for k, (a, t) in enumerate(s["steps"]))
    faq = "".join(f'<details class="faq__item" data-rv><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in s["faq"])
    rel = "".join(card(b, SV[r]) for r in s["related"])
    compare = ""
    if s.get("compare"):
        a, z = s["compare"]
        compare = f"""
    <section class="sec wrap">
      <h2 class="h2" data-rv>작업 전 · 후</h2>
      <div class="compare compare--wide" data-rv>
        <figure>{img(b, a, '작업 전 예시', w=1254, h=1254)}<figcaption>작업 전</figcaption></figure>
        <figure>{img(b, z, '작업 후 예시', w=1254, h=1254)}<figcaption>작업 후</figcaption></figure>
        <p class="ai-note ai-note--static">예시 이미지</p>
      </div>
    </section>"""
    prev_s = C.SERVICES[i - 1]
    next_s = C.SERVICES[(i + 1) % len(C.SERVICES)]
    body = f"""
    <section class="phero">
      <div class="phero__media">{img(b, s['hero'], s['title'] + ' 작업 예시', eager=True)}<p class="ai-note">예시 이미지</p></div>
      <div class="phero__txt wrap">
        <nav class="crumbs" aria-label="현재 위치"><a href="{b}services.html">시공</a><span aria-hidden="true">/</span><span aria-current="page">{esc(s['title'])}</span></nav>
        <p class="phero__no">{s['no']} · {s['en']}</p>
        <h1 class="h1">{esc(s['title'])}</h1>
        <p class="lede">{esc(s['lead'])}</p>
        <div class="cta-row"><a class="btn btn--light" href="{C.TEL}">전화 상담</a><a class="btn btn--ghost" href="{b}reserve.html?service={s['slug']}">이 시공 예약하기</a></div>
      </div>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>이럴 때 맡겨요</h2>
      <ul class="when">{when}</ul>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>작업 순서</h2>
      <div class="flow-wrap">
        <ol class="flow">{steps}</ol>
        <figure class="flow__fig" data-rv>{img(b, s['side'], '')}<p class="ai-note ai-note--static">예시 이미지</p></figure>
      </div>
    </section>
{compare}
{posts_block(s['cats'])}

    <section class="sec wrap">
      <h2 class="h2" data-rv>알아 두면 좋아요</h2>
      <div class="faq">{faq}</div>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>함께 많이 맡기는 시공</h2>
      <ul class="cards">{rel}</ul>
    </section>
{cta_band(b, reserve_q='?service=' + s['slug'])}

    <nav class="pager wrap" aria-label="다른 시공">
      <a class="pager__prev" href="{prev_s['slug']}.html"><span>이전</span>{esc(prev_s['title'])}</a>
      <a class="pager__all" href="{b}services.html">시공 전체</a>
      <a class="pager__next" href="{next_s['slug']}.html"><span>다음</span>{esc(next_s['title'])}</a>
    </nav>"""
    desc = f"{s['title']} — {s['lead']} 광주 김프로 {C.PHONE}"
    return page(f"service/{s['slug']}.html", f"{s['title']} | 김프로 광택 코팅", desc, body, "service", b, og=s["hero"])


def services_index():
    b = ""
    cards = "".join(card(b, s) for s in C.SERVICES)
    body = f"""
    <section class="ptitle wrap">
      <h1 class="h1" data-rv>시공</h1>
      <p class="lede lede--dim" data-rv>유리 · 도장 · 휠 · 실내까지, 김프로가 맡는 아홉 가지 시공이에요.</p>
    </section>
    <section class="sec sec--tight wrap">
      <ul class="cards cards--3">{cards}</ul>
    </section>
{cta_band(b, '어떤 시공이 맞을지 모르겠다면', '상처 사진을 보내 주시거나 전화로 상태를 말씀해 주세요. 맞는 방법부터 같이 정해요.')}"""
    return page("services.html", "시공 | 김프로 광택 코팅", "광택 · 유리막코팅 · 부분도색 · 덴트 · 휠 복원 · 다이아몬드 컷팅휠 · 유리 복원 · 썬팅 · 실내크리닝. 광주 김프로", body, "service", b)


# ---------------------------------------------------------------- 김프로
def about_page():
    b, a = "", C.ABOUT
    story = "".join(f'<div class="story__item" data-rv><h3>{esc(t)}</h3><p>{esc(x)}</p></div>' for t, x in a["story"])
    pr = "".join(f'<li data-rv><span class="when__no">{k+1:02d}</span><h3>{esc(t)}</h3><p>{esc(x)}</p></li>' for k, (t, x) in enumerate(a["principles"]))
    stats = ""
    for st in a["stats"]:
        num, unit, label = st[0], st[1], st[2]
        pre = f'<span class="stat__pre">{st[3]}</span>' if len(st) > 3 else ""
        stats += f'<div class="stat" data-rv>{pre}<span class="stat__num">{num}</span><span class="stat__unit">{unit}</span><p class="stat__label">{label}</p></div>'
    space = "".join(f'<figure data-rv>{img(b, k, "")}</figure>' for k in a["space"])
    cards = "".join(card(b, s) for s in C.SERVICES[:6])
    body = f"""
    <section class="phero phero--tall">
      <div class="phero__media">{img(b, 'shop-night', '밤에 불이 켜진 작업장 예시', eager=True, w=1672, h=941)}<p class="ai-note">예시 이미지</p></div>
      <div class="phero__txt wrap">
        <nav class="crumbs" aria-label="현재 위치"><a href="about.html">김프로</a><span aria-hidden="true">/</span><span aria-current="page">매장 소개</span></nav>
        <p class="phero__no">{esc(a['kicker'])}</p>
        <h1 class="h1">광주 내/외장 복원은<br>김프로</h1>
        <p class="lede">{esc(a['lead'])}</p>
      </div>
    </section>

    <section class="sec wrap">
      <div class="stats">{stats}</div>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>김프로 이야기</h2>
      <div class="story">{story}</div>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>일하는 방식</h2>
      <ul class="when when--4">{pr}</ul>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>작업 공간</h2>
      <div class="gallery">{space}<p class="ai-note ai-note--static">예시 이미지</p></div>
    </section>

    <section class="sec wrap">
      <div class="sec__head" data-rv><h2 class="h2">맡기는 시공</h2><a class="more" href="services.html">시공 전체 보기 →</a></div>
      <ul class="cards">{cards}</ul>
    </section>
{cta_band(b, '맡길 차가 있으면 먼저 전화 주세요', '예약 뒤 방문해 주세요. 차를 보고 필요한 만큼만 권해 드려요.')}"""
    return page("about.html", "매장 소개 | 김프로 광택 코팅", f"{a['kicker']}. {a['lead']}", body, "kimpro", b, og="shop-night")


def equipment_page():
    b, e = "", C.EQUIPMENT
    feats = "".join(f'<li data-rv><span class="when__no">{k+1:02d}</span><h3>{esc(t)}</h3><p>{esc(x)}</p></li>' for k, (t, x) in enumerate(e["features"]))
    steps = "".join(f'<li class="flow__step" data-rv><span class="flow__no">{k+1:02d}</span><div><h3>{esc(t)}</h3><p>{esc(x)}</p></div></li>' for k, (t, x) in enumerate(e["steps"]))
    body = f"""
    <section class="phero">
      <div class="phero__media">{img(b, 'wheel-cut', '휠 선반에서 휠 면을 깎는 모습 예시', eager=True)}<p class="ai-note">예시 이미지</p></div>
      <div class="phero__txt wrap">
        <nav class="crumbs" aria-label="현재 위치"><a href="about.html">김프로</a><span aria-hidden="true">/</span><span aria-current="page">{esc(e['title'])}</span></nav>
        <p class="phero__no">EQUIPMENT</p>
        <h1 class="h1">휠 컷팅기<br>장비 설치 문의</h1>
        <p class="lede">{esc(e['lead'])}</p>
        <div class="cta-row"><a class="btn btn--light" href="{C.TEL}">장비 문의 {C.PHONE}</a><a class="btn btn--ghost" href="reserve.html?service=equipment">문의 남기기</a></div>
      </div>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>장비 특징</h2>
      <ul class="when when--4">{feats}</ul>
    </section>

    <section class="sec wrap">
      <h2 class="h2" data-rv>설치까지</h2>
      <div class="flow-wrap">
        <ol class="flow">{steps}</ol>
        <figure class="flow__fig" data-rv>{img(b, 'tools', '')}<p class="ai-note ai-note--static">예시 이미지</p></figure>
      </div>
    </section>
{posts_block(e['cats'], '장비 설치 기록')}
{cta_band(b, '휠 복원 창업을 준비한다면', '작업 공간과 하려는 휠 작업을 알려 주시면 맞는 구성부터 이야기해요.', '?service=equipment')}"""
    return page("equipment.html", "휠컷팅기 장비 | 김프로 광택 코팅", e["lead"], body, "kimpro", b, og="wheel-cut")


# ---------------------------------------------------------------- 예약 · 오시는 길
def visit_page():
    b = ""
    body = f"""
    <section class="ptitle wrap">
      <nav class="crumbs" aria-label="현재 위치"><a href="reserve.html">예약 · 오시는 길</a><span aria-hidden="true">/</span><span aria-current="page">오시는 길</span></nav>
      <h1 class="h1" data-rv>오시는 길</h1>
      <p class="lede lede--dim" data-rv>광주 신안동 자동차의 거리, 서암대로 113이에요. 예약 뒤 방문해 주세요.</p>
    </section>
    <section class="sec sec--tight wrap">
      <div class="visit2">
        <div class="map" data-rv><iframe title="김프로 위치 지도" src="{MAPS['embed']}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
        <div class="visit2__info" data-rv>
          <dl class="info">
            <div><dt>주소</dt><dd>{C.ADDRESS}</dd></div>
            <div><dt>전화</dt><dd><a href="{C.TEL}">{C.PHONE}</a></dd></div>
            <div><dt>방문</dt><dd>예약 뒤 방문해 주세요. 작업 시간은 전화로 맞춰요.</dd></div>
            <div><dt>블로그</dt><dd><a href="{C.BLOG}" target="_blank" rel="noopener">blog.naver.com/kimpromall</a></dd></div>
          </dl>
          <div class="cta-row">
            <a class="btn btn--light" href="{MAPS['naver']}" target="_blank" rel="noopener">네이버 지도 ↗</a>
            <a class="btn btn--ghost" href="{MAPS['kakao']}" target="_blank" rel="noopener">카카오맵 ↗</a>
            <a class="btn btn--ghost" href="{C.TEL}">전화하기</a>
          </div>
        </div>
      </div>
    </section>
    <section class="sec wrap">
      <figure class="wide-fig" data-rv>{img(b, 'shop-night', '불 켜진 작업장 문이 열린 밤의 매장 예시', w=1672, h=941)}<p class="ai-note">예시 이미지</p></figure>
    </section>
{cta_band(b, '방문 전에 예약해 주세요', '차종과 상태를 미리 알려 주시면 방문 날짜와 시간을 맞춰 드려요.')}"""
    return page("visit.html", "오시는 길 | 김프로 광택 코팅", f"{C.ADDRESS} · {C.PHONE} · 예약 후 방문", body, "contact", b, og="shop-night")


def reserve_page():
    b = ""
    opts = [(s["slug"], s["title"]) for s in C.SERVICES] + [("equipment", "휠컷팅기 장비 문의"), ("unsure", "잘 모르겠어요(상담)")]
    checks = "".join(f'<label class="chip"><input type="checkbox" name="service" value="{v}" data-label="{esc(t)}"><span>{esc(t)}</span></label>' for v, t in opts)
    body = f"""
    <section class="ptitle wrap">
      <nav class="crumbs" aria-label="현재 위치"><a href="reserve.html">예약 · 오시는 길</a><span aria-hidden="true">/</span><span aria-current="page">예약하기</span></nav>
      <h1 class="h1" data-rv>예약하기</h1>
      <p class="lede lede--dim" data-rv>차와 원하는 시공을 적어 보내 주시면 확인하고 전화로 날짜를 맞춰 드려요. 급하면 바로 전화 주세요.</p>
    </section>
    <section class="sec sec--tight wrap">
      <div class="reserve">
        <form class="rform" data-reserve novalidate>
          <fieldset>
            <legend>원하는 시공 <em>여러 개 고를 수 있어요</em></legend>
            <div class="chips" data-required-group>{checks}</div>
            <p class="rform__err" data-err="service" hidden>시공을 하나 이상 골라 주세요.</p>
          </fieldset>
          <fieldset>
            <legend>차량</legend>
            <div class="row2">
              <label class="field"><span>차종 *</span><input name="car" required placeholder="예: 그랜저, 싼타페" autocomplete="off"></label>
              <label class="field"><span>연식</span><input name="year" inputmode="numeric" placeholder="예: 2019" autocomplete="off"></label>
            </div>
            <label class="field"><span>차 상태</span><textarea name="memo" rows="4" placeholder="예: 운전석 문에 문콕, 앞범퍼 오른쪽 긁힘"></textarea></label>
          </fieldset>
          <fieldset>
            <legend>방문 희망</legend>
            <div class="row2">
              <label class="field"><span>날짜</span><input type="date" name="date"></label>
              <label class="field"><span>시간대</span><select name="time"><option value="">상관없어요</option><option>오전</option><option>오후</option></select></label>
            </div>
          </fieldset>
          <fieldset>
            <legend>연락처</legend>
            <div class="row2">
              <label class="field"><span>이름 *</span><input name="name" required autocomplete="name"></label>
              <label class="field"><span>휴대전화 *</span><input type="tel" name="phone" required inputmode="tel" placeholder="010-0000-0000" autocomplete="tel"></label>
            </div>
          </fieldset>
          <p class="fine">입력한 내용은 이 사이트에 저장되지 않아요. 보내기를 누르면 휴대전화의 문자 앱이 열리고, 김프로({C.PHONE})에게 보낼 문자가 채워져요.</p>
          <button class="btn btn--light btn--block" type="submit">문자로 예약 요청 보내기</button>
        </form>

        <div class="rdone" data-done hidden tabindex="-1">
          <h2 class="h2">보낼 내용을 만들었어요</h2>
          <p class="lede lede--dim">문자 앱이 열리지 않았다면 아래 내용을 복사해 {C.PHONE}로 보내거나 전화 주세요.</p>
          <pre class="rdone__msg" data-msg></pre>
          <div class="cta-row">
            <a class="btn btn--light" data-sms href="sms:01064114123">문자 앱 열기</a>
            <button class="btn btn--ghost" type="button" data-copy>내용 복사</button>
            <a class="btn btn--ghost" href="{C.TEL}">전화하기</a>
          </div>
          <button class="rdone__back" type="button" data-back>← 다시 고치기</button>
        </div>

        <aside class="reserve__side" data-rv>
          <h2 class="h3">전화가 더 빨라요</h2>
          <p><a class="reserve__tel" href="{C.TEL}">{C.PHONE}</a></p>
          <p class="fine">작업 중에는 전화를 못 받을 수 있어요. 문자를 남겨 주시면 확인하고 연락드려요.</p>
          <a class="more" href="visit.html">오시는 길 →</a>
        </aside>
      </div>
    </section>"""
    return page("reserve.html", "예약하기 | 김프로 광택 코팅", f"원하는 시공과 차량을 적어 문자로 예약 요청을 보내 주세요. {C.PHONE}", body, "contact", b)


# ---------------------------------------------------------------- 홈 머리 · 꼬리말 맞추기
def patch_home():
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'\n\s*<header class="hdr[^"]*" data-hdr>.*?</header>(\s*<div class="mnav".*?</div>\s*</div>\s*</div>)?\n', header("", "", solid=False), s, count=1, flags=re.S)
    s = re.sub(r'\n\s*<footer class="ftr wrap">.*?</footer>\n', footer(""), s, count=1, flags=re.S)
    if "data-totop" not in s:
        s = re.sub(r'(<a class="fab[^"]*"[^>]*>전화 상담</a>\n)', lambda m: m.group(1) + TOTOP, s, count=1)
    if 'css/pages.css' not in s:
        s = s.replace('<link rel="stylesheet" href="css/style.css">', '<link rel="stylesheet" href="css/style.css">\n  <link rel="stylesheet" href="css/pages.css">')
    if 'js/site.js' not in s:
        s = s.replace('<script src="js/main.js" defer></script>', '<script src="js/site.js" defer></script>\n  <script src="js/main.js" defer></script>')
    # 홈 서비스 카드 → 상세 쪽 링크
    for sv in C.SERVICES:
        tag = f'<p class="svc__no">{sv["no"]} · {sv["en"]}</p>'
        if tag in s and f'class="svc__more" href="service/{sv["slug"]}.html"' not in s:
            s = re.sub(re.escape(tag) + r'(.*?)</p>\n(\s*)</div>', lambda m: tag + m.group(1) + f'</p>\n{m.group(2)}  <a class="svc__more" href="service/{sv["slug"]}.html">자세히 보기 →</a>\n{m.group(2)}</div>', s, count=1, flags=re.S)
    p.write_text(s, encoding="utf-8")
    return "index.html"


if __name__ == "__main__":
    made = [service_page(s, i) for i, s in enumerate(C.SERVICES)]
    made += [services_index(), about_page(), equipment_page(), visit_page(), reserve_page(), patch_home()]
    print(len(made), "pages:", ", ".join(made))
