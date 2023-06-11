from distutils.core import setup

# read the contents of README.md
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="eqalert",
    version="3.5.4",
    author="M Geitz",
    author_email="git@geitz.xyz",
    install_requires=[
        "playsound>=1.3.0",
        "gtts>=2.3.1",
    ],
    python_requires=">=3.9.2",
    packages=["eqa", "eqa.lib", "eqa.sound"],
    include_package_data=True,
    package_data={"eqa.sound": ["*.wav"]},
    license="GPL2",
    entry_points={
        "console_scripts": [
            "eqalert = eqa.eqalert:main",
        ],
    },
    description="Configurable and Context Driven Project 1999 Log Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mgeitz/eqalert",
)
