/**
*   This class is responsible for representing the tentative dialog
*   that is displayed when a user selects a specific time.
*/

Ext.namespace('Rack.app.maintcal.tentativeDialog');

Rack.app.maintcal.tentativeDialog = function (schedule_view, recordSelected) {

    this.schedule_view      = schedule_view;

    //   recordSelected.json is an array of 3 elements: 
    //       [startJsDate, endJsDate, string representation of js date range]

    this.selected_time      = recordSelected;

    this.contactIsDirty     = false;
    this.currentOffset      = this.schedule_view.calendar.currentOffset;
    
    this.fillOptionsPanel = function () {
        var task = new Rack.app.maintcal.gatherTentativeDialog(this.schedule_view, this);
        return task.start();
    };
    
    this.updateOptionsPanel = function () {
        this.optionsPanel = new Ext.Panel({
            frame: true,
            html: this.fillOptionsPanel()
        });
        
        this.items.insert(0,'',this.optionsPanel);                
    };

    /**
    *   Get the information for the individual notes for the each calendar.
    */
    this.addScheduleMaintenanceNotes = function () {
        var cals_list   = this.schedule_view.calendar.selectedCalendars;
        var returnArray = [];
        var k;
        var calNotes = '';

        for (k = 0; k < cals_list.length; k++) {
            if (typeof this.schedule_view.storeCalTitle != 'undefined'){
                if (this.schedule_view.storeCalTitle[k] == cals_list[k].name){
                    calNotes = this.schedule_view.storeCalNotes[k];
                }
            }            
            var thisCalendarNotes = new Ext.form.TextArea({
                title: cals_list[k].name,
                calendar_id: cals_list[k].value,
                tabIndex: k+2,
                width: 480,
                height: 120,
                hideLabel: true,
                value: calNotes
            });
            returnArray.push(thisCalendarNotes);
            calNotes = '';
        }

        return returnArray;
    };

    /**
    *   This method is invoked when the user clicks the "Schedule" button.
    */
    this.scheduleMaintenance = function () {

        if (    this.contactCustomerBeforeField.getValue() 
            ||  this.contactCustomerAfterField.getValue()) {
            if (this.contactCustomerNameField.getValue() == "") {
                alert("Please provide a Customer Name for Contacting the Customer.");
                this.contactCustomerNameField.focus();
                return;
            }
            if (this.contactCustomerInfoField.getValue() == "") {
                alert("Please provide Customer Information for Contacting the Customer.");
                this.contactCustomerInfoField.focus();
                return;
            }

            var department_id = this.contactCustomerDepartmentField.getValue();

            if (department_id == "") {
                alert("Please select a department to Contact the Customer.");
                this.contactCustomerDepartmentField.focus();
                return;
            }
            
        }

        var calendar_count = this.schedule_view.calendar.selectedCalendars.length;

        //   We persist data in the schedule_view so that it will be available if the user
        //   chooses a different time instead of this one.

        this.schedule_view.storeGenNotes = this.generalNotes.getValue();
        this.schedule_view.storeCalTitle = [];
        this.schedule_view.storeCalNotes = [];

        //  Persist the customer contact data

        this.schedule_view.storeContactCustomer = [
            this.contactCustomerBeforeField.getValue(),
            this.contactCustomerAfterField.getValue(),
            this.contactCustomerNameField.getValue(),
            this.contactCustomerInfoField.getValue(),
            this.contactCustomerDepartmentField.getValue()
        ];

        if (calendar_count > 1) {
            var x;

            for ( x = 0 ; x < calendar_count; x++ ) {
                this.schedule_view.storeCalTitle[x] = this.calendarTabs.items.items[x].title;
                this.schedule_view.storeCalNotes[x] = this.calendarTabs.items.items[x].getValue();
            }
        }

        if (!this.contactIsDirty) {
            var task = new Rack.app.maintcal.updateMaintenanceDescriptions(this);
            task.start();
        }
        else {
            Ext.MessageBox.show({
                title: 'Alert',
                msg: "Please enter a valid contact",
                fn: this.contactField.focus,
                buttons: Ext.MessageBox.OK,
                width: 250,
                scope: this                                                                                  
            });
        }
    };

    this.temporaryCancelMessage = "User cancelled maintenance before scheduled.";

    this.cancelMaintenance =  function () {
        var cancelTask = new Rack.app.maintcal.cancelMaintenance(this.schedule_view.doc);
        cancelTask.start(null, this.temporaryCancelMessage);
        this.close();        
    };
    
    this.confirmMaintenance = function () {        
        var confirmTask = new Rack.app.maintcal.getConfirmationOptions(this.schedule_view, this.schedule_view.doc, this);
        confirmTask.start();
    };
   
    this.NagMessage = "Please give specific instructions for each of the " +
                    "maintenance groups . Lack of specifics might cause delays." +
                    " In fairness to your co-workers, please do not just " + 
                    " refer them to look at the SuperTicket.";

    this.NagPanel = new Ext.Panel({
        frame: true,
        html: this.NagMessage
    });
    
    var generalNotesValue = '';

    if (this.schedule_view.storeGenNotes){
        generalNotesValue = this.schedule_view.storeGenNotes;
    };
    
    this.generalNotes = new Ext.form.TextArea({
        tabIndex: 1,
        width: 660,
        height: 120,
        hideLabel: true,
        value: generalNotesValue
    });

    this.generalNotesPanel = new Ext.Panel({
        title: 'General Maintenance Notes for All Maintenance Groups',
        layout: 'fit',
        height: 120,
        collapsible: false,
        bodyStyle: 'margin:5px; background-color:transparent;',
        footer: false,
        items: this.generalNotes
    });

    this.contactField = new Ext.form.TextField({
        hideLabel: true,
        tabIndex: 2,
        width: 150
    });

    // set the current user to the value of the contact field.
    this.contactField.setValue(this.schedule_view.doc.contact);
    this.contactField.on('change', this.handleContactField, this);
    
    this.calendarTabs = new Ext.TabPanel({
        frame: true,
        activeTab: 0,
        tabPosition: 'top',
        width: 684,
        height: 148,
        layoutOnTabChange: true,
        enableTabScroll: true,
        items: this.addScheduleMaintenanceNotes()
    });

    this.specificNotesPanel = new Ext.Panel({
        title: 'Group Specific Notes',
        height: 170,
        collapsible: false,
        bodyStyle: 'margin:5px',
        items: this.calendarTabs
    });

    //  Customer Contact Form

    this.contactCustomerCheckboxHandler = function (checkbox, checked) {
        if (    this.contactCustomerBeforeField.getValue() 
            ||  this.contactCustomerAfterField.getValue()) {
            this.contactCustomerNameField.enable();
            this.contactCustomerInfoField.enable();
            this.contactCustomerDepartmentField.enable();
        } else {
            this.contactCustomerNameField.disable();
            this.contactCustomerInfoField.disable();
            this.contactCustomerDepartmentField.disable();
        }
    };

    this.contactCustomerBeforeLabel = new Rack.app.maintcal.Label({cls: 'mc-tentative-msg'});
    this.contactCustomerBeforeLabel.setText("Contact Customer Before Maintenance? ");

    this.contactCustomerBeforeField = new Ext.form.Checkbox({
        id: 'contactCustomerBeforeField',
        name: 'contactCustomerBeforeField',
        itemCls: 'mc-SVSO-chkbox',
        style: 'dislpay:inline;text-align:right'
    });
    
    this.contactCustomerBeforeField.on('check', this.contactCustomerCheckboxHandler, this);

    this.contactCustomerAfterLabel = new Rack.app.maintcal.Label({cls: 'mc-tentative-msg'});
    this.contactCustomerAfterLabel.setText("Contact Customer After Maintenance? ");

    this.contactCustomerAfterField = new Ext.form.Checkbox({
        id: 'contactCustomerAfterField',
        name: 'contactCustomerAfterField',
        itemCls: 'mc-SVSO-chkbox',
        style: 'dislpay:inline;text-align:right'
    });

    this.contactCustomerAfterField.on('check', this.contactCustomerCheckboxHandler, this);

    this.contactCustomerNameLabel = new Rack.app.maintcal.Label({cls: 'mc-tentative-msg'});
    this.contactCustomerNameLabel.setText("Customer Name: ");

    this.contactCustomerNameField = new Ext.form.TextField({
        id: 'contactCustomerNameField',
        name: 'contactCustomerNameField',
        width: 150
    });

    this.contactCustomerNameField.disable();

    this.contactCustomerInfoLabel = new Rack.app.maintcal.Label({cls: 'mc-tentative-msg'});
    this.contactCustomerInfoLabel.setText("Customer Phone or Email:");

    this.contactCustomerInfoField = new Ext.form.TextField({
        id: 'contactCustomerInfoField',
        name: 'contactCustomerInfoField',
        width: 150
    });

    this.contactCustomerInfoField.disable();

    this.contactCustomerDepartmentLabel = new Rack.app.maintcal.Label({cls: 'mc-tentative-msg'});
    this.contactCustomerDepartmentLabel.setText('Department that should Contact Customer:');

    var calendar_list       = this.schedule_view.calendar.selectedCalendars;
    var department_options  = [];
    var i;

    var notify_statuses     = this.schedule_view.doc.notify_statuses;

    for ( i = 0 ; i < calendar_list.length ; i++ ) {
        //  Skip queues that do not have an "In Progress" status
        if (! notify_statuses.hasOwnProperty(calendar_list[i].value)) {
            continue;
        }
        department_options.push([calendar_list[i].value, calendar_list[i].name]);
    }

    this.contactCustomerDepartmentFieldStore = new Ext.data.SimpleStore({
        id: 0,
        fields: [
            'department_id',
            'displayText'
        ],
        data: department_options
    });

    this.contactCustomerDepartmentField = new Ext.form.ComboBox({
        name: 'contactCustomerDepartmentField',
        allowBlank: true,
        editable: false,
        triggerAction: 'all',
        typeAhead: false,
        mode: 'local',
        hiddenName: 'hidden_contactCustomerDepartmentField',
        readOnly: true,
        store: this.contactCustomerDepartmentFieldStore,
        valueField: 'department_id',
        displayField: 'displayText'
    });

    //  If there are no available departments, then disable notification
    if (department_options.length == 0) {
        this.contactCustomerBeforeField.disable();
        this.contactCustomerAfterField.disable();
    } 

    this.contactCustomerDepartmentField.disable();

    var contactCustomerPanelItems = 
        [
            {
                layout: 'table',
                layoutConfig: {columns: 4},
                style:  'width: 100%',
                items:  [ this.contactCustomerBeforeLabel, this.contactCustomerBeforeField,
                          this.contactCustomerAfterLabel,  this.contactCustomerAfterField ] 
            },
            {
                style:  'width: 100%',
                layout: 'table',
                layoutConfig: {columns: 4},
                items:  [ this.contactCustomerNameLabel, this.contactCustomerNameField,
                          this.contactCustomerInfoLabel, this.contactCustomerInfoField ]
            },
            {
                style:  'width: 100%',
                layout: 'table',
                layoutConfig: {columns: 2},
                items:  [ this.contactCustomerDepartmentLabel, this.contactCustomerDepartmentField ]

                //layout: 'border',
                //items:  [ { region:'west',   items: [this.contactCustomerDepartmentLabel] }, 
                //          { region:'center', items: [this.contactCustomerDepartmentField] }]
            }
        ];

    this.contactCustomerPanel = new Ext.Panel({
        frame:          true,
        style:          'width: 100%',
        layout:         'table',
        layoutConfig:   { columns: 1 },
        items:          contactCustomerPanelItems
    });

    if (this.schedule_view.storeContactCustomer) {
        this.contactCustomerBeforeField.setValue(       this.schedule_view.storeContactCustomer[0]),
        this.contactCustomerAfterField.setValue(        this.schedule_view.storeContactCustomer[1]),
        this.contactCustomerNameField.setValue(         this.schedule_view.storeContactCustomer[2]),
        this.contactCustomerInfoField.setValue(         this.schedule_view.storeContactCustomer[3]),
        this.contactCustomerDepartmentField.setValue(   this.schedule_view.storeContactCustomer[4])
    }

    //

    var sistring = []; 

    var lastIndex = this.selected_time.json[2].lastIndexOf(' ');
    var maint_time = this.selected_time.json[2].substring(0,lastIndex);    
    
    sistring.push('<table class="mc-sv-tentative-text" width=675><tr><td>Date: <span>' + this.schedule_view.calendar.activeDate.format('l - F j, Y') + '</span></td>');
    sistring.push('<td align="right">Account: <span>' + this.schedule_view.doc.account_number + ' - ' + Ext.util.Format.ellipsis(this.schedule_view.doc.account_name,45) + '</span></td></tr>');
    sistring.push('<tr><td>Time: <span>' + maint_time + ' ');
    sistring.push(decodeURIComponent(this.schedule_view.doc.selectedZoneName) + '</span></td>');
    sistring.push('<td align="right">SuperTicket: <span>' + this.schedule_view.doc.master_ticket + '</span></td></tr></table>');
    this.schedInfoHtml = sistring.join('');

    this.schedInfoPanel = new Ext.Panel({
        frame: true,
        html: this.schedInfoHtml
    });  

    var cals_list = this.schedule_view.calendar.selectedCalendars;
    this.tentativePanels = []
    if (cals_list.length <= 1) {
        //  If only one calendar has been selected:
        this.tentativePanels = [
            this.generalNotesPanel,
            this.contactCustomerPanel,            
            this.schedInfoPanel
        ]
    }
    else {
        //  If multiple calendars have been selected:
        this.tentativePanels = [
            this.generalNotesPanel,
            this.NagPanel,
            this.calendarTabs,
            this.contactCustomerPanel,            
            this.schedInfoPanel            
        ]
    }
  
    var config = {
        width: 700,
        autoScroll: true,
        draggable: false,
        resizable: false,
        shadow: true,
        closeAction: 'close',
        title: 'Tentatively Scheduled Maintenance Options',
        plain: true,
        frame: true,
        modal: true,
        defaultButton: 0,
        buttons: [{
            text: 'Schedule',
            handler: this.scheduleMaintenance,
            scope: this
        }, {
            text: 'Cancel',
            handler: this.cancelMaintenance,
            scope: this
        }],
        items: this.tentativePanels
    };

    Ext.Window.call(this, config);

    this.on('show', this.focusFirstItem, this);
};

Ext.extend(Rack.app.maintcal.tentativeDialog, Ext.Window, {
    handleContactField : function (f, n, o) {
        if (o !== n) {
            this.contactIsDirty = true;
            var validateTask = new Rack.app.maintcal.validateContact(this);
            validateTask.start();
        }
    },

    focusFirstItem : function () {
        this.generalNotes.focus(false, true);
    }
});

