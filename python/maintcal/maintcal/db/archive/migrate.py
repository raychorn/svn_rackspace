#!/usr/bin/env python

import psycopg
import sys
import xmlrpclib

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

from_connection_string = '''
    dbname=core_dev host=devdb2.core.redacted.com user=core_write password=""
'''
to_connection_string = '''
    dbname=core_dev host=devdb2.core.redacted.com user=core_write password=""
'''

from_schema = ''
to_schema = 'mcal'

xmlrpc_url = 'https://vcoreudev6.dev.core.redacted.com'
xmlrpc_login = 'emao'
xmlrpc_password = 'qwerty'

#  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #

if len(from_schema) > 0 and from_schema[-1] != '.':
    from_schema += '.'
if len(to_schema) > 0 and to_schema[-1] != '.':
    to_schema += '.'

from_connection = psycopg.connect(from_connection_string)
to_connection = psycopg.connect(to_connection_string)

from_cursor = from_connection.cursor()
to_cursor = to_connection.cursor()

xmlrpc_auth = xmlrpclib.Server('%s/xmlrpc/Auth' % (xmlrpc_url))
xmlrpc_token = xmlrpc_auth.userLogin(xmlrpc_login, xmlrpc_password)
xmlrpc_computer = xmlrpclib.Server(
    '%s/xmlrpc/Computer/::session_id::%s' % (xmlrpc_url, xmlrpc_token)
)

from_queue_to_queue_map = {
     2:  9, # DC Ops (SAT1)
     3: 12, # DC Ops (LON1)
     4: 10, # DC Ops (SAT2)
     5:  8, # DC Ops (IAD1)
     7:  3, # Managed Windows (M1,M3,M5,M7,M9)
     8:  4, # Managed Unix (M2,M4,M6,M8,M12)
    12:  7, # DC Ops (DFW1)
    14: 11, # DC Ops (SAT4)
    16:  5, # Intensive Network Security
    17: 14, # DC Ops (LONB)
    18: 13, # DC Ops (LON2)
    20:  6, # Managed NetSec
    21:  2, # Intensive Unix
    22:  1, # Intensive Windows
    24: 15, # Managed Storage
    45: 16  # DC Ops (LON3)
}

from_queue_time_conversion_map = {
     2: "'%s' at time zone 'US/Central'",    # DC Ops (SAT1)
     3: "'%s' at time zone 'Europe/London'", # DC Ops (LON1)
     4: "'%s' at time zone 'US/Central'",    # DC Ops (SAT2)
     5: "'%s' at time zone 'US/Eastern'",    # DC Ops (IAD1)
     7: "'%s' at time zone 'US/Central'",    # Managed Windows
     8: "'%s' at time zone 'US/Central'",    # Managed Unix
    12: "'%s' at time zone 'US/Central'",    # DC Ops (DFW1)
    14: "'%s' at time zone 'US/Central'",    # DC Ops (SAT4)
    16: "'%s' at time zone 'US/Central'",    # Intensive Network Security
    17: "'%s' at time zone 'Europe/London'", # DC Ops (LONB)
    18: "'%s' at time zone 'Europe/London'", # DC Ops (LON2)
    20: "'%s' at time zone 'US/Central'",    # Managed NetSec
    21: "'%s' at time zone 'US/Central'",    # Intensive Unix
    22: "'%s' at time zone 'US/Central'",    # Intensive Windows
    24: "'%s' at time zone 'US/Central'",     # Managed Storage
    45: "'%s' at time zone 'Europe/London'", # DC Ops (LON3)
}

sql = '''
    select  t.id,
            t.length
    from    %(to_schema)sservice_type t,
            %(to_schema)sservice_category c
    where   t.name = 'Other'
    and     t.service_category_id = c.id
    and     c.name = 'General'
''' % {'to_schema': to_schema}
print "Discovering service type General/Other's details:", sql
to_cursor.execute(sql)
row = to_cursor.fetchone()
to_service_type_id = row[0]
to_service_type_length = row[1]
print "General/Other's details are id = %s and length = %s." % (
    to_service_type_id,
    to_service_type_length
)

