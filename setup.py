from setuptools import setup, find_packages
from pywebwinui3 import __version__

setup(
    name='PyWebWinUI3',
    description='Create modern WinUI3-style desktop UIs in Python effortlessly using pywebview.',
    url='https://github.com/Haruna5718/PyWebWinUI3',
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pywebview','pywin32'],
    keywords=['PyWebWinUI3', 'pywebwinui3', 'Haruna5718', 'pywebview', 'winui3', 'pypi'],
    version=__version__,
    license='Apache 2.0',
    author='Haruna5718',
    author_email='me@haruna5718.dev',
)