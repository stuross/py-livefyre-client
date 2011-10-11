import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "livefyre.client",
    version = "0.1.1",
    author = "Nino Walker",
    author_email = "support@livefyre.com",
    description = ("Livefyre API python client."),
    license = "BSD",
    keywords = "documentation client",
    url = "http://github.com/Livefyre/py-livefyre-client",
    packages=['livefyre.client', 'livefyre'],
    install_requires = ['httplib2>=0.6.0', 'python-rest-client>=0.3'],
    setup_requires=['nose>=0.11'],
    test_suite = "nose.collector",
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: BSD License",
    ],

    )
