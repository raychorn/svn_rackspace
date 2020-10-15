"""
This is where the maintcal tests live.

Individual tests will be invoked from a test runner.
They will not contain supporting code to be run standalone.

How to run the tests:

 cd maintcal/maintcal/tests
 nosetests

"""
import pkg_resources
import paste.fixture
import paste.script.appinstall
from paste.deploy import loadapp
import os
import sys

# We need to load up the test.ini file

conf_dir = None

class SetupTestEnvironment(object):
    def monkeypatch_paste(self):
        """
        Two patches are necessary to make paste directly use an .ini file
        that includes a filter-with

        """

        from paste.deploy import loadwsgi

        # These symbols are needed by the monekypatched method
        from paste.deploy.loadwsgi import APP, FILTER, FILTER_WITH, loadcontext, LoaderContext

        def monkeypatched_get_context(self, object_type, name=None, global_conf=None):
            if self.absolute_name(name):
                return loadcontext(object_type, name,
                                   relative_to=os.path.dirname(self.filename),
                                   global_conf=global_conf)
            section = self.find_config_section(
                object_type, name=name)
            if global_conf is None:
                global_conf = {}
            else:
                global_conf = global_conf.copy()
            defaults = self.parser.defaults()
            global_conf.update(defaults)
            local_conf = {}
            global_additions = {}
            get_from_globals = {}
            for option in self.parser.options(section):
                if option.startswith('set '):
                    name = option[4:].strip()
                    global_additions[name] = global_conf[name] = (
                        self.parser.get(section, option))
                elif option.startswith('get '):
                    name = option[4:].strip()
                    get_from_globals[name] = self.parser.get(section, option)
                else:
                    if option in defaults:
                        # @@: It's a global option (?), so skip it
                        continue
                    local_conf[option] = self.parser.get(section, option)
            for local_var, glob_var in get_from_globals.items():
                local_conf[local_var] = global_conf[glob_var]
            if object_type in (APP, FILTER) and 'filter-with' in local_conf:
                filter_with = local_conf.pop('filter-with')
            else:
                filter_with = None
            if 'require' in local_conf:
                for spec in local_conf['require'].split():
                    pkg_resources.require(spec)
                del local_conf['require']
            if section.startswith('filter-app:'):
                context = self._filter_app_context(
                    object_type, section, name=name,
                    global_conf=global_conf, local_conf=local_conf,
                    global_additions=global_additions)
            elif section.startswith('pipeline:'):
                context = self._pipeline_app_context(
                    object_type, section, name=name,
                    global_conf=global_conf, local_conf=local_conf,
                    global_additions=global_additions)
            elif 'use' in local_conf:
                context = self._context_from_use(
                    object_type, local_conf, global_conf, global_additions,
                    section)
            else:
                context = self._context_from_explicit(
                    object_type, local_conf, global_conf, global_additions,
                    section)
            if filter_with is not None:
                filter_with_context = LoaderContext(
                    obj=None,
                    object_type=FILTER_WITH,
                    protocol=None,
                    global_conf=global_conf, local_conf=local_conf,
                    # This is the monkeypatching
                    # This is the old line:
                    #loader=self)
                    # These are the two new lines
                    loader=self,
                    distribution=context.distribution)
                filter_with_context.filter_context = self.filter_context(
                    name=filter_with, global_conf=global_conf)
                filter_with_context.next_context = context
                return filter_with_context
            return context
     
        setattr(loadwsgi.ConfigLoader, 'get_context', monkeypatched_get_context)

        # Now we have to monkeypatch appconfig:

        from paste.script import appinstall

        # These symbols are needed by the monekypatched method
        from paste.deploy import appconfig

        def monkeypatched_command(self):
            config_spec = self.args[0]
            section = self.options.section_name
            if section is None:
                if '#' in config_spec:
                    config_spec, section = config_spec.split('#', 1)
                else:
                    section = 'main'
            if not ':' in section:
                plain_section = section
                section = 'app:'+section
            else:
                plain_section = section.split(':', 1)[0]
            if not config_spec.startswith('config:'):
                config_spec = 'config:' + config_spec
            if plain_section != 'main':
                config_spec += '#' + plain_section
            config_file = config_spec[len('config:'):].split('#', 1)[0]
            config_file = os.path.join(os.getcwd(), config_file)
            self.logging_file_config(config_file)
            conf = appconfig(config_spec, relative_to=os.getcwd())
            ep_name = conf.context.entry_point_name
            if ep_name is None:
                ep_name = 'main'
            ep_group = conf.context.protocol
            dist = conf.context.distribution
            if dist is None:
                raise BadCommand(
                    "The section %r is not the application (probably a filter).  You should add #section_name, where section_name is the section that configures your application" % plain_section)
            installer = self.get_installer(dist, ep_group, ep_name)
            installer.setup_config(
                self, config_file, section, self.sysconfig_install_vars(installer))
            self.call_sysconfig_functions(
                'post_setup_hook', installer, config_file)

        setattr(appinstall.SetupCommand, 'command', monkeypatched_command)

    def setup_for_paste(self, options):
        """
        This requires Paste and PasteScript,
        adding the base pylons dir to the python path
        and executing the test.ini file.
        """

        self.conf_dir = self._get_pylons_base_dir()

        sys.path.insert(0, self.conf_dir)
        pkg_resources.working_set.add_entry(self.conf_dir)
        pkg_resources.require('Paste')
        pkg_resources.require('PasteScript')

        if options.browser_tests:
            self.monkeypatch_paste()
            test_file = os.path.join(self.conf_dir, 'browsertest.ini')
        else:
            test_file = os.path.join(self.conf_dir, 'test.ini')

        cmd = paste.script.appinstall.SetupCommand('setup-app')
        cmd.run([test_file])

        return self.conf_dir

    def _get_pylons_base_dir(self):
        # ~/maintcal/maintcal/tests/lib
        here_dir = os.path.dirname(os.path.abspath(__file__))

        # pop 2 more directories... sigh...
        conf_dir = os.path.dirname(os.path.dirname(here_dir))

        # conf_dir should now be ~/maintcal/
        return conf_dir

setupTestEnvironment = SetupTestEnvironment()
