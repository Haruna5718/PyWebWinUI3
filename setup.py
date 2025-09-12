from setuptools import setup, find_packages

def get_version():
    with open("pywebwinui3/__init__.py", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")

setup(
    name='PyWebWinUI3',
    description='Create modern WinUI3-style desktop UIs in Python effortlessly using pywebview.',
    url='https://github.com/Haruna5718/PyWebWinUI3',
    long_description=open('README.md', 'r', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pywebview','pywin32'],
    keywords=['PyWebWinUI3', 'Haruna5718', 'pywebview', 'winui3', 'pypi'],
    version=get_version(),
    license='Apache 2.0',
    author='Haruna5718',
    author_email='devharuna5718@gmail.com',
)