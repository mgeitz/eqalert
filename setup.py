from distutils.core import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='eqalert',
    version='1.2.0',
    author='Michael Geitz',
    author_email='git@geitz.xyz',
    install_requires=[
        'pyinotify',
        'playsound',
        'gtts',
    ],
    python_requires='>3',
    packages=['eqa', 'eqa.lib'],
    license='LICENSE.txt',
    entry_points={
        "console_scripts": [
            "eqalert = eqa.eqalert:main",
        ],
    },
    description='Parse and react to eqemu logs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mgeitz/eqalert'
)
