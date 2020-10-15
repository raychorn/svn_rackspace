/**
*   This seems to be the top-level schedule maintenance window.
*
*   It contains the bigcal, the options on the left, 
*   and the update times available button.
*/

Ext.namespace('Rack.app.maintcal.scheduleView');

Rack.app.maintcal.scheduleView = function (schedule_model) {
    this.doc = schedule_model;
    
    // timezone Manager instance
    this.tzMan = new Rack.app.maintcal.tzManager({
        initialLoad : true
    });

    this.tzMan.on('currenttz', this.handleTZSet, this);
    this.doc.on('widgetsready', this.handleWidgetsReady, this);

    // listen to the devices model object for data errors
    this.doc.devices.on('dataerror',this.showDataError,this);
    this.doc.on('dataerror', this.showDataError, this);

    //listen to the serviceTypes for dataerrors
    this.doc.serviceTypes.on('dataerror', this.showDataError, this);

    // listen to the options model for dataerrors.
    this.doc.options.on('dataerror', this.showDataError, this);

    // get the document body for use by the masking
    this.body = Ext.getBody();

    // move this down to where the constructor is inited.
    this.setTimeFormat();
    this.calendar = new Ext.bigcal({
        useTZPicker: true,
        scheduling: true,
        timeFormat: this.timeFormat
    });
    Ext.onReady(this.getCurrentTZ, this);
};

