This file is for you to describe the maintcal application. Typically
you would include information such as the information below:

Installation and Setup
======================

Install ``maintcal`` using easy_install::

    easy_install maintcal

Make a config file as follows::

    paster make-config maintcal config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

To run a development server on port 5000

    paster serve development.ini

Developer Notes
=======================

Do NOT use mxdatetime inside of maintenance calendar.

Only use the python standard datetime library.

They do NOT play well together.

Template Notes:
=======================

tickets_info.mako

    This is rendered inside of the ticket/view.pt page in CORE
    when the user clicks on the Maintenance Info section 
    on the left of the page.


Javascript Notes
=======================

Even though we are using Ext, we will use "id" attributes.

This is because we are not designing maintenance calendar to
be loaded more than once in the same window, so there should
be no id duplication to worry about. 

Javascript:
=======================

calendar_view/

    This is displayed when a core user selects the
    "Maintenance Calendar" option under the "CORE" menu.



maintenance_view/

    This is displayed when the user clicks on
    the "Maintenance Info" link from the ticket page in core.

    doc/
        maintenance.js

    tasks/
        maintenanceTasks.js

    view/
        maintenanceView.js
            This is the top-level view and
            the left column.

        serviceView.js
            This is the right column

schedule/
    This is where the user is sent when they try to schedule
    a maintenance from the core ticket page.


    at some point:

        POST maintenances/create

    then

        GET maintenances/times_available



    Clicking "Update Available Times"
    ->
    Display list of times.

    
    Double clicking a time 
    ->
        invokes scheduleView.js scheduleTenative()

    -->
    Displays "Tenative Scheduled Maintenance Options"

        js/view/tentativeDialog.js    



    Clicking "Schedule" button
    -->
        POST maintenances/schedule/( some id )/
            update overall info?

            js/tasks/tentativeDialogTask
                updateMaintenanceDescriptions()

        For each service involved:
            POST services/update/( service id? )/
             

        Handled by:
    
        js/tasks/confirmationDialogTasks.js

            getConfirmationOptions()

        Handled by on the server:

        GET maintenances/(maint_id).sjon?tzname=
    

    ->
    Displays "Confirm Scheduled Maintenance"

        js/view/confirmationDialog.js

        NOTE: the private comment has already been added to the ticket
        at this point.


    
    


