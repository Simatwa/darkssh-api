import os
import requests
import darkssh.utils as utils
import darkssh.errors as errors
from typing import Literal
from darkssh.models import SSHModel

headers = {
    "Accept" : "application/json",
    "Accept-Encoding" : "gzip, deflate",
    "Accept-Language" : "en-US,en;q=0.5",
    "Connection" : "keep-alive",
    "Referer" : "http://darkssh.com/server/SSH/413",
    "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
}

country_codes_map = {
    "Singapore" : 412,
    "United States" : 413,
    "Germany" : 414,
    "United Kingdom" : 415,
    "Netherlands" : 416,
    "Australia" : 417,
    "Canada" : 418,
    "Indonesia" : 0,
    "Japan" :474,
    "Sweden" : 475,
    "Italy" : 476,
}
class SSH:

    def __init__(self, country:Literal['Singapore', 'United States', 'Germany', 'United Kingdom', 'Netherlands', 'Australia', 'Canada', 'Indonesia', 'Japan', 'Sweden', 'Italy']="Singapore"):
        """Constructor

        Args:
            country : Server location. Defaults to "Singapore".
        """
        assert country in country_codes_map, f"Country '{country}' is not one of {tuple(country_codes_map.keys())}"
        self.url = url = f"http://darkssh.com/server/SSH/{country_codes_map[country]}"
        self.timeout = 10
        self.session = requests.Session()
        self.session.headers = headers
        self.html_content = self.fetch_html_contents()

    def fetch_html_contents(self) -> str:
        """Gets html contents"""
        resp = self.session.get(self.url, timeout=self.timeout)
        resp.raise_for_status()
        self.html_content = resp.text
        return self.html_content

    @property
    def captcha_url(self) -> str:
        """extract captcha url from html codes"""
        return utils.extract_captcha_url(self.html_content)

    def download_captcha_image(self, dir: str = os.getcwd()) -> str:
        """Download captcha image

        Args:
            dir (str, optional): Folder to save the image. Defaults to os.getcwd().

        Returns:
            str: path to the image
        """
        assert os.path.isdir(dir), f"Directory '{dir}' does not exist!"
        image_url = self.captcha_url
        save_to = os.path.join(
            dir, 
            image_url.split("?")[1] + ".png"
            )
        resp = self.session.get(image_url)
        resp.raise_for_status()
        with open(save_to, "wb") as fp:
            fp.write(resp.content)

        return save_to

    def generate(self, username: str, password: str, captcha: str) -> SSHModel:
        """Generate ssh server and return credentials

        Args:
            username (str): Server username.
            password (str): Server password.
            captcha (str): Captcha value.

        Raises:
            errors.ServerCreationError: Upon server creation failure.

        Returns:
            SSHModel: Server info
        """
        payload = {
            "username": username,
            "password": password,
            "captcha": captcha
        }
        self.session.headers.update(
            {
                "X-CSRF-TOKEN": utils.extract_csrf_token(
                    self.html_content,
                ),
                "X-XSRF-TOKEN": self.session.cookies["XSRF-TOKEN"],
            }
        )
        resp = self.session.post(self.url, data=payload, timeout=self.timeout)

        if resp.ok:
            return SSHModel(**resp.json())

        else:
            raise errors.ServerCreationError(
                f"Failed to create server - ({resp.status_code}, {resp.reason}) - {resp.text}"
            )