Ext.extend(Rack.app.maintcal.scheduleView, Ext.util.Observable, {

    title: "Schedule Maintenance",

    genericDataErrorText : "There has been an undefined error. Please try " +
                            "again.",

    expediteWarningText : "You must have prior approval to select the " +
                        " Expedite option. By selecting the Expedite " +
                        "option all lead times will be disregarded. " +
                        "Please contact the associated groups for approval " +
                        "and to confirm available resources.",

    moreDevicesWarning :  "You have included 4 or more servers in this " +
                        "request. Please contact the associated groups to" + 
                        "confirm the appropriate time required to complete " +
                        "this maintenance. Please increase the maintenace " +
                        "duration to accommodate the extra servers.",

    getCurrentTZ : function () {
        if (!UASCheck()) {
            // run a check of user agent check for Firefox2.x or IE
            return false;
        }
        this.currentTZ = this.tzMan.check();
        if (!this.currentTZ) {
            this.tzMan.show();
        }
        else {
            this.doc.selectedZoneName = this.currentTZ;
            this.getPageData();
        }
    },

    handleTZSet : function (tz_val, initial_load) {
        this.currentTZ = tz_val;
        if (initial_load) {
            this.getPageData();
        }
        else {
            // reload the current window.
            var currentURL = window.location.href;
            window.location.href = currentURL;
        }
    },

    handleTZChangeRequest : function () {
        this.tzMan = new Rack.app.maintcal.tzManager({
            initialLoad : false
        });
         // event listeners.
        this.tzMan.on('currenttz', this.handleTZSet, this);
        this.tzMan.show();
    }, 

    getPageData : function () {
        this.doc.body = Ext.get(document.body);
        this.pbar = Ext.Msg.progress('', 'Loading...');

        var task = new Rack.app.maintcal.schedule.getMaintInfo(this, this.doc);
        task.start();
    },

    updatePageDataProgress: function (percent) {
        if (this.pbar) {
            this.pbar.updateProgress(percent);
        }
    },

    handleExpedite : function () {
        if (!this.options.expediteHasFired) {
            Ext.MessageBox.alert('WARNING', this.moreDevicesWarning);
            this.options.expediteHasFired = true;
        }
        this.recalculateAvailableTimes();
    },

    handleExtendTime : function () {
        this.recalculateAvailableTimes();
    },

    handleWidgetsReady : function () {
        this.setTimeFormat();
        this.serviceTypes = new Rack.app.maintcal.serviceTypesView(this.doc.serviceTypes);
       
        this.devices = new Rack.app.maintcal.devicesView(this.doc.devices);
        this.options = new Rack.app.maintcal.optionsView(this.doc.options);
        this.calendar_overrides = new Rack.app.maintcal.overridesView(this.doc.overrides,this);
        this.header = new Rack.app.maintcal.headingView({
            region: 'north',
            height: 80,
            border: false,
            collapsible: false,
            baseCls: 'mc-heading'
        });
        this.westPanel = new Ext.Panel({
                region: 'west',
                width: 300,
                collapsible: false,
                margins: '5 5 5 5',
                border: false,
                bodyStyle: 'background-color:transparent;',
                layout: 'accordion',
                layoutConfig: {animate: true, autoWidth: false},
                items: [this.serviceTypes, 
                        this.devices, 
                        this.options,
                        this.calendar_overrides
                        ]
            });
        this.centerPanel = new Ext.Panel({
                region: 'center',
                items: this.calendar
            });
        this.header.pageTitle.setText(this.title);
        this.setHeadingTZName(this.currentTZ);
        this.header.tzChangeButton.setTitle("Current Timezone: " + 
                decodeURIComponent(this.currentTZ.replace(/_/g,' ')) + ". Click to Change");
        this.header.ticketNumber.setText("Ticket #: " + 
                this.renderTicketURL(this.doc.ticket_url));
        this.header.accountInfo.setText(this.doc.account_name + 
                    ' (' + this.renderAccountURL(this.doc.account_url) + ')');
        this.pbar.hide();
        // lay everything out.
        this.layout = new Ext.Viewport({
                layout: 'border',
                width: 915,
                height: 555,
                items: [this.header, this.westPanel, this.centerPanel]                
        });
        Ext.QuickTips.init();
        //add Business Logic listeners
        // listen for changes on any of the maintenance values objects
        // this.serviceTypes, this.devices,this.options and mask calendar if they
        // change from the original values.
        this.devices.gridSelectionModel.on('rowselect', this.handleCollectData, this);
        this.devices.gridSelectionModel.on('rowdeselect', this.handleCollectData, this);
        this.calendar_overrides.gridSelectionModel.on('rowselect', this.overridesChangeListener, this);
        this.calendar_overrides.gridSelectionModel.on('rowdeselect', this.overridesChangeListener, this);
        this.options.on('optionschange', this.handleCollectData, this);
        // only enable button after the schedule has a service type selected.
        this.serviceTypes.on('rowclick', this.handleCollectData, this);
        // process the selected devices and service type and get available times.
        this.header.updateAvailableButton.on('click', this.sendMaintenanceData, this);
        // listen for month changes on the calendar
        this.calendar.on('monthchange', this.calendarChange, this);
        // listen for available time selected.
        this.calendar.on('availableselected', this.scheduleTentative, this);
        // listen for Timezone changes from the calendar.
        this.calendar.on('tzselect', this.handleUserTZSelection, this);
        // disable button until a service type has been selected.
        this.header.updateAvailableButton.disable();
        // mask calendar until a call to recalculateAvailableTimes has been made.
        this.centerPanel.body.mask();
        // create a segment regular expression to and apply a filter to service
        // types based on it.
        this.createSegmentRE();
        // apply event listener for the change Timezone button.
        var headerEl = this.header.getEl();
        var tzButton = headerEl.select('button.mc-tz-change-button-schedule');
        tzButton.on('click', this.handleTZChangeRequest, this);
        // apply event listener for help clicks
        //var helpButton = headerEl.select('button.mc-help');
        //helpButton.on('click', this.showHelp, this);
        // update the clock with appropriate TZ offset
        this.handleTZSelection(this.currentTZ);

        //  Setting the Service Types View Panel Header Tooltips

        this.servTypeView_el = Ext.get('serviceTypesView_id');
        Ext.get(this.servTypeView_el.dom.firstChild.firstChild.firstChild.firstChild.firstChild).set({qtip:'Click to Expand/Collapse Service Types'});

        //Setting deviceView Panel Header Tooltips
        this.deviceView_el = Ext.get('deviceView_id');
        Ext.get(this.deviceView_el.dom.firstChild.firstChild.firstChild.firstChild.firstChild).set({qtip:'Click to Expand/Collapse Device List'});
        //Setting overridesView Panel Header Tooltips
        this.overridesView_el = Ext.get('overridesView_id');
        Ext.get(this.overridesView_el.dom.firstChild.firstChild.firstChild.firstChild.firstChild).set({qtip:'Click to Expand/Collapse Calendar List'});
        //Setting optionsView Panel objects Tooltips
        Ext.get('expediteCheckBox_id').set({qtip:'Check this box to eliminate lead time'});
        Ext.get('extendTimesComboBox_id').set({qtip:'Click to amount choose time to extend maintenance by'});
    },

    handleCollectData : function () {
        // collect data.
        var serviceTypesSM = this.serviceTypes.getSelectionModel();
        // used by the tentative maintenance dialog to gather data.
        this.selectedServiceTypeRecord = serviceTypesSM.getSelected();
        if (!this.selectedServiceTypeRecord) {
            return false
        }
        else {
            this.selectedServiceType = this.selectedServiceTypeRecord.json.id;
        }
        var selectedDeviceRecords = this.devices.gridSelectionModel.getSelections();
        var sdr;
        this.selectedDevices = [];
        for (sdr = 0; sdr < selectedDeviceRecords.length; sdr++) {
            this.selectedDevices.push(selectedDeviceRecords[sdr].json.id);
        }
        if (this.header.updateAvailableButton.disabled) {
            this.header.updateAvailableButton.enable();
        }
        if (!this.centerPanel.body.isMasked()) {
            Ext.WindowMgr.each(function (w) { 
                if (w.initialConfig.cls === 'mc-avail-window') {
                    w.destroy();
                }
            });
            this.centerPanel.body.mask();
        }

    },

    overridesChangeListener : function () {
        if (this.header.updateAvailableButton.disabled) {
            this.header.updateAvailableButton.enable();
        }
        if (!this.centerPanel.body.isMasked()) {
            Ext.WindowMgr.each(function (w) { 
                if (w.initialConfig.cls === 'mc-avail-window') {
                    w.destroy();
                }
            });
            this.centerPanel.body.mask();
        }
    },

    sendMaintenanceData : function () {
        if (!this.selectedServiceType) {
            Ext.MessageBox.alert('ALERT', "You must select at least one Service Type");
            return false;
        }
        if (!this.selectedDevices) {
            Ext.MessageBox.alert('ALERT', "You must select at least one device to include in the maintenance");
            return false;
        }
        if (this.calendar_overrides.hasBeenExpanded && this.calendar_overrides.getSelecteds().length === 0) {
            Ext.MessageBox.alert('ALERT', "You must select at least one calendar");
            return false;
        }
        this.createMaintenanceTask = new Rack.app.maintcal.schedule.createMaintenance(this, this.doc);
        this.createMaintenanceTask.start();
    },
    calendarChange : function () {
        var task = new Rack.app.maintcal.schedule.createMaintenance(this, this.doc);
        task.start();
    },

    /**
    *  Update the calendar with the results of a times_available query.
    */
    updateCalendar : function (response) {
        var json = response.responseText;
        var results = eval("(" + json + ")");

        if (!results) {
            throw "updateCalendar: Json object not found";
        }

        if (!results.calendars) {
            this.showDataError(this, response);
        }

        this.calendar.setAvailableTime(results);

        if (this.centerPanel.body.isMasked()) {
            this.centerPanel.body.unmask();
        }
    },

    setHeadingTZName : function (tzname) {
        if (tzname) {
            this.header.pageTitle.setText(this.title + ' (' + 
                        decodeURIComponent(tzname) + ') ');
        }
        else {  
            var currentDate = new Date();
            this.header.pageTitle.setText(this.title + ' ( Unknown Zone ) ');
        }
    },

    renderAccountURL : function (acct_url) {
        var twoPart = acct_url.split('?account_number=');
        if (twoPart.length === 2) {
            return '<a href="javascript:loadParent(' + "'" + acct_url + "'" + 
                ',0,1)">' + twoPart[1] + '</a>';
        }
        else {
            return 'Not Available';
        }
    },

    createSegmentRE : function () {
        var segmentArray = [];
        this.devices.doc.each(function (r) {
            if (segmentArray.indexOf(r.json.segment) !== -1) {
            }
            else {
                segmentArray.push(r.json.segment);
            }
        });
        var segmentString = segmentArray.toString();
        var segmentRE = new RegExp();
    },
    handleFocusDevices : function () {
        if (this.devices.collapsed) {
            this.devices.expand(false);
        }
        if (!this.serviceTypes.collapsed) {
            this.serviceTypes.collapse(false);
        }
        if (!this.options.collapsed) {
            this.options.collapse(false);
        }
    },
    renderTicketURL : function (tkct_url) {
        var twoPart = tkct_url.split('?ref_no=');
        if (twoPart.length === 2) {
            return '<a href="javascript:loadParent(' + "'" + tkct_url + "'" +  
                ',0,1)">' + twoPart[1] + '</a>';
        } else {
            return 'Not Available';
        }
    },

    setTimeFormat : function () {
        this.timeFormat = "G:i"; // 24 hour display
        var tdate = new Date();
        var localOffset = tdate.getTimezoneOffset() / 60;
        if (localOffset <= 8 || localOffset >= 4) {
            this.timeFormat = "g:i A"; // US-style AM/PM 12 hour display.
        }
    },

    handleTZSelection : function (tzname) {
        var tztask = new Rack.app.maintcal.schedule.changeTZ(this, this.doc);
        tztask.start(tzname);
    },

    handleUserTZSelection : function (tzname) {
        var usertztask = new Rack.app.maintcal.schedule.userChangeTZ(this, this.doc);
        usertztask.start(tzname);
    },

    /**
    *  Handle when an available time is selected on bigcal.
    */
    scheduleTentative : function (recordSelected) {
        if (!this.centerPanel.body.isMasked()) {
            //atwGroup is the name of the Available Time's window group
            atwGroup.each(function (w) { 
                if (w.initialConfig.cls === 'mc-avail-window') {
                    w.destroy();
                }
            });
            this.centerPanel.body.mask();
        }
        var tentative = new Rack.app.maintcal.tentativeDialog(this, recordSelected);
        tentative.updateOptionsPanel();
        tentative.show();
    },

    destroy: function () {
        this.layout.destroy();
    },

    showDataError : function (r) {
        Ext.getBody().unmask();
        var msgResponse = this.genericDataErrorText;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText !== 'undefined') {
                msgResponse = parseWSGIError(r.responseText);
            }
            
        }        
        Ext.MessageBox.show({
            title: 'Alert',
            msg: msgResponse,
            fn: globalCloseWindow,
            buttons: Ext.MessageBox.OK,
            width: 250
        });        
    },

    setPageTitle : function (ticket_ref_no) {
        if (!ticket_ref_no) {
            document.title = "Maintenance Calendar: Scheduling Maintenance for Unknown";
        } else {
            document.title = "Maintenance Calendar: Scheduling Maintenance for " +
                ticket_ref_no;
        }
    },

    showHelp : function () {
        if (! this.helpWindow) {
            this.helpWindow = window.open('/maintcal/shared/help.htm#maintenance_view');
        }
    }   
});

