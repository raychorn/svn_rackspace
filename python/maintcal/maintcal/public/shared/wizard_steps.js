var calendar_steps = [
        {
            step : '1',
            title : 'Name Calendar',
            description : 'Please name the new calendar.' + 
                        ' It should be distinct from other calendar names' +
                        ', although it doesn\'t have to be.',
            required : true,
            editor : 'textfield'
        },{
            step : '2',
            title : 'Description',
            description : 'You may provide an optional short description for ' +
                           'explaining the necessity of this calendar or ' +
                           'other notes' ,
            required : false,
            editor : 'textfield'
        },{
            step : '3',
            title : 'Maximum Bookings',
            description : 'This value represents the number of maintenances ' +
                          'that can be scheduled into this calendar at any ' +
                          'one time. For example if the Maximum Bookings ( ' +
                          'Max. Bookings ) is set to 3, then at any point ' +
                          'during the day up to 3 maintenances can be ' +
                          'scheduled into a single block of time.',
            required : true,
            defaultValue : '1',
            editor : 'textfield'
        },{
            step : '4',
            title : 'Default Timezone',
            description : 'This is the timezone that represents the location ' +
                           'of the team reponsible for handling maintenances ' +
                           ' for this calendar. This value will be used to ' +
                           'represent the local time for the maintenance ' +
                           'sub-tickets created in the CATS queue.',
            required : true,
            editor : 'tzpicker'
        },{
            step : '5',
            title : 'CATS Queue Reference',
            description : 'This is the CATS ticket queue that the calendar ' +
                          ' will default to in changing ticket attributes. ' +
                          'This can be overridden by controling where ' +
                          'maintenance tickets are created and refreshed ' +
                          'after successfully scheduling a maintenance.', 
            required : true,
            editor : 'queuepicker'
        },{
            step : '6',
            title : 'Maintenance Ticket Creation Queue',
            description : 'This is the CATS ticket queue that the calendar ' +
                          ' will use to create Maintenance Tickets in. ', 
            defaultValue : 5, 
            required : true,
            editor : 'queuepicker'
        },{
            step : '7',
            title : 'Maintenance Ticket Creation Subcategory',
            description : 'Tickets created by the Maintenance Calendar can be '+
                          'automatically set into a CATS Queue Category.',
            required : false,
            editor : 'categorypicker'
        },{
            step : '8',
            title : 'Maintenance Ticket Creation Status',
            description : 'Tickets created by the Maintenance Calendar can be '+
                          'automatically set into a CATS Queue Status.',
            defaultValue : 'New',
            required : true,
            editor : 'statuspicker'
        },{
            step : '9',
            title : 'Time before Maintenance Ticket Refresh',
            description : 'Once a Maintenance Ticket has been created, its ' +
                          'queue, subcategory and or its status can be ' +
                          'changed ( referred to as its "Refresh"). ' +
                          'This value is the number of hours before the ' +
                          'maintenance is scheduled to happen that the ' +
                          '"Refresh" occurs.',
            defaultValue : '2',
            required : true,
            editor : 'textfield'
        },{
            step : '10',
            title : 'Maintenance Ticket Refresh Queue',
            description : 'Once a Maintenance Ticket Refreshes it can be ' +
                          'moved to another queue.',
            defaultValue : 5,
            required : true,
            editor : 'queuepicker'
        },{
            step : '11',
            title : 'Maintenance Ticket Refresh Subcategory',
            description : 'Once a Maintenance Ticket Refreshes it can be also '+
                          'moved to another CATS Queue Subcategory.',
            required : false,
            editor : 'categorypicker'
        },{
            step : '12',
            title : 'Maintenance Ticket Refresh Status',
            description : 'Once a Maintenance Ticket Refreshes it can be also '+
                          'moved to another status.',
            defaultValue : 'New',
            required : true,
            editor : 'statuspicker'
        },{
            step : '13',
            title : 'Unassign Maintenance Ticket on Refresh',
            description : 'Once a Maintenance Ticket Refreshes it can also be '+
                          'unassigned from its current owner. Checking the ' +
                          'means that the ticket WILL be unassigned after ' +
                          'refresh.',
            required : true,
            editor : 'boolean'
        },{
            step : '14',
            title : 'Calendar Selector Rules Creation',
            description : 'In order for this calendar to be selected during ' +
                          'maintenance scheduling, it will need to have at ' +
                          'least one rule created for it that will evaluate ' +
                          'to either true or false indicating if it should ' +
                          'used in the maintenance process. <p>Rules are' +
                          'based around four "Rule Types" which determine ' +
                          'the attributes.',
            required : true,
            editor : 'ruletype'
        },{
            step : '15',
            title : 'Specify Rule Attributes',
            description : 'In the previous step a "Rule Type" was selected ' +
                          'and in this step an attribute will be selected. ' +
                          'A Rule Attribute is the key that will be used to ' +
                          'lookup a value that you will specify in the next ' +
                          'steps. For example if the "Rule Type" you selected' +
                          ' in the previous step was "Device" then if you' +
                          ' selected the attribute of "Department" a valid' +
                          ' value might be "IAD1". This rule would' +
                          ' become true if a device involved in a maintenance' +
                          ' was in the "IAD1" datacenter.',
            required : true,
            dependency : '14',
            editor : 'ruleattribute'
        },{
            step : '16',
            title : 'Select a Rule Operator',
            description : 'A Rule Operator is used to compare the "Rule ' +
                          'Attribute" ( selected in the previous step ) ' +
                          ' to a value specified in the next step. In many ' +
                          'cases a particular operator will not make any ' +
                          'sense. Such as selecting the ">=" ( Greater than ' +
                          ' or equal to ... ) operator in the case of the ' +
                          'previous example of a device in the "IAD1" ' +
                          'datacenter. One would want to use the "=" operator' +
                          ' in that case.', 
            required : true,
            editor : 'ruleoperator'
        },{
            step : '17',
            title : 'Specify a Value for the Rule to Operate on',
            description : 'A Rule Operator is used to compare the "Rule ' +
                          'Attribute" ( selected in the previous step ) ' +
                          ' to a value specified in the next step. In many ' +
                          'cases a particular operator will not make any ' +
                          'sense. Such as selecting the ">=" ( Greater than ' +
                          ' or equal to ... ) operator in the case of the ' +
                          'previous example of a device in the "IAD1" ' +
                          'datacenter. One would want to use the "=" operator' +
                          ' in that case.', 
            required : true,
            editor : 'textfield'
        },{
            step : '18',
            title : 'Calendar Creation Process is Complete !',
            description : 'The process for calendar creation is now complete' +
                          '. This calendar is currently inactive. Please ' +
                          ' review the information you have entered in the ' +
                          ' wizard by selecting this calendar from the list ' +
                          ' on left.', 
            isTerminal : true
        }];

