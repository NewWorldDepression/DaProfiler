import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def skype2email(name: str, pren: str, alt_sources: list | None = None):
    """
    Replaces skypli lookup by trying several public Skype-directory-like pages.
    - name, pren : search terms
    - alt_sources : optional list of URL templates containing {q} where the search term will be injected.
      Example: "https://skypeusernames.com/?s={q}"
    Returns a list of verified emails (may be empty).
    """
    if not name and not pren:
        return []

    # prepare search term
    search_term = f"{name} {pren}".strip()
    q = quote_plus(search_term)

    # default candidate sources (templates must contain {q})
    candidates = [
        # community directories (may change over time)
        "https://www.skypeusernames.com/?s={q}",
        "https://speed-friends.com/?s={q}",
        "https://add-me-contacts.com/find-online-skype-contacts.php?search={q}",
        # generic site search (Bing / Google scrapers removed intentionally)
        # If you have a replacement API, add it to alt_sources
    ]
    if alt_sources:
        # allow caller to provide their own preferred sources (higher priority)
        candidates = list(alt_sources) + candidates

    # helper: extract potential skype handles from HTML text
    def extract_usernames_from_text(text: str):
        found = set()
        if not text:
            return found
        # 1) look for tokens starting with live:, live:abcd or live:.abcd
        for m in re.finditer(r"\blive:[A-Za-z0-9_\-\.]{2,}\b", text, flags=re.I):
            found.add(m.group(0).lower().replace("live:", ""))
        # 2) look for href=skype:username links (skype URI)
        for m in re.finditer(r'href=["\']skype:([A-Za-z0-9_\-\.]{2,})', text, flags=re.I):
            found.add(m.group(1).lower())
        # 3) generic username-like tokens (avoid catching emails)
        # pattern: start with letter/number, allow letters/numbers/._- and length 3..50
        for m in re.finditer(r"\b([A-Za-z0-9][A-Za-z0-9_\-\.]{2,49})\b", text):
            token = m.group(1)
            # filter out tokens that look like domains/emails or pure numbers
            if "@" in token or token.isdigit():
                continue
            # avoid common words by simple blacklist (can be extended)
            if token.lower() in {"search","username","skype","contact","profile","online","find","www","http","https","com","net"}:
                continue
            # heuristic: token with at least one letter and not too short
            if re.search(r"[A-Za-z]", token) and len(token) >= 3:
                found.add(token.lower())
        return found

    profile_names = set()

    # iterate candidates and try to parse
    for tpl in candidates:
        try:
            url = tpl.format(q=q)
        except Exception:
            continue
        resp = fetch_url(url, timeout=8, allow_insecure_debug=False)
        if resp is None:
            continue
        try:
            soup = BeautifulSoup(resp.content, "html.parser")
        except Exception:
            # fallback to raw text
            page_text = resp.text
        else:
            # gather text + attributes to search for usernames
            parts = []
            parts.append(soup.get_text(separator=" "))
            # include hrefs and some attributes where usernames often appear
            for a in soup.find_all("a"):
                if a.string:
                    parts.append(str(a.string))
                if a.has_attr("href"):
                    parts.append(a["href"])
            page_text = " ".join(parts)

        # extract candidates
        found_names = extract_usernames_from_text(page_text)
        # Basic cleanup: remove obviously short or garbage tokens
        for fn in found_names:
            # ignore tokens that are clearly not usernames (contains domain)
            if fn.count(".") > 2 or "/" in fn or "\\" in fn:
                continue
            if len(fn) < 3:
                continue
            profile_names.add(fn)

        # small early exit if we already have a bunch
        if len(profile_names) >= 30:
            break

    if not profile_names:
        # nothing found across sources
        return []

    # Build candidate emails from domains file
    domains = _read_mail_domains()
    if not domains:
        # fallback common domains if mail_domain.txt missing
        domains = ["@gmail.com", "@hotmail.com", "@outlook.com", "@hotmail.fr", "@outlook.fr"]

    valid_emails = []
    for pname in profile_names:
        for d in domains:
            candidate = f"{pname}{d}".strip()
            try:
                ok = mail_check.verify(mail=candidate)
            except Exception:
                ok = None
            if ok is not None:
                valid_emails.append(candidate)

    # dedupe, return
    return list(dict.fromkeys(valid_emails))
