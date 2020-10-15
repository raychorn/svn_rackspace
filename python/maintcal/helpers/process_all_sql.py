f = file('all-cal-sql.txt','r')
o = file('processed-cal-sql.txt','w')

interesting_block = 10 
for line in f.readlines():

    if interesting_block <= 4:
        interesting_block += 1
        if interesting_block == 5:
            interesting_block = 10
            continue 

        o.write(line)
        continue
    if '36d0 SELECT' in line:
        interesting_block = 1 
        o.write(line)

f.close()
o.close()
         