sql = '''
    select  u."Description",
            t."ReferenceNumber",
            u.start_time,
            u.start_time + cast(y.length || ' minutes' as interval) as end_time,
            u."CONT_ContactID",
            u."UPGD_QueueID",
            a."AccountNumber",
            t."TCKT_TicketID",
            u."DateAssigned"
    from    %s"UPGD_ScheduledService" u,
            %s"UPGD_val_ServiceType" y,
            %s"TCKT_Ticket" t,
            %s"ACCT_xref_Account_Ticket" x,
            %s"ACCT_Account" a
    where   u."UPGD_QueueID" in (%s)
    and     (u.start_time >= now() or u.end_time >= now())
    and     u."UPGD_val_ServiceTypeID" = y."UPGD_val_ServiceTypeID"
    and     u."TCKT_TicketID" = t."TCKT_TicketID"
    and     t."TCKT_TicketID" = x."TCKT_TicketID"
    and     x."ACCT_AccountID" = a."ID"
''' % (
    from_schema,
    from_schema,
    from_schema,
    from_schema,
    from_schema,
    ', '.join(str(k) for k in from_queue_to_queue_map.keys())
)
print "Gathering scheduled services to migrate with:", sql
from_cursor.execute(sql)
print "Found %s scheduled services to migrate." % (from_cursor.rowcount)

# Account dictionary
acct_dict = {}

