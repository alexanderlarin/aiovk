import codecs
import os
import re

from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = list(map(lambda x: x.strip(), f.readlines()))

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'aiovk', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

setup(
    name='aiovk',
    version=version,

    author='Fahreev Eldar',
    author_email='fahreeve@yandex.ru',

    url='https://github.com/Fahreeve/aiovk',
    description='vk.com API python wrapper for asyncio',
    long_description=readme,

    packages=find_packages(),
    install_requires=requirements,

    license='MIT License',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='vk.com api vk wrappper asyncio',
    test_suite="tests",
    python_requires='>=3.6'
)
