# modules/mail/mail_gen.py
import os
import socket
import logging
from urllib.parse import urlparse, quote_plus

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

from modules.mail import mail_check

logger = logging.getLogger(__name__)
# configure a default basic logger if the application hasn't configured logging
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)


def host_resolves(hostname: str, timeout: float = 3.0) -> bool:
    """Return True if hostname resolves (DNS)."""
    if not hostname:
        return False
    try:
        socket.getaddrinfo(hostname, None)
        return True
    except socket.gaierror:
        return False
    except Exception as e:
        logger.debug("Unexpected error while resolving %s: %s", hostname, e)
        return False


def fetch_url(url: str, alt_url: str | None = None, timeout: int = 10, allow_insecure_debug: bool = False):
    """
    Robust GET:
    - checks DNS resolution of target host(s) before requesting,
    - handles RequestException cleanly,
    - optionally tries an alt_url,
    - returns requests.Response or None on failure.
    """
    def _do_get(u, verify=True):
        return requests.get(u, timeout=timeout, verify=verify)

    # ensure scheme
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    candidates = [url]
    if alt_url:
        candidates.append(alt_url)

    # Skip candidate if host doesn't resolve
    for candidate in candidates:
        parsed_c = urlparse(candidate)
        host = parsed_c.hostname
        if host and not host_resolves(host):
            logger.warning("Host does not resolve, skipping candidate: %s", host)
            continue
        try:
            logger.debug("Requesting %s", candidate)
            r = _do_get(candidate, verify=True)
            r.raise_for_status()
            return r
        except RequestException as e:
            logger.warning("Request failed for %s: %s", candidate, e)
            last_exc = e

    # optional insecure debug retry (DANGEROUS — only for local debugging)
    if allow_insecure_debug and candidates:
        try:
            logger.warning("Retrying %s with verify=False (DEBUG only)", candidates[-1])
            r = _do_get(candidates[-1], verify=False)
            r.raise_for_status()
            return r
        except Exception as e:
            logger.error("Insecure retry failed: %s", e)

    logger.error("All attempts to fetch URL failed.")
    return None


def _read_mail_domains():
    """
    Read modules/mail_domain.txt next to this file.
    Returns list of domain strings (with leading '@'), or empty list if file missing.
    """
    base = os.path.dirname(__file__)
    path = os.path.join(base, "mail_domain.txt")
    domains = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if "@" in line and "." in line:
                    domains.append(line if line.startswith("@") else ("@" + line))
    except FileNotFoundError:
        logger.warning("mail_domain.txt not found at %s", path)
    except Exception as e:
        logger.exception("Error reading mail_domain.txt: %s", e)
    return domains


def check(name: str, pren: str):
    """
    Guess common mailbox patterns and verify them via mail_check.verify.
    Returns a list of valid emails (may be empty).
    """
    logger.info("📪 MailBox guessing ...")
    name = (name or "").strip().lower()
    pren = (pren or "").strip().lower()

    results = [
        f"{name}.{pren}@gmail.com",
        f"{name}.{pren}@hotmail.com",
        f"{name}{pren}@hotmail.com",
        f"{name}{pren}@hotmail.fr",
        f"{name}{pren}@outlook.fr",
        f"{name}.{pren}@outlook.com",
        f"{name}{pren}@outlook.com",
        f"{pren}.{name}@gmail.com",
        f"{pren}.{name}@hotmail.com",
        f"{pren}{name}@hotmail.com",
        f"{pren}{name}@hotmail.fr",
        f"{pren}{name}@outlook.fr",
        f"{pren}.{name}@outlook.com",
        f"{pren}{name}@outlook.com",
    ]

    valid_mails = []
    for candidate in results:
        try:
            ok = mail_check.verify(mail=candidate)
            if ok is not None:
                valid_mails.append(candidate)
        except Exception as e:
            logger.debug("mail_check.verify raised for %s: %s", candidate, e)
    return valid_mails


def skype2email(name: str, pren: str):
    """
    Try to collect Skype usernames from skypli (or alternative) and build candidate emails
    using the domains from mail_domain.txt. Returns a list of verified emails or an empty list.
    If the remote service/domain is not resolvable, returns an empty list (does not raise).
    """
    if not name and not pren:
        return []

    name = (name or "").strip()
    pren = (pren or "").strip()
    # URL-encode the search term (space -> + or %20)
    search_term = quote_plus(f"{name} {pren}")
    url = f"https://www.skypli.com/search/{search_term}"
    # If you have a known alternative domain, put it here:
    alt_url = None  # e.g. "https://nouveau-domaine.example/search/..." 

    resp = fetch_url(url, alt_url=alt_url, timeout=8, allow_insecure_debug=False)
    if resp is None:
        logger.info("skype2email: remote host unreachable or returned error. Returning empty list.")
        return []

    try:
        soup = BeautifulSoup(resp.content, "html.parser")
    except Exception as e:
        logger.error("Failed to parse HTML: %s", e)
        return []

    # defensive find: there might be 0 matches
    profiles = soup.find_all("span", {"class": "search-results__block-info-username"}) or []
    # limit to first 20 to avoid excessive processing
    profiles = profiles[:20]

    profile_names = []
    for el in profiles:
        try:
            text = el.get_text(strip=True)
            if not text:
                continue
            # ignore live: entries
            if "live:." in text or text.startswith("live:."):
                continue
            # sanitize common suffixes
            cleaned = text.replace("live:", "").replace("_1", "").strip().lower()
            if cleaned:
                profile_names.append(cleaned)
        except Exception:
            continue

    # build candidate emails using domains file
    domains = _read_mail_domains()
    valid_emails = []
    for p in profile_names:
        for d in domains:
            candidate = f"{p}{d}".strip()
            try:
                ok = mail_check.verify(mail=candidate)
                if ok is not None:
                    valid_emails.append(candidate)
            except Exception as e:
                logger.debug("mail_check.verify raised for %s: %s", candidate, e)

    # deduplicate and return
    return list(dict.fromkeys(valid_emails))


def pinterest2email(name: str, pren: str):
    """
    Placeholder for Pinterest-based email discovery.
    Current implementation intentionally returns None (kept for backward compatibility).
    If you want to implement later, consider using search APIs and the same verification flow.
    """
    return None
