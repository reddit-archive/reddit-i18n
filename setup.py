#!/usr/bin/env python2.5
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='reddit_i18n',
    version="",
    #description='',
    #author='',
    #author_email='',
    #url='',
    install_requires=["Pylons>=0.9.6.1"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'reddit_i18n': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'reddit_i18n': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = reddit_i18n.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
