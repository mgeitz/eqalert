from distutils.core import setup

setup(
    name='eqalert',
    version='1.1.0',
    author='Michael Geitz',
    author_email='git@geitz.xyz',
    install_requires=['pyinotify'],
    python_requires='>3',
    packages=['eqa', 'eqa.lib'],
    license='LICENSE.txt',
    description='Parse and react to eqemu logs',
    url='https://github.com/mgeitz/eqalert',
)
