import setuptools
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(name="ruqqus-api",
    version="0.3.4",
    description="Unofficial Ruqqus API Wrapper",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/AgeOfMarcus/ruqqus-api",
    author="AgeOfMarcus",
    author_email="marcus@marcusweinberger.com",
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=['atoma', 'requests'],
)