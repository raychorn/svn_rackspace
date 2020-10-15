import psycopg2
import pprint
import sys

DB_HOSTNAME = 'dev.db.core.redacted.com'
DB_HOSTPORT = 5432
DB_NAME = 'core_dev'
DB_USER = 'core_write'

def sort_results(a,b):
    return cmp(a['time'],b['time'])

conn = psycopg2.connect(host=DB_HOSTNAME,user=DB_USER,database=DB_NAME)

cursor = conn.cursor()

fname = file(sys.argv[1],'r')
all = fname.read()
query_key = 0
all_results = {}
for stmt in all.split(';'):
    query_key += 1
    t = 0
    if 'SELECT' not in  stmt:
        continue
    for i in range(5):
        try:
            cursor.execute(stmt)
        except psycopg2.ProgrammingError, e:
            #print stmt
            #print e
            raise e
        all_r = cursor.fetchall()
        t += float(all_r[-1][0].split(':')[1].strip()[:-3])
    time = t/5
    all_results[query_key] = {'stmt' : stmt, 
        'plan' : '\n'.join([r[0] for r in all_r]),
        'time' : time}

results_list = [v for k,v in all_results.items()]
results_list.sort(lambda a,b: cmp(b['time'],a['time'])) 
outf = file('cal-sql-report_CTS.txt','w')
pprint.pprint(results_list,outf) 
