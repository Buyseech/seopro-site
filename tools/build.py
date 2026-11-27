#!/usr/bin/env python3
"""Builds the blog pages of seopro.si from content/posts/*.html.

The home page (public/index.html), privacy page and 404 are written by hand.
This script only (re)generates:
  public/<slug>/index.html   one page per post, at the same address the old WordPress site used
  public/blog/index.html     the list of all posts
  public/sitemap.xml

Run it after adding or editing a post:  python3 tools/build.py
Each post file starts with a few header lines (TITLE, H1, DESC, DATE), then the article HTML.
"""
import datetime, html, os, pathlib, re, shutil

# Scheduled publishing: a post whose DATE is after today (Ljubljana time) is not built.
# It is left out of the blog list, the home page, the sitemap and "Preberite še",
# and links to it from other pages are shown as plain text until it is published.
# Override the day with BUILD_DATE=YYYY-MM-DD.
def _today():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo("Europe/Ljubljana")).date().isoformat()
    except Exception:
        return datetime.date.today().isoformat()
TODAY = os.environ.get("BUILD_DATE") or _today()
UNPUBLISHED = set()

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
POSTS = ROOT / "content" / "posts"
SITE = "https://www.seopro.si"
MONTHS = ["januar", "februar", "marec", "april", "maj", "junij", "julij", "avgust", "september", "oktober", "november", "december"]
EMAIL = "igor@seopro.si"
# Staging: every page is noindex, nofollow. Set to False (and remove the X-Robots-Tag line in public/_headers) before seopro.si goes live.
STAGING = False
STAGING_ROBOTS = "noindex, nofollow"

ICON_MAIL = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>'
ICON_YT = '<svg viewBox="0 0 68 48" width="24" height="17" aria-hidden="true" focusable="false"><path d="M66.5 7.7a8.5 8.5 0 0 0-6-6C55.2.3 34 .3 34 .3S12.8.3 7.5 1.7a8.5 8.5 0 0 0-6 6C.1 13 .1 24 .1 24s0 11 1.4 16.3a8.5 8.5 0 0 0 6 6C12.8 47.7 34 47.7 34 47.7s21.2 0 26.5-1.4a8.5 8.5 0 0 0 6-6C67.9 35 67.9 24 67.9 24s0-11-1.4-16.3z" fill="#FF0000"/><path d="M27 34V14l18 10z" fill="#fff"/></svg>'
ICON_LI = '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><rect width="24" height="24" rx="4" fill="#0A66C2"/><path fill="#fff" d="M7.1 9.3H4.8V19h2.3V9.3zM6 5a1.35 1.35 0 1 0 0 2.7A1.35 1.35 0 0 0 6 5zm13.2 8.8c0-2.6-1.4-4.7-4-4.7-1.3 0-2.2.7-2.6 1.4V9.3H10.4V19h2.3v-4.8c0-1.3.3-2.6 1.9-2.6 1.6 0 1.6 1.5 1.6 2.7V19h2.3l.7-5.2z"/></svg>'

# Landing pages shown only in the mobile menu (desktop nav is already full)
MOBILE_EXTRA = [("/optimizacija-spletnih-strani/", "Optimizacija spletnih strani"), ("/seo-za-spletne-trgovine/", "SEO za spletne trgovine")]
NAV = [("/#who", "Komu pomagamo"), ("/#services", "Kako delamo"), ("/#results", "Rezultati"), ("/#people", "Ekipa"), ("/blog/", "Blog")]


def header():
    links = "\n".join(f'      <a href="{h}">{t}</a>' for h, t in NAV)
    mobile = "\n".join(f'    <a href="{h}">{t}</a>' for h, t in NAV[:2] + MOBILE_EXTRA + NAV[2:])
    return f'''<a class="skip" href="#main">Preskoči na vsebino</a>
<header class="site-header">
  <nav class="wrap nav" aria-label="Glavni meni">
    <a class="logo" href="/">SEOPRO<span>.</span></a>
    <div class="nav-links">
{links}
      <a class="btn btn--sm" href="/#review">Potrebujemo več strank</a>
      <button class="nav-toggle" type="button" aria-label="Odpri meni" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
    </div>
  </nav>
  <div class="mobile-menu" id="mobile-menu" hidden>
{mobile}
  </div>
</header>'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap footer-in">
    <div class="footer-top">
      <span class="footer-logo">SEOPRO<span>.</span></span>
      <div class="footer-links">
        <a href="mailto:{EMAIL}">{ICON_MAIL}<span>{EMAIL}</span></a>
        <a href="https://www.youtube.com/@Buyseech" target="_blank" rel="noopener">{ICON_YT}<span>YouTube</span></a>
        <a href="https://www.linkedin.com/in/igor-buyseech" target="_blank" rel="noopener">{ICON_LI}<span>LinkedIn</span></a>
      </div>
    </div>
    <p class="footer-copy">© 2026 SEOPRO.si · SEOPRO, spletna optimizacija, Igor Bajsić s.p. · <a href="/blog/">Blog</a> · <a href="/zasebnost/">Zasebnost in podatki o podjetju</a></p>
  </div>
</footer>

<script src="/site.js?v=1.1" defer></script>'''


