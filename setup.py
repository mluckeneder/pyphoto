try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="pyphoto",
    version="0.0.5",
    provides=["pyphoto"],
    author="Michael Luckeneder",
    author_email="michael@luckeneder.net",
    url="http://github.com/pyphoto",
    description='Backup iPhoto/Aperture libraries',
    install_requires=['flickrapi', 'colorama'],
    packages=['pyphoto'],
    scripts=['bin/backup_iphoto'],
    long_description="""pyPhoto - backup your iPhoto/Aperture library
"""
)
