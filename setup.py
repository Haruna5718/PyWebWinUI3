from setuptools import setup, find_packages

setup(
    name='PyWebWinUI3',
    version='1.0.0-beta.1',
    description='Create modern WinUI3-style desktop UIs in Python effortlessly using pywebview.',
    author='Haruna5718',
    author_email='devharuna5718@gmail.com',
    url='https://github.com/Haruna5718/PyWebWinUI3',
    install_requires=['pywebview','pywin32'],
    packages=find_packages(exclude=[]),
    keywords=['PyWebWinUI3', 'Haruna5718', 'pywebview', 'winui3', 'pypi'],
    python_requires='>=3.8',
    include_package_data=True,
    package_data={},
    zip_safe=False,
    classifiers=[],
)