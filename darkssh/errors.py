class CaptchaUrlNotFoundError(Exception):
    """Raised when url to captcha image can't be extracted"""

    pass


class CsrfEXtractionError(Exception):
    """Raised when csrf token extraction failed"""

    pass


class ServerCreationError(Exception):
    """Raised upon failure to generate server credentials"""