def head(title, desc, url, og_type="website", extra="", robots="index, follow, max-image-preview:large"):
    if STAGING:
        robots = STAGING_ROBOTS
    t, d = html.escape(title), html.escape(desc)
    return f'''<!doctype html>
<html lang="sl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Google Analytics 4: add seopro.si's own GA4 snippet here (do not reuse the buyseech.com or seopack.net ID). -->
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="author" content="Igor Bajsić">
<meta name="theme-color" content="#04091A">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="SEOPRO.si">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/igor-buyseech.jpg">
<meta property="og:locale" content="sl_SI">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{SITE}/assets/img/igor-buyseech.jpg">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/anton-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css?v=1.5">
{extra}</head>'''


def sl_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)}. {MONTHS[int(m) - 1]} {y}"


def load_posts():
    posts = []
    for f in sorted(POSTS.glob("*.html")) if POSTS.exists() else []:
        text = f.read_text(encoding="utf-8")
        meta, body = {}, []
        lines = text.split("\n")
        i = 0
        while i < len(lines) and re.match(r"^[A-Z0-9]+: ", lines[i]):
            k, v = lines[i].split(": ", 1)
            meta[k] = v.strip()
            i += 1
        body = "\n".join(lines[i:]).strip()
        plain = re.sub(r"<[^>]+>", "", body)
        if meta.get("DATE", "") > TODAY:
            UNPUBLISHED.add(f.stem)
            continue
        posts.append(dict(slug=f.stem, body=body, words=len(plain.split()), **meta))
    posts.sort(key=lambda p: (-int(p["DATE"].replace("-", "")), int(p.get("NUM", "999"))))
    return posts


def card(p, level="h3"):
    return f'''<a class="sr-post" href="/{p['slug']}/">
        <time datetime="{p['DATE']}">{sl_date(p['DATE'])}</time>
        <{level}>{p['H1']}</{level}>
        <p>{html.escape(p['DESC'])}</p>
        <span class="more">Preberi več &rarr;</span>
      </a>'''


def label_tables(content):
    """Give each <td> a data-label with its column header, so tables can stack as cards on mobile."""
    def one(m):
        t = m.group(0)
        heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", t, re.S)]
        if not heads:
            return t
        def row(r):
            i = [0]
            def cell(c):
                k = i[0]; i[0] += 1
                if "data-label" in c.group(0) or k >= len(heads):
                    return c.group(0)
                return c.group(0)[:-1] + f' data-label="{html.escape(heads[k], quote=True)}">'
            return re.sub(r"<td(?:\s[^>]*)?>", cell, r.group(0))
        return re.sub(r"<tr[^>]*>.*?</tr>", row, t, flags=re.S)
    return re.sub(r"<table[^>]*>.*?</table>", one, content, flags=re.S)


def unlink_unpublished(content):
    """Turn links to not-yet-published posts into plain text."""
    if not UNPUBLISHED:
        return content
    alt = "|".join(re.escape(x) for x in UNPUBLISHED)
    pat = r'<a\b[^>]*\bhref="(?:https://(?:www\.)?seopro\.si)?/(?:' + alt + r')/[^"]*"[^>]*>(.*?)</a>'
    return re.sub(pat, r"\1", content, flags=re.S)


