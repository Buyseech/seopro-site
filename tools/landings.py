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
        ("Kaj je SEO v eni povedi?", "SEO je urejanje spletne strani in njenega ugleda na spletu, da jo Google pokaže čim višje ljudem, ki iščejo to, kar prodajate."),
        ("Kaj vključuje optimizacija spletne strani?", "Tehnični SEO (hitrost, indeksiranje, struktura), on-page optimizacijo (ključne besede, naslovi, vsebina, notranje povezave), off-page optimizacijo (kakovostne povratne povezave) in izboljšave konverzij, da obisk postane povpraševanje ali nakup."),
        ("Koliko časa traja, da SEO začne delovati?", "Prve premike pogosto vidimo v nekaj tednih, posebej po tehničnih popravkih. Stabilna rast pri konkurenčnih iskanjih običajno pride v 3 do 6 mesecih, odvisno od konkurence in stanja strani."),
        ("Ali je SEO boljši od Google oglasov?", "Oglasi delajo le, dokler plačujete. SEO gradi pozicije, ki prinašajo obisk in povpraševanja tudi dolgo po opravljenem delu, zato je na dolgi rok za večino podjetij cenejši vir strank."),
        ("Koliko stane SEO optimizacija?", "Odvisno od konkurence, velikosti strani in njenega stanja. Po brezplačni analizi dobite jasen predlog: kaj je treba narediti, koliko stane in kakšen doprinos lahko pričakujete."),
        ("Ali lahko SEO naredim sam?", "Osnove lahko uredite sami: jasne naslove strani, dobro vsebino za vsako storitev in hitro stran. Pri konkurenčnih iskanjih pa odločajo tehnične podrobnosti, strategija ključnih besed in povezave, kjer se izkušnje hitro poznajo."),
        ("Ali delate tudi za lokalna podjetja in spletne trgovine?", "Da. Delamo za lokalna podjetja, spletne trgovine, B2B podjetja in velike mednarodne strani. Pristop prilagodimo temu, kje so vaši kupci in kako kupujejo."),
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
             '      <h2 id="rez-title" class="h2"><span class="ln">Prave stranke.</span> <span class="yl">Prave številke.</span></h2>\n    </div>\n'
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
        page = head(meta["TITLE"], meta["DESC"], url, extra=ld) + f"\n<body>\n{header()}\n\n<main id=\"main\" class=\"lp\">\n{body}\n</main>\n\n{footer()}\n</body>\n</html>\n"
        write(PUB / slug / "index.html", page)
        built.append(slug)
    return built
