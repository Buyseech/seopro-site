# SEOPRO.si

Slovenian SEO agency site. Same setup as `Buyseech/buyseech-site` and `Buyseech/seopack-site-`: static files, no build step on Cloudflare. Cloudflare serves the files in `public/` as they are.

## Where things are

- `public/index.html`: the home page, a Slovenian translation of buyseech.com with the same sections, images and facts (hero, numbers, who we help, toolbox, "Šteje rezultat" band, 3 case studies, team, speaking, 2018 challenge, Unscripted SEO, form)
- `public/styles.css`: all styling. Copied from buyseech.com/seopack.net so the sites look the same; the hero line sizes (`.fit-1/2/3`) are re-measured for the Slovenian text at the bottom of the file. SEOpack parts are prefixed `sp-`, SEOPRO-only parts (blog, articles) `sr-` at the bottom. Accent colour is `--accent`.
- `public/site.js`: scroll-in animation, form handling (Slovenian messages), phone menu
- `public/<slug>/index.html`: the 10 old blog posts, kept at **the same addresses** the old WordPress site used, so their Google rankings and backlinks carry over
- `public/blog/`, `public/trendi/`, `public/zasebnost/` (privacy & company info, BUYSEECH d.o.o.)
- `public/_redirects`: 301s from old WordPress addresses (`/kontakt/`, `/pogosta-vprasanja/`, feeds, author pages…) to the new ones
- `public/assets/fonts/`: self-hosted fonts, with latin-ext files for č, š, ž
- `wrangler.jsonc`: tells Cloudflare to publish the `public/` folder

## Blog posts

Posts live in `content/posts/<slug>.html` (a few header lines, then the article HTML). After adding or editing one, run:

    python3 tools/build.py

It rebuilds the post pages, the blog list, the three newest posts on the home page, the sitemap, and the shared header/footer. Commit the result; Cloudflare still needs no build step.

## Cloudflare settings

- Build command: none
- Deploy: Workers & Pages → Create → Import a repository → this repo. Staging URL: `seopro-site.<account>.workers.dev`

## Form

Sends to Web3Forms (same account as buyseech.com and seopack.net), which emails each enquiry to igor@buyseech.com with the subject "Novo povpraševanje za brezplačno analizo s seopro.si".

## Before pointing seopro.si at it

- Add `seopro.si` and `www.seopro.si` as custom domains on the Worker, and redirect `www` to `seopro.si` (the old site used `www.seopro.si`)
- **Google Analytics:** create a GA4 property for seopro.si and paste its snippet where the comment says
- Submit `https://seopro.si/sitemap.xml` in Search Console after the switch
- Old blog images were not carried over (they were 2017 screenshots); the text was adjusted where it referred to them
