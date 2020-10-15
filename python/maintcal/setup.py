try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='maintcal',
    version="0.6.3",
    description="""
    Application to allow redacted CORE CRM users to schedule 
    blocks of time in work groups.
    """,
    author='Nathen Hinson',
    author_email='nathen.hinson@redacted.com',
    #url='',
    install_requires=["Pylons>=0.9.6.1", "core_authkit>=0.1", "SQLAlchemy>=0.5.0"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'maintcal': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'maintcal': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = maintcal.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [distutils.setup_keywords]
    paster_plugins = setuptools.dist:assert_string_list

    [egg_info.writers]
    paster_plugins.txt = setuptools.command.egg_info:write_arg
    """,
    paster_plugins = ["Pylons", "WebHelpers", "PasteScript"]
)
