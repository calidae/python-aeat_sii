
from setuptools import setup
from setuptools import find_packages

install_requires = [
    'zeep<2',
]

tests_require = [
    'pytest>3',
]

setup(
    name='pyAEATsii',
    version='0.1',
    description='A python wrapper for the AEAT SII webservices',
    author="Calidae S.L.",
    author_email="dev@calidae.com",
    url='http://www.calidae.com/',
    download_url='https://github.com/calidae/python-aeat_sii',
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    entry_points={},
    package_dir={'': 'src'},
    packages=find_packages('src'),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
