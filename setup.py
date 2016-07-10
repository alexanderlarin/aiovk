from setuptools import setup, find_packages

setup(
    name='aiovk',
    version=__import__('aiovk').__version__,

    author='Fahreev Eldar',
    author_email='fahreeve@yandex.ru',

    url='https://github.com/Fahreeve/aiovk',
    description='vk.com API python wrapper for asyncio',

    packages=find_packages(),
    install_requires='aiohttp>=0.21',

    license='MIT License',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='vk.com api vk wrappper asyncio',
)
