from setuptools import setup, find_packages

INSTALL_REQUIRE = ["requests==2.31.0", "bs4==0.0.1", "pydantic==2.7.3"]

cli_reqs = [
    "click==8.1.3",
]

EXTRA_REQUIRE = {
    "cli": cli_reqs,
    "all": INSTALL_REQUIRE + cli_reqs,
}

setup(
    name="darkssh-api",
    # packages="darkssh",
    packages=find_packages(""),
    version="0.0.1",
    license="MIT",
    author="Smartwa",
    maintainer="Smartwa",
    author_email="simatwacaleb@proton.me",
    description="Unofficial Python SDK/API fo Darkssh",
    url="https://github.com/Simatwa/darkssh-api",
    project_urls={
        "Bug Report": "https://github.com/Simatwa/darkssh-api/issues/new",
        "Homepage": "https://github.com/Simatwa/darkssh-api",
        "Source Code": "https://github.com/Simatwa/darkssh-api",
        "Issue Tracker": "https://github.com/Simatwa/darkssh-api/issues",
        "Download": "https://github.com/Simatwa/darkssh-api/releases",
        "Documentation": "https://github.com/Simatwa/darkssh-api/blob/main/docs",
    },
    entry_points={
        "console_scripts": ["darkssh = darkssh.console:main"],
    },
    install_requires=INSTALL_REQUIRE,
    extras_require=EXTRA_REQUIRE,
    python_requires=">=3.10",
    keywords=[
        "darkssh",
        "ssh",
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
