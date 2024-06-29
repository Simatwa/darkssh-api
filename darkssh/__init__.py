from importlib import metadata
from darkssh.main import SSH

try:
    __version__ = metadata.version("darkssh")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__author__ = "Smartwa"
__repo__ = "https://github.com/Simatwa/darkssh-api"