def write(path, content):
    if str(path).endswith(".html"):
        content = unlink_unpublished(content)
    if str(path).endswith(".html") and "<table" in content:
        content = label_tables(content)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_post(p, posts):
    url = f"{SITE}/{p['slug']}/"
    ld = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": html.unescape(re.sub(r"<[^>]+>", "", p["H1"])), "description": p["DESC"],
        "datePublished": p["DATE"], "inLanguage": "sl-SI", "mainEntityOfPage": url,
        "author": {"@type": "Person", "name": "Igor Bajsić", "url": "https://buyseech.com/"},
        "publisher": {"@type": "Organization", "name": "SEOPRO.si", "url": SITE + "/"},
        "image": SITE + "/assets/img/igor-buyseech.jpg",
    }
    import json
    graph = [ld, {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "SEOPRO", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
        {"@type": "ListItem", "position": 3, "name": ld["headline"], "item": url}]}]
    ld.pop("@context")
    m = re.search(r"<h2>Pogosta vprašanja.*?</h2>(.*?)(<h2>|$)", p["body"], flags=re.S)
    if m:
        qa = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", m.group(1), flags=re.S)
        strip = lambda t: html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qa]})
    extra = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>\n"
    by_slug = {o["slug"]: o for o in posts}
    others = [by_slug[x.strip()] for x in p.get("RELATED", "").split(",") if x.strip() in by_slug and x.strip() != p["slug"]]
    others += [o for o in posts if o["slug"] != p["slug"] and o not in others and o.get("CLUSTER") and o.get("CLUSTER") == p.get("CLUSTER")]
    others += [o for o in posts if o["slug"] != p["slug"] and o not in others]
    others = others[:3]
    related = "\n      ".join(card(o) for o in others)
    archive = f'<p class="sr-archive">Zapis iz arhiva SEOPRO bloga ({p['DATE'][:4]}). Osnove še vedno veljajo, nekatera orodja in številke pa so se od takrat spremenile.</p>' if p["DATE"] < "2026" else ""
    related_html = f'''<section class="sr-related" aria-labelledby="related-title">
      <h2 id="related-title">Preberite <span>še</span></h2>
      <div class="sr-posts">
      {related}
      </div>
    </section>''' if others else ""
    page = head(f"{p['TITLE']} | SEOPRO Blog", p["DESC"], url, "article", extra, p.get("ROBOTS", "index, follow, max-image-preview:large")) + f'''
<body>
{header()}

<main id="main" class="legal sr-article">
  <article class="wrap legal-in">
    <p class="eyebrow"><a href="/blog/">SEOPRO Blog</a></p>
    <h1 class="h2">{p['H1']}</h1>
    <p class="sr-meta"><time datetime="{p['DATE']}">{sl_date(p['DATE'])}</time> · Igor Bajsić · {max(1, round(p['words'] / 200))} min branja</p>
    {archive}
    <div class="sr-body">
{p['body']}
    </div>
    <p class="sr-sign">Igor Bajsić, SEOPRO</p>

    <aside class="sr-cta" aria-label="Brezplačna analiza">
      <h2>Vas zanima, kje se vaša stran <span>zatika?</span></h2>
      <p>Pošljite nam naslov spletne strani in ključne besede, za katere bi se radi prikazovali. Igor jo pregleda in vam pove, kaj bi prineslo največ.</p>
      <a class="btn" href="/#review">Brezplačna analiza strani</a>
    </aside>

    {related_html}
  </article>
</main>

{footer()}
</body>
</html>
'''
    write(PUB / p["slug"] / "index.html", page)


INFINITE_JS = """(function(){var l=document.getElementById('blogroll'),s=document.getElementById('blogroll-more');if(!l||!s)return;var c=[].slice.call(l.querySelectorAll('.sr-post')),n=0,B=9;l.classList.add('is-paged');function more(){c.slice(n,n+B).forEach(function(e){e.classList.add('is-shown')});n+=B;if(n>=c.length){s.remove();window.removeEventListener('scroll',check);window.removeEventListener('resize',check);if(o)o.disconnect()}}function check(){if(n<c.length&&s.getBoundingClientRect().top<window.innerHeight+600){more();requestAnimationFrame(check)}}var o='IntersectionObserver' in window?new IntersectionObserver(check,{rootMargin:'600px 0px'}):null;more();if(o)o.observe(s);window.addEventListener('scroll',check,{passive:true});window.addEventListener('resize',check);check()})();"""


