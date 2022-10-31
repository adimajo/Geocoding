from setuptools import setup

with open('README.rst') as reader:
    readme = reader.read()

setup(
    name='Geocoding',
    version=version,
    description='geocoding is an address search engine for France',
    long_description=readme,
    url='https://github.com/adimajo/geocoding',
    authors=['Paulo Emilio de Vilhena', '', 'Adrien Ehrhardt'],
    author_emails=['pevilhena2@gmail.com', '', 'adrien.ehrhardt@credit-agricole-sa.fr'],
    license='Apache Software License',
    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='Geocoder.py France',
    packages=['geocoding'],
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'geocoding = geocoding.__main__:main'
        ]
    },
)
