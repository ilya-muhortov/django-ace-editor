from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='ace_editor',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ace_editor": ["static/**/*"]
    },
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
)