for from_scheduled_service in from_cursor.dictfetchall():
    sql = '''
        select id, date_assigned
        from   %sscheduled_maintenance
        where  master_ticket = '%s'
    ''' % (
        to_schema,
        from_scheduled_service['ReferenceNumber']
    )
    print "Checking for existing scheduled maintenance:", sql
    to_cursor.execute(sql)
    for ex_scheduled_maintenance in to_cursor.dictfetchall():
        if ex_scheduled_maintenance['date_assigned'] != from_scheduled_service['DateAssigned']:
            print "Found existing scheduled maintenance that has been modified since conversion, skipping", ex_scheduled_maintenance
            continue
        else:
            print "Found existing scheduled maintenance, but not modified since conversion", ex_scheduled_maintenance
            sql = '''
                delete
                from   %sxref_scheduled_service_server_list
                where  scheduled_service_id in (
                    select id
                    from   %sscheduled_service
                    where  scheduled_maintenance_id = %s
                )
                ;
                delete
                from   %sscheduled_service
                where  scheduled_maintenance_id = %s
                ;
                delete
                from   %sscheduled_maintenance
                where  id = %s
            ''' % (
                to_schema,
                to_schema,
                ex_scheduled_maintenance['id'],
                to_schema,
                ex_scheduled_maintenance['id'],
                to_schema,
                ex_scheduled_maintenance['id']
            )
            print "Removing previous conversion to make way for reconversion:", sql
            to_cursor.execute(sql)
    
    print "Converting from scheduled service:", from_scheduled_service
    from_queue_id = from_scheduled_service['UPGD_QueueID']
    to_calendar_id = \
        from_queue_to_queue_map[from_scheduled_service['UPGD_QueueID']]
    time_conversion = from_queue_time_conversion_map[from_queue_id]

    sql = '''
        insert into %sscheduled_maintenance (
            master_ticket,
            account_id,
            account_name,
            state_id,
            additional_duration,
            expedite,
            general_description,
            service_type_id,
            contact_id,
            date_assigned
        ) values ('%s', %s, 'Not available', 3, %s, 'f', '%s', %s, %s, '%s')
    ''' % (
        to_schema,
        from_scheduled_service['ReferenceNumber'],
        from_scheduled_service['AccountNumber'],
        """
              cast('%s' as timestamp)
            - cast('%s' as timestamp)
            - cast('%s' as interval)
        """ % (
            from_scheduled_service['end_time'],
            from_scheduled_service['start_time'],
            to_service_type_length
        ),
        from_scheduled_service['Description'].replace("'", "''"),
        to_service_type_id,
        from_scheduled_service['CONT_ContactID'],
        from_scheduled_service['DateAssigned']
    )
    print "Inserting to scheduled maintenance:", sql
    to_cursor.execute(sql)

    sql = '''
        select  id
        from    %sscheduled_maintenance
        where   master_ticket = '%s'
    ''' % (
        to_schema,
        from_scheduled_service['ReferenceNumber']
    )
    print "Discovering id of that last entry:", sql
    to_cursor.execute(sql)
    to_scheduled_maintenance_id = to_cursor.fetchone()[0]

    sql = '''
        insert into %sscheduled_service (
            description,
            ticket_number,
            start_time,
            end_time,
            calendar_id,
            scheduled_maintenance_id,
            state_id
        ) values ('%s', '%s', %s, %s, %s, %s, 2)
    ''' % (
        to_schema,
        from_scheduled_service['Description'].replace("'", "''"),
        from_scheduled_service['ReferenceNumber'],
        time_conversion % (from_scheduled_service['start_time']),
        time_conversion % (from_scheduled_service['end_time']),
        to_calendar_id,
        to_scheduled_maintenance_id
    )
    print "Inserting to scheduled service:", sql
    to_cursor.execute(sql)

    sql = '''
        select  id,
                start_time,
                end_time
        from    %sscheduled_service
        where   ticket_number = '%s'
    ''' % (
        to_schema,
        from_scheduled_service['ReferenceNumber']
    )
    print 'Retrieving scheduled service id to link to:', sql
    to_cursor.execute(sql)
    row = to_cursor.fetchone()
    to_scheduled_service_id = row[0]
    to_start_time = row[1]
    to_end_time = row[2]

    sql = '''
        select  computer_number
        from    %s"xref_server_Ticket"
        where   "TCKT_TicketID" = %s
    ''' % (
        from_schema,
        from_scheduled_service['TCKT_TicketID']
    )
    print "Gathering server numbers for maintenance:", sql
    from_cursor.execute(sql)
    for from_server in from_cursor.dictfetchall():
        sql = '''
            select  id
            from    %sserver_cache
            where   id = %s
        ''' % (
            to_schema,
            from_server['computer_number']
        )
        print 'Checking if we already have server info cached', sql
        to_cursor.execute(sql)
        if to_cursor.rowcount > 0:
            print 'We already had server info cached',
            print from_server['computer_number']

        else:

            print 'No cached info; gathering server info via XMLRPC:',
            print from_server
            xmlrpc_server = xmlrpc_computer.getDetailsByComputers(
                [from_server['computer_number']]
            )
            if len(xmlrpc_server) < 1:
                print 'WARNING: Could not gather XMLRPC info about server',
                print from_server['computer_number'], ':::::', xmlrpc_server
                continue
            xmlrpc_server = xmlrpc_server[0]
            print 'Info gathered:', xmlrpc_server
            if xmlrpc_server['customer'] not in acct_dict.keys():
                acct_dict[xmlrpc_server['customer']] = xmlrpc_server['customer_name']
            to_has_managed_storage = 'f'
            if xmlrpc_server['has_managed_storage']:
                to_has_managed_storage = 't'
            sql = '''
                insert into %sserver_cache (
                    id,
                    name,
                    os_type,
                    datacenter_symbol,
                    has_managed_storage,
                    segment,
                    icon
                ) values (%s, '%s', '%s', '%s', '%s', '%s', '%s')
            ''' % (
                to_schema,
                xmlrpc_server['server'],
                str(xmlrpc_server['server_name']),
                xmlrpc_server['os_group'],
                xmlrpc_server['datacenter'],
                to_has_managed_storage,
                xmlrpc_server['segment'],
                xmlrpc_server['icon']
            )
            print "Adding server to cache:", sql
            to_cursor.execute(sql)

        sql = '''
            insert into %sxref_scheduled_service_server_list (
                scheduled_service_id,
                computer_number
            ) values (%s, %s)
        ''' % (
            to_schema,
            to_scheduled_service_id,
            from_server['computer_number']
        )
        print 'Linking scheduled service and server:', sql
        to_cursor.execute(sql)

        sql = '''
            select  bookings
            from    %scalendar
            where   id = %s
        ''' % (
            to_schema,
            to_calendar_id
        )
        print 'Retreiving new calendar info:', sql
        to_cursor.execute(sql)
        calendar_default_bookings = to_cursor.fetchone()[0]

        sql = '''
            select      id,
                        bookings,
                        start_time,
                        end_time
            from        %stimes_available
            where       calendar_id = %s
            and         start_time < '%s'
            and         end_time > '%s'
            order by    start_time
        ''' % (
            to_schema,
            to_calendar_id,
            to_end_time,
            to_start_time
        )
        print 'Gathering existing times_available entries:', sql
        to_cursor.execute(sql)
        blocks = to_cursor.dictfetchall()
        print 'Got %s times_available entries:', len(blocks)

        done = False
        p = to_start_time
        if len(blocks) > 0 and blocks[0]['start_time'] < to_start_time:
            if blocks[0]['bookings'] <= 0:
                print 'WARNING: Time Unavailable: Calendar %s,' % (
                    to_calendar_id
                )
                print '         Requested Time: %s,' % (
                    to_start_time
                )
                print '         Conflicting Time: %s' % (
                    blocks[0]['start_time']
                )
                print '         Scheduled maintenance was still created.'
                done = True
            else:
                head_block = blocks.pop(0)
                p = head_block['end_time']
                if head_block['end_time'] > to_end_time:
                    print 'Block starts before and ends after ours:', head_block
                    sql = '''
                        insert into %stimes_available (
                            calendar_id,
                            bookings,
                            start_time,
                            end_time
                        ) values (%s, %s, '%s', '%s')
                    ''' % (
                        to_schema,
                        to_calendar_id,
                        head_block['bookings'] - 1,
                        to_start_time,
                        to_end_time
                    )
                    print 'Adding new block for our area, minus a booking.', sql
                    to_cursor.execute(sql)

                    sql = '''
                        insert into %stimes_available (
                            calendar_id,
                            bookings,
                            start_time,
                            end_time
                        ) values (%s, %s, '%s', '%s')
                    ''' % (
                        to_schema,
                        to_calendar_id,
                        head_block['bookings'],
                        to_end_time,
                        head_block['end_time']
                    )
                    print 'Adding new block for area past ours.', sql
                    to_cursor.execute(sql)

                    sql = '''
                        update  %stimes_available
                        set     end_time = '%s'
                        where   id = %s
                    ''' % (
                        to_schema,
                        to_start_time,
                        head_block['id']
                    )
                    print 'Shortening original block to just before ours.', sql
                    to_cursor.execute(sql)

        if  not done \
            and len(blocks) > 0 \
            and blocks[-1]['end_time'] > to_end_time:
            print 'Block starts after ours, but goes beyond it:', blocks[-1]
            if blocks[-1]['bookings'] <= 0:
                print 'WARNING: Time Unavailable [b]: Calendar %s,' % (
                    to_calendar_id
                )
                print '         Requested Time: %s,' % (
                    to_start_time
                )
                print '         Conflicting Time: %s' % (
                    blocks[-1]['start_time']
                )
                print '         Scheduled maintenance was still created.'
                done = True
            else:
                tail_block = blocks.pop(-1)
                sql = '''
                    insert into %stimes_available (
                        calendar_id,
                        bookings,
                        start_time,
                        end_time
                    ) values (%s, %s, '%s', '%s')
                ''' % (
                    to_schema,
                    to_calendar_id,
                    tail_block['bookings'] - 1,
                    tail_block['start_time'],
                    to_end_time
                )
                print 'Adding new block for our area, minus a booking.', sql
                to_cursor.execute(sql)

                sql = '''
                    update  %stimes_available
                    set     start_time = '%s'
                    where   id = %s
                ''' % (
                    to_schema,
                    to_end_time,
                    tail_block['id']
                )
                print 'Shortening original block to just after ours.', sql
                to_cursor.execute(sql)

        if not done:
            for block in blocks:
                print 'Block is within ours:', block
                if block['bookings'] <= 0:
                    print 'WARNING: Time Unavailable [b]: Calendar %s,' % (
                        to_calendar_id
                    )
                    print '         Requested Time: %s,' % (
                        to_start_time
                    )
                    print '         Conflicting Time: %s' % (
                        block['start_time']
                    )
                    print '         Scheduled maintenance was still created.'
                    done = True
                    break
                if p < block['start_time']:
                    sql = '''
                        insert into %stimes_available (
                            calendar_id,
                            bookings,
                            start_time,
                            end_time
                        ) values (%s, %s, '%s', '%s')
                    ''' % (
                        to_schema,
                        to_calendar_id,
                        calendar_default_bookings - 1,
                        p,
                        block['start_time']
                    )
                    print 'Adding new default block, minus a booking, for ' \
                          'our area where there is no overlap.', sql
                    to_cursor.execute(sql)

                sql = '''
                    update  %stimes_available
                    set     bookings = %s
                    where   id = %s
                ''' % (
                    to_schema,
                    block['bookings'] - 1,
                    block['id']
                )
                print 'Taking a booking away from original block.', sql
                to_cursor.execute(sql)

                p = block['end_time']

        if not done and p < to_end_time:
            sql = '''
                insert into %stimes_available (
                    calendar_id,
                    bookings,
                    start_time,
                    end_time
                ) values (%s, %s, '%s', '%s')
            ''' % (
                to_schema,
                to_calendar_id,
                calendar_default_bookings - 1,
                p,
                to_end_time
            )
            print 'Adding new default block, minus a booking, for ' \
                  'our area where there is no overlap [b].', sql
            to_cursor.execute(sql)

# Populate the account names on the scheduled_maintenance table
for acct_id in acct_dict.keys():
    sql = '''
        update %sscheduled_maintenance set
            account_name='%s'
        where
            account_id=%s
        ''' % (
            to_schema,
            acct_dict[acct_id].replace("'", "\\'").encode('ascii','ignore'),
            acct_id
        )
    print 'Setting account name to "%s" where account id is %s:\n%s' % \
        (acct_dict[acct_id], acct_id, sql)
    to_cursor.execute(sql)

if len(sys.argv) == 2 and sys.argv[1].lower() == 'commit':
    print 'Commit command was given. Committing changes.'
    from_connection.commit()
    to_connection.commit()
else:
    print 'Commit command was not given. Rolling back.'
    from_connection.rollback()
    to_connection.rollback()