var category_steps = [
        {
            step : '1',
            title : 'Mainteance Category Creation Wizard',
            description : ' In this process you will be creating a new ' + 
                          'maintenance category. The first step in this ' +
                          'process is to give the new Category a name.',
            required: true,
            editor : 'textfield'
        },{
            step : '2',
            title : 'Initial Service Type Creation',
            description : ' A Maintenance Category is not valid unless at ' +
                          'least one service type is associated with it.' +
                          ' Please specify the service type associated with ' +
                          'the new category.',
            required : true,
            editor : 'textfield'
        },{
            step : '3',
            title : ' Service Category Association',
            description : ' Each service type is associated with an existing' +
                          ' Service Category.',
            required : true,
            editor : 'servicecategory'
        },{
            step : '4',
            title : 'Length of Service',
            description : 'In this field you will enter a number of hours ' +
                        ' that this particular service will take. You can ' +
                        'specify half-hour increments as well as full hours',
            required : true,
            editor : 'textfield',
            validator : 'delta'
        },{
            step : '5',
            title : 'Lead Time Required',
            description : ' The Lead Time required for a particular service ' +
                        'type is the minimum amount of time that the calendar' +
                        ' will allow' ,
            required : true,
            editor : 'textfield',
            validator : 'delta'
        },{
            step : '6',
            title : 'Maintenance Category Creation is Complete !',
            description : ' You have completed the maintenance category creation'+
                        ' process. The service type associated with this ' +
                        ' category is currently inactive. Please review ' +
                        'the choices you have made by clicking on the ' +
                        'Service Type Admin button on the left and selecting ' +
                        ' the category you have just created. The category ' +
                        'will not appear in the Scheduling Window until ' +
                        'you have activated the service type.', 
            isTerminal : true
        }];

