"""Builds the landing pages from content/landings/*.html.

Each file starts with TITLE/DESC/H1 lines, then the page body. Placeholders:
{{PROOF}} the numbers band, {{CASES}} the first two case studies and {{REVIEW}} the
contact form are copied from public/index.html, so they always match the home page.
{{FAQ}} is filled from FAQS below and also goes into the FAQPage schema.
"""
import html, json, re
from build import ROOT, PUB, SITE, head, header, footer, write

LANDINGS = ROOT / "content" / "landings"

FAQS = {
    "optimizacija-spletnih-strani": [
        ("Kaj pomeni SEO?", "SEO (Search Engine Optimization) pomeni optimizacijo za iskalnike: urejanje spletne strani in njenega ugleda na spletu, da jo Google pokaže čim višje ljudem, ki iščejo to, kar prodajate. Cilj so povpraševanja, naročila in prihodki iz Googla."),
        ("Kaj je razlika med SEO in optimizacijo spletne strani?", "V praksi gre za isto stvar. SEO je mednarodni izraz, optimizacija spletnih strani pa slovenski. Oba pomenita urejanje tehnike, vsebine in povezav, da se stran bolje uvršča v Googlu in drugih iskalnikih."),
        ("Ali lahko SEO naredim sam?", "Osnove lahko uredite sami: povežete stran s Search Consolom, vsaki storitvi namenite svojo stran, uredite naslove in meta opise ter pospešite stran. Pri konkurenčnih iskanjih, spletnih trgovinah in večjih straneh pa odločajo tehnične podrobnosti, izbira ključnih besed in povezave, kjer se izkušnje hitro poznajo."),
        ("Kaj je prvi korak pri optimizaciji spletne strani?", "Povežite stran z Google Search Console in preverite, za katera iskanja se že prikazujete in na katerem mestu. Iz tega vidite, katere strani so blizu prve strani Googla, kar so običajno najhitrejše priložnosti."),
        ("Ali je SEO brezplačen ali plačljiv?", "Klikov iz organskega iskanja ne plačate, plačate pa delo, ki stran pripelje na prvo stran: tehnične popravke, vsebino in povezave. Oglasi delajo le, dokler plačujete, organske pozicije pa prinašajo obisk tudi po opravljenem delu."),
        ("Koliko časa traja, da SEO začne delovati?", "Prve premike pogosto vidimo v nekaj tednih, posebej po tehničnih popravkih. Stabilna rast pri konkurenčnih iskanjih običajno pride v 3 do 6 mesecih ali več, odvisno od konkurence, zgodovine strani in tega, koliko sprememb na strani uvedete."),
        ("Ali je SEO boljši od Google oglasov?", "Odvisno od cilja. Oglasi prinesejo obisk takoj, a le dokler plačujete. SEO potrebuje več časa, vendar na dolgi rok za večino podjetij prinese cenejša povpraševanja. Veliko podjetij uporablja oboje, SEOPRO pa dela samo SEO."),
        ("Ali je dovolj samo vsebina brez tehničnega SEO?", "Ne. Če Google strani ne more pravilno najti in indeksirati ali če je stran prepočasna, tudi najboljša vsebina ne pride do kupcev. Tehnični SEO je temelj, vsebina in povezave pa gradijo na njem."),
        ("Kako vem, ali je moja stran že optimizirana?", "V Search Consolu preverite, za katera iskanja se prikazujete in na katerem mestu ter ali so vse pomembne strani indeksirane. Če vas za glavne storitve ni na prvi strani Googla ali obisk ne prinaša povpraševanj, je prostora za izboljšave še veliko."),
        ("Ali delate tudi za lokalna podjetja in spletne trgovine?", "Da. Delamo za lokalna podjetja, spletne trgovine, B2B podjetja, izvoznike in velike mednarodne strani. Pristop prilagodimo temu, kje so vaši kupci in kako kupujejo."),
    ],
}


def section(src, start_pat, end_pat):
    i = src.index(start_pat)
    j = src.index(end_pat, i) + len(end_pat)
    return src[i:j]


def build_landings():
    idx = (PUB / "index.html").read_text(encoding="utf-8")
    proof = section(idx, '<section class="band band--blue" aria-label="Na kratko">', "</section>")
    review = section(idx, '<section id="review"', "</section>")
    arts = re.findall(r'<article class="case[^"]*".*?</article>', idx, flags=re.S)[:2]
    cases = ('<section id="rezultati" aria-labelledby="rez-title">\n  <div class="wrap results">\n'
             '    <div class="results-head reveal">\n      <p class="eyebrow">Primeri rezultatov</p>\n'
             '      <h2 id="rez-title" class="h2"><span class="ln">Primeri rezultatov</span> <span class="yl">in dokazila.</span></h2>\n      <p class="sp-sub">Dva primera pri mednarodnih strankah. Imena strank ostajajo zaupna.</p>\n    </div>\n'
             + "\n".join(arts) + '\n    <p class="lp-more reveal"><a href="/#results">Več rezultatov na naslovnici &rarr;</a></p>\n  </div>\n</section>')
    built = []
    for f in sorted(LANDINGS.glob("*.html")) if LANDINGS.exists() else []:
        slug = f.stem
        lines = f.read_text(encoding="utf-8").split("\n")
        meta, i = {}, 0
        while i < len(lines) and re.match(r"^[A-Z0-9]+: ", lines[i]):
            k, v = lines[i].split(": ", 1); meta[k] = v.strip(); i += 1
        body = "\n".join(lines[i:])
        faqs = FAQS.get(slug, [])
        faq_html = "\n".join(f'      <details class="lp-q"><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in faqs)
        body = body.replace("{{PROOF}}", proof).replace("{{CASES}}", cases).replace("{{REVIEW}}", review).replace("{{FAQ}}", faq_html)
        url = f"{SITE}/{slug}/"
        graph = [
            {"@type": "Service", "@id": url + "#service", "name": meta["H1"], "serviceType": "SEO optimizacija spletnih strani",
             "description": meta["DESC"], "url": url, "areaServed": "SI",
             "provider": {"@type": "ProfessionalService", "@id": SITE + "/#org", "name": "SEOPRO.si",
                          "legalName": "SEOPRO, spletna optimizacija, Igor Bajsić s.p.", "url": SITE + "/", "email": "igor@seopro.si",
                          "address": {"@type": "PostalAddress", "streetAddress": "Pod kostanji 32", "postalCode": "1000", "addressLocality": "Ljubljana", "addressCountry": "SI"}}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "SEOPRO", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": meta["H1"], "item": url}]},
        ]
        if faqs:
            graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>\n"
        page = head(meta["TITLE"], meta["DESC"], url, extra=ld, robots=meta.get("ROBOTS", "index, follow, max-image-preview:large")) + f"\n<body>\n{header()}\n\n<main id=\"main\" class=\"lp\">\n{body}\n</main>\n\n{footer()}\n</body>\n</html>\n"
        write(PUB / slug / "index.html", page)
        if "noindex" not in meta.get("ROBOTS", ""):
            built.append(slug)
    return built
