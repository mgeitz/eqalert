from distutils.core import setup

setup(
    name="eqalert",
    version="3.0.0",
    author="Michael Geitz",
    author_email="git@geitz.xyz",
    install_requires=[
        "playsound",
        "gtts",
    ],
    python_requires=">3",
    packages=["eqa", "eqa.lib"],
    license="LICENSE.txt",
    entry_points={
        "console_scripts": [
            "eqalert = eqa.eqalert:main",
        ],
    },
    description="Parse and React to EQEmu Logs",
    url="https://github.com/mgeitz/eqalert",
)
