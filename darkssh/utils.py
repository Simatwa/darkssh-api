from bs4 import BeautifulSoup as bts
from darkssh.errors import CaptchaUrlNotFoundError, CsrfEXtractionError
import re


def extract_captcha_url(html: str) -> str:
    """Extract link to captcha image

    Args:
        html (str): Html content for account creation

    Returns:
        str: URL to captcha image.
    """
    soup = bts(html, "html.parser")
    results: list = soup.find_all(attrs={"alt": "captcha", "x-ref": "imgCaptcha"})
    if not results:
        raise CaptchaUrlNotFoundError("No captcha url found in the html content.")
    else:
        return results[0].get("src")


def extract_csrf_token(html: str) -> str:
    """Extract csrf token

    Args:
        html (str): Html content for account creation

    Returns:
        str: csrf token
    """
    s = re.findall(r".*createAccount\(.*\)\"", html)
    if s:
        s1 = re.search(r"\w{40}", s[0])
        if s1:
            return s1.group()
    raise CsrfEXtractionError("Failed to extract CSRF token from the html content.")
