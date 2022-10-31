"""
A setuptools based setup module.
"""
import os
import re
import codecs
from setuptools import setup


here = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def long_description():
    with open(os.path.join(here, 'README.rst')) as f:
        long_description = f.read()
    return long_description


def find_version(file_path, file_name):
    """
    Get the version from __init__.py file

    Parameters
    ----------
    file_path: path of this file
    file_name: which python file to search for the version

    Returns
    -------
    version
    """
    with codecs.open(os.path.join(file_path, file_name), 'r') as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open('requirements.txt') as fp:
    install_requires = [x.split("/")[-1] for x in fp.read().splitlines()[1:]]

if __name__ == "__main__":
    setup(
        setup_requires=["wheel"],
        name='Geocoding',
        version=find_version(here, "__init__.py"),
        description='geocoding is an address search engine for France',
        long_description=long_description(),
        url='https://github.com/adimajo/geocoding',
        authors=['Paulo Emilio de Vilhena', 'Adrien Ehrhardt'],
        author_emails=['pevilhena2@gmail.com', 'adrien.ehrhardt@credit-agricole-sa.fr'],
        license='Apache Software License',
        classifiers=[
            "Development Status :: 4 - Beta",
            'Intended Audience :: Financial and Insurance Industry',
            'Topic :: Utilities',
            'License :: OSI Approved :: Apache Software License',
            "Programming Language :: Python :: 3 :: Only",
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        keywords='Geocoder.py France',
        packages=['geocoding'],
        install_requires=install_requires,
        test_suite="pytest-runner",
        tests_require=["pytest", "coverage"],
        entry_points={
            'console_scripts': [
                'geocoding = geocoding.__main__:main'
            ]
        },
    )