def build_blog(posts):
    cards = "\n      ".join(card(p, "h2") for p in posts)
    if posts:
        cards_html = ('<div class="sr-posts" id="blogroll">\n      ' + cards + '\n    </div>\n'
                      '    <div class="sr-more" id="blogroll-more" aria-hidden="true"></div>\n'
                      '    <noscript><style>.sr-posts .sr-post{display:flex!important}</style></noscript>\n'
                      '    <script>' + INFINITE_JS + '</script>')
        h1, sub = 'Nasveti o SEO, <span>brez ovinkov.</span>', 'Zapisi Igorja Bajsića o optimizaciji spletnih strani za slovenski trg.'
    else:
        cards_html = '<p class="sr-soon"><a class="btn" href="/#review">Povečajmo vaše prihodke <span aria-hidden="true">&rarr;</span></a></p>'
        h1, sub = 'Blog <span>prihaja kmalu.</span>', 'Pripravljamo nove zapise o SEO, ki prinaša povpraševanja, naročila in prihodke. Do takrat nam pišite.'
    page = head("SEOPRO Blog: nasveti o optimizaciji spletnih strani", "Zapisi o SEO in optimizaciji spletnih strani: povratne povezave, on-site in off-site optimizacija, indeksiranje, varnost in lastništvo spletne strani.", SITE + "/blog/") + f'''
<body>
{header()}

<main id="main" class="sr-blog">
  <div class="wrap">
    <div class="results-head">
      <p class="eyebrow">SEOPRO Blog</p>
      <h1 class="h2">{h1}</h1>
      <p class="sp-sub">{sub}</p>
    </div>
    {cards_html}
  </div>
</main>

{footer()}
</body>
</html>
'''
    write(PUB / "blog" / "index.html", page)


def build_sitemap(posts, landings=()):
    urls = [(SITE + "/", "2026-11-27")] + [(f"{SITE}/{l}/", "2026-11-27") for l in landings] + [(SITE + "/blog/", "2026-11-27"), (SITE + "/trendi/", "2026-11-27"), (SITE + "/zasebnost/", "2026-11-27")]
    urls += [(f"{SITE}/{p['slug']}/", p["DATE"]) for p in posts if STAGING or "noindex" not in p.get("ROBOTS", "")]
    body = "\n".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    write(PUB / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')


def build_home_blog(posts):
    """Refresh the three newest posts in the home page's blog section (between the BLOG markers)."""
    idx = PUB / "index.html"
    s = idx.read_text(encoding="utf-8")
    cards = "\n      ".join(card(p) for p in posts[:3])
    s = re.sub(r"(<!-- BLOG:START -->).*?(<!-- BLOG:END -->)", lambda m: m.group(1) + "\n      " + cards + "\n      " + m.group(2), s, flags=re.S)
    idx.write_text(s, encoding="utf-8")


def build_shared_pages():
    """Put the shared header and footer into the hand-written pages (between the HEADER/FOOTER markers)."""
    for f in [PUB / "zasebnost" / "index.html", PUB / "trendi" / "index.html", PUB / "index.html"]:
        s = f.read_text(encoding="utf-8")
        robots = STAGING_ROBOTS if STAGING else "index, follow, max-image-preview:large"
        s = re.sub(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots}">', s, count=1)
        s = re.sub(r"<!-- HEADER -->.*?<!-- /HEADER -->", lambda m: "<!-- HEADER -->\n" + header() + "\n<!-- /HEADER -->", s, flags=re.S)
        s = re.sub(r"<!-- FOOTER -->.*?<!-- /FOOTER -->", lambda m: "<!-- FOOTER -->\n" + footer() + "\n<!-- /FOOTER -->", s, flags=re.S)
        f.write_text(unlink_unpublished(s), encoding="utf-8")


def build_redirects():
    out = []
    for line in (ROOT / "tools" / "redirects.src").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if line.startswith("#") or len(parts) < 3:
            out.append(line)
            continue
        src, dst, code = parts[:3]
        fb = next((x.split(":", 1)[1] for x in parts[3:] if x.startswith("until-published:")), "/")
        if dst.strip("/").split("/")[0].split("#")[0] in UNPUBLISHED:
            dst, code = fb, "302"
        out.append(f"{src} {dst} {code}")
    (PUB / "_redirects").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    posts = load_posts()
    for slug in UNPUBLISHED:
        shutil.rmtree(PUB / slug, ignore_errors=True)
    for p in posts:
        build_post(p, posts)
    build_blog(posts)
    build_sitemap(posts)
    build_shared_pages()
    import build as _self  # landings.py imports this file as a separate module
    _self.UNPUBLISHED.update(UNPUBLISHED)
    from landings import build_landings
    landings = build_landings()
    build_sitemap(posts, landings)
    build_redirects()
    print(f"Built {len(posts)} posts, {len(landings)} landing pages, blog list, sitemap. Scheduled (not built): {len(UNPUBLISHED)}.")
