"""
This runs the tests

"""
import os
import sys
import imp
import re
import unittest
import StringIO 
import inspect

class TestRunner(object):

    currentTestRunner = None

    def __init__(self, options, root_dir):
        self.options = options
        self.root_dir = root_dir
        self.results = None
        self.matchTestName = re.compile('test',re.I)

        # a text stream to capture the results of running the test
        self.result_stream = None

        self.run_functional_tests = True 
        self.run_unit_tests = True 

        self.run_browser_tests = False 

        if self.options.browser_tests:
            self.run_browser_tests = True 

            # For now, turn off unit and functional tests when running browser tests

            self.run_functional_tests = False 
            self.run_unit_tests = False 



        self.disabledTestWarnings = []


    def run(self):
        # Register this instance as the current test runner
        self.__class__.currentTestRunner = self
        self._glob_tests()
        self._run_tests()


    def _glob_tests(self):
        """Import the test files that we want to run."""
        self.test_suite = unittest.TestSuite()

        if self.run_browser_tests:
            func_test_root_dir = self.root_dir + "/maintcal/tests/browser/schedule_view"
            test_files = self._glob_test_files(func_test_root_dir)
            self._import_test_modules(test_files, func_test_root_dir)

        if self.run_functional_tests:
            func_test_root_dir = self.root_dir + "/maintcal/tests/functional"
            test_files = self._glob_test_files(func_test_root_dir)
            self._import_test_modules(test_files, func_test_root_dir)

        if self.run_unit_tests:
            unit_test_root_dir = self.root_dir + "/maintcal/tests/unit"
            test_files = self._glob_test_files(unit_test_root_dir)
            self._import_test_modules(test_files, unit_test_root_dir)

            unit_test_root_dir = self.root_dir + "/maintcal/tests/unit/date"
            test_files = self._glob_test_files(unit_test_root_dir)
            self._import_test_modules(test_files, unit_test_root_dir)

            unit_test_root_dir = self.root_dir + "/maintcal/tests/unit/model"
            test_files = self._glob_test_files(unit_test_root_dir)
            self._import_test_modules(test_files, unit_test_root_dir)

            unit_test_root_dir = self.root_dir + "/maintcal/tests/unit/times_available"
            test_files = self._glob_test_files(unit_test_root_dir)
            self._import_test_modules(test_files, unit_test_root_dir)

    def strip_unwanted_files(self,file):
        return (self.matchTestName.match(file) and file.endswith('.py'))

    def _glob_test_files(self, test_dir):
        """Get a list of names of the test files to run."""
        all_test_files = [test for test in os.listdir(test_dir) if self.strip_unwanted_files(test)] 
        if self.options.test_file:
            # fully qualify the test file name
            full_test_file = 'test_' + self.options.test_file + '.py'
            if full_test_file in all_test_files:
                return [full_test_file]
            return []            
        return all_test_files

    def _import_test_modules(self, test_files, test_dir):
        """Import test modules and add them to the test suite."""
        for test_file in test_files:
            try:
                file_name = test_file[:-3]
                # do this evil fucking thing. It imports a module from a file name and a path. The single
                # test_dir attribute in the list is required by find_module ... weird.
                #print "file_name: %s  test_dir: %s" % (file_name, test_dir)
                module = imp.load_module(file_name, *imp.find_module(file_name, [test_dir]))                
                if self.options.test_method:
                    # derive the test class's name
                    classes = [klass for klass in dir(module) if inspect.isclass(getattr(module, klass))] 
                    class_name = ''
                    for klass in classes:
                        if klass.startswith('Test'):
                            class_name = klass
                            break 
                    # Note: We assume that there is only one test class per file
                    #full_test_name = file_name + '.' + class_name + '.test_' + self.options.test_method
                    full_test_name =  class_name + '.test_' + self.options.test_method
                    test_suite = unittest.defaultTestLoader.loadTestsFromName(full_test_name, module)
                    #print repr(test_suite)
                    if test_suite:
                        self.test_suite.addTests([test_suite])
                else:
                    self.test_suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
            except ImportError, e:
                raise "Can't Import file: %s  Reason: %s" % (test_file, str(e))             

    def _run_tests(self):
        self.test_suite_setup()

        if self.options.quiet:
            self.result_stream = StringIO.StringIO()
            self.test_runner = unittest.TextTestRunner(stream=self.result_stream)
        else:
            self.test_runner = unittest.TextTestRunner()
        self.results = self.test_runner.run(self.test_suite)

        self.test_suite_teardown()

    def test_suite_setup(self):
        """
        This is run once before all tests are run.
        """
        if self.options.refresh_schema:
            self.setup_non_temp_tables()

    def test_suite_teardown(self):
        """
        This is run once after all tests are run.
        """
        pass

    def _create_indexes(self, db_sess):
        """
        Create all indexes for all tables.
        """
        all_indexes = """
            CREATE INDEX change_log_date ON maintcal_test.change_log USING btree (date);

            CREATE INDEX change_log_row_id ON maintcal_test.change_log USING btree (row_id);

            CREATE INDEX change_log_table_id ON maintcal_test.change_log USING btree (table_id);

            CREATE INDEX scheduled_maintenance_account_id ON maintcal_test.scheduled_maintenance USING btree (account_id);

            CREATE INDEX scheduled_maintenance_contact_id ON maintcal_test.scheduled_maintenance USING btree (contact_id);

            CREATE INDEX scheduled_maintenance_creation_date ON maintcal_test.scheduled_maintenance USING btree (creation_date);

            CREATE INDEX scheduled_maintenance_master_ticket ON maintcal_test.scheduled_maintenance USING btree (master_ticket);

            CREATE INDEX scheduled_maintenance_modification_date ON maintcal_test.scheduled_maintenance USING btree (modification_date);

            CREATE INDEX scheduled_maintenance_service_type_id ON maintcal_test.scheduled_maintenance USING btree (service_type_id);

            CREATE INDEX scheduled_maintenance_state_id ON maintcal_test.scheduled_maintenance USING btree (state_id);

            CREATE INDEX scheduled_service_calendar_id ON maintcal_test.scheduled_service USING btree (calendar_id);

            CREATE INDEX scheduled_service_end_time ON maintcal_test.scheduled_service USING btree (end_time);

            CREATE INDEX scheduled_service_scheduled_maintenance_id ON maintcal_test.scheduled_service USING btree (scheduled_maintenance_id);

            CREATE INDEX scheduled_service_scheduled_state_id ON maintcal_test.scheduled_service USING btree (state_id);

            CREATE INDEX scheduled_service_start_time ON maintcal_test.scheduled_service USING btree (start_time);

            CREATE INDEX scheduled_service_ticket_number ON maintcal_test.scheduled_service USING btree (ticket_number);

            CREATE INDEX xref_scheduled_service_server_list_computer_number ON maintcal_test.xref_scheduled_service_server_list USING btree (computer_number);

            CREATE INDEX xref_scheduled_service_server_list_scheduled_service_id ON maintcal_test.xref_scheduled_service_server_list USING btree (scheduled_service_id);
        """
        db_sess.execute(all_indexes)
        db_sess.commit()

    def setup_non_temp_tables(self):
        """
        Create the non-temporary maintcal tables.
        """
        from maintcal.model import metadata, engine
        from maintcal.model import db_sess

        print "dropping schema"
        db_sess.execute('DROP SCHEMA IF EXISTS maintcal_test CASCADE');
        print "creating schema"
        db_sess.execute('CREATE SCHEMA maintcal_test');
        db_sess.commit()

        print "creating trigger functions"
        print "NOTE: make sure to run 'CREATE LANGUAGE plpgsql' as db user postgres if the mcal_test database is recreated."
        db_sess.execute('CREATE OR REPLACE FUNCTION creation_date() RETURNS "trigger" as $$ DECLARE BEGIN NEW.creation_date := now(); RETURN NEW; END; $$ language plpgsql')
        db_sess.execute('CREATE OR REPLACE FUNCTION modification_date() RETURNS "trigger" as $$ DECLARE BEGIN NEW.modification_date := now(); RETURN NEW; END; $$ language plpgsql')

        print "creating tables"
        metadata.create_all(bind=engine)

        print "Attaching triggers to creation_date and modification_date columns"

        db_sess.execute('CREATE TRIGGER available_defaults_creation_date BEFORE INSERT ON maintcal_test.available_defaults FOR EACH ROW EXECUTE PROCEDURE creation_date();')
        db_sess.execute('CREATE TRIGGER available_defaults_modification_date BEFORE INSERT OR UPDATE ON maintcal_test.available_defaults FOR EACH ROW EXECUTE PROCEDURE modification_date();')

        db_sess.execute('CREATE TRIGGER available_exceptions_creation_date BEFORE INSERT ON maintcal_test.available_exceptions FOR EACH ROW EXECUTE PROCEDURE creation_date();')
        db_sess.execute('CREATE TRIGGER available_exceptions_modification_date BEFORE INSERT OR UPDATE ON maintcal_test.available_exceptions FOR EACH ROW EXECUTE PROCEDURE modification_date();')

        db_sess.commit()
        print "all tables and triggers created with no data."
        self._create_indexes(db_sess)
        print "all indexes installed."

    def shouldRollbackData(self):
        """
        Should we rollback the data changes?
        """
        return not self.options.skip_rollback

    def addDisabledTestWarning(self, stack_frame):
        """This takes a stack_frame of the disabled test method.
        The stack_frame is a tuple of:
        (frame_object, filename, line_number, func_name, lines_code, index_current_line)
        """ 
        disabled_info = (stack_frame[1], stack_frame[3])
        self.disabledTestWarnings.append(disabled_info)

    def print_results(self):
        totalTests = self.results.testsRun
        wasSuccessful = self.results.wasSuccessful()
        errors = len(self.results.errors)
        failures = len(self.results.failures)

        colors = {
            # text on colored background
            'red_highlight':      '\033[1;41m',
            'green_highlight':    '\033[1;42m',
            # remove color formatting
            'clear':              '\033[0m',
        }

        bar_string = " " * 79

        if self.results.wasSuccessful():
            print colors['green_highlight'] + bar_string + colors['clear']
        else:
            print colors['red_highlight'] + bar_string + colors['clear']

        enabled = totalTests - len(self.disabledTestWarnings)

        try:
            percentageEnabled = 1.0 - (float(len(self.disabledTestWarnings)) / totalTests)
        except ZeroDivisionError:
            percentageEnabled = 0.0

        percentageEnabled = int(100 * round(percentageEnabled, 2))

        print "Test Result Details:"
        print "Successful?: %s  Errors: %s  Failures: %s  --  Tests Run: %s  Disabled Tests: %s  Total Tests: %s  Percentage Enabled: %s%%" % (wasSuccessful, errors, failures, enabled, len(self.disabledTestWarnings), totalTests, percentageEnabled)

        if not self.options.quiet:
            if len(self.disabledTestWarnings) > 0:
                current_file = ''
                print "Disabled Tests:"
                for disabled_info in self.disabledTestWarnings:
                    if disabled_info[0] != current_file: 
                        print "\n    %s" % (disabled_info[0])
                        current_file = disabled_info[0] 
                    print "        %s" % (disabled_info[1])
                print ""



