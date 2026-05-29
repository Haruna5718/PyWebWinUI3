from pathlib import Path
import re

from setuptools import setup, find_packages


ROOT = Path(__file__).parent.resolve()


def read_requirements():
	return [
		line.strip()
		for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
		if line.strip() and not line.lstrip().startswith("#")
	]


def collect_package_data():
	return [
		str(path.relative_to(ROOT / "pywebwinui3")).replace("\\", "/")
		for path in (ROOT / "pywebwinui3" / "web").rglob("*")
		if path.is_file()
	]


def read_version():
	match = re.search(
		r"^__version__\s*=\s*['\"]([^'\"]+)['\"]",
		(ROOT / "pywebwinui3" / "__init__.py").read_text(encoding="utf-8"),
		re.MULTILINE,
	)
	if match is None:
		raise RuntimeError("Failed to read package version from pywebwinui3/__init__.py")
	return match.group(1)

setup(
	name='PyWebWinUI3',
	description='Create modern WinUI3-style desktop UIs in Python using pywebview and a Svelte frontend.',
	url='https://github.com/Haruna5718/PyWebWinUI3',
	long_description=(ROOT / 'README.md').read_text(encoding="utf-8"),
	long_description_content_type='text/markdown',
	packages=find_packages(),
	package_data={'pywebwinui3': collect_package_data()},
	include_package_data=False,
	install_requires=read_requirements(),
	keywords=['PyWebWinUI3', 'pywebwinui3', 'Haruna5718', 'pywebview', 'svelte', 'winui3', 'pypi'],
	version=read_version(),
	license='Apache-2.0',
	author='Haruna5718',
	author_email='me@haruna5718.dev',
	python_requires='>=3.10',
	classifiers=[
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3.11',
		'Programming Language :: Python :: 3.12',
		'Programming Language :: Python :: 3.13',
		'Operating System :: Microsoft :: Windows',
	],
)
