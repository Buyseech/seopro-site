#!/usr/bin/env python3
"""Resubmits the sitemap to Google Search Console after a publish.
Needs the GitHub secret GSC_SERVICE_ACCOUNT_JSON (a Google service account key whose email
is an Owner of the https://www.seopro.si/ property). Without it, the step is skipped."""
import json, os, sys, urllib.parse
key = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
if not key:
    print("No GSC_SERVICE_ACCOUNT_JSON secret, skipping the sitemap submit."); sys.exit(0)
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
creds = service_account.Credentials.from_service_account_info(json.loads(key), scopes=["https://www.googleapis.com/auth/webmasters"])
s = AuthorizedSession(creds)
site = urllib.parse.quote("https://www.seopro.si/", safe="")
feed = urllib.parse.quote("https://www.seopro.si/sitemap.xml", safe="")
r = s.put(f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}")
print("Search Console sitemap submit:", r.status_code, r.text[:300])
r.raise_for_status()
