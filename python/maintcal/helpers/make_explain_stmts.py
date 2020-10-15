import sys
import datetime

inpt = file(sys.argv[1],'r')

outf = file('last_explain_analyzes.sql','w')
line = inpt.readline()
in_select = False
while line:
    if in_select and not line.startswith('2012-05-10'):
        # "inside" a select block.
        stmt = stmt + line
    if line.startswith('2012-05-10'):
        if '{' in line and '}' in line:
            # a parameter dictionary.
            in_select = False
            # get single quotes around dates and strings.
            params_dict = eval(line[68:])
            for k in params_dict.keys():
                if isinstance(params_dict[k], str):
                    params_dict[k] = "'" + params_dict[k] + "'"

                if isinstance(params_dict[k],datetime.datetime) or \
                    isinstance(params_dict[k], datetime.date):
                    params_dict[k] = "'" + str(params_dict[k]) + "'"

            stmt = stmt % params_dict 
            stmt = stmt.replace('maintcal_test.','mcal.')
            outf.write('EXPLAIN ANALYZE ' + stmt.strip() + ';\n\n')
        # "guess" what it is.
        if 'SELECT' in line:
            # probably a select stmt.
            in_select = True
            stmt = line[68:]
    line = inpt.readline()

