from setuptools import setup

# Dynamically calculate the version based on django.VERSION.
version = __import__('libscampi').get_version()

setup(
    version=version,
    setup_requires=['pbr'],
    pbr=True,
)
