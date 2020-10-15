/**
*  This is the top-level container for everything in the admin ui.
*/
/*extern Ext, Rack, parseWSGIError, globalCloseWindow */

Rack.app.maintcal.adminConsole.View = function(config) {
    // some default error message
    var defaultErrorMessage = "There has been an undefined error.";

    // add data events
    this.addEvents({
        calendarsloaded : true,
        calendarloaded : true,
        contentready : true
    });

    this.document_body = Ext.getBody();
    this.doc = config.doc;

    this.west = new Rack.app.maintcal.consoleNavigator({ 
        view: this,
        doc: config.doc
    });

    this.center = new Rack.app.maintcal.adminConsole.Center(); 
    this.south = new Rack.app.maintcal.consoleTools(); 

    // The three tasks
    this.loadcalendarsTask = new Rack.app.maintcal.adminConsole.loadCalendars(this,config.doc);
    this.loadQueueDataTask = new Rack.app.maintcal.adminConsole.loadQueueData(this,config.doc);
    // This was being initialized for use in doAsyncLoad. No longer needed.
    //this.loadCalendarDataTask = new Rack.app.maintcal.adminConsole.loadCalendarData(this,config.doc);

    this.on('calendarsloaded',this.document_body.unmask,this.document_body);
    this.on('contentready',this.focusCalendarContent,this);
    Ext.util.Observable.call(this,config);
    Ext.onReady(this.startApp,this);
};

Ext.extend(Rack.app.maintcal.adminConsole.View,Ext.util.Observable,{
    startApp : function() {
        this.document_body.mask('Loading ...');
        Ext.QuickTips.init();
        this.loadcalendarsTask.start();
        // general tab is being disabled so don't perform this task.
        // adminV3 addition.
        this.loadQueueDataTask.start();
    },

    makeViewPort : function () {
        this.vport= new Ext.Viewport({
            layout : 'border',
            style: 'margin: 0 0 0 5',
            items : [this.west,this.south,this.center]
        });
    },

    /* This "feature" is probably unnecessary as loads of async data 
    TIcket Queue Categories and Statuses appear to be "fast" enough.
    doAsyncLoad : function() {
        // this method is called on successfully loading calendars, unmask.
        this.document_body.unmask();
        // This is used to load calendar data, not needed right now.
        var last_cal_id = this.checkLastSelected();
        var cal_data_to_load = this.doc.calendarData;
        while (cal_data_to_load.length > 0) {
            if (last_cal_id) {
                // start with this calendar
                this.loadCalendarDataTask.start(last_cal_id);
                cal_data_to_load.splice(
                    cal_data_to_load.indexOf(last_cal_id),1);
            }

            var cal_to_load = cal_data_to_load.pop();
            this.loadCalendarDataTask.start(cal_to_load.id);
        }
    },
    // This method is only being called by doAsyncLoad which is being
    // disabled.
    checkLastSelected : function() {
        // checks for user's last selected action and loads that data first.
        var last_action = Rack.readCookie(this.console_last_action_key);
        if (!last_action) {
            return false;
        } else {
            // ensure the cookie value is still a valid calendar id
            var c;
            for (c=0;c < this.doc.calendarData.length; c++) {
                // the irony of this loop counter is not lost on me.
                if (last_action == this.doc.calendarData[c].id) {
                    return last_action;
                }
            }
            return false;
        } 
    }, 
    */
    generalDataLoad : function (cal_id_str) {
        var cal_id = parseInt(cal_id_str,10);
        if (typeof cal_id === "number" && !isNaN(cal_id)) {
            this.center.createContentManager(cal_id,this.doc.calendarData[cal_id]);
        }
        else {
            throw "Invalid Calendar id";
        }
       
    },

    focusCalendarContent : function(cal_id) {
        this.center.layout.setActiveItem(cal_id);
    },
    
    handleDataError : function(r,o) {

        var error_config = {
            title: 'Alert',
            buttons: Ext.MessageBox.OK,
            width: 250
        };

        var msgResponse = this.errorText;
        if (typeof r === "string") {
            error_config.msg = r;
        } else {
            if (r.status === 500 || r.status === 403) {
                error_config.msg = parseWSGIError(r.responseText);
                error_config.fn = globalCloseWindow;
            }
            if (typeof r.responseText !== 'undefined') {
                error_config.msg = parseWSGIError(r.responseText);
            } else {
                error_config.msg = "An Unhandled error occurred.";
                error_config.fn = globalCloseWindow;
            }
        }
        Ext.MessageBox.show(error_config);
    },

    setCalendarData : function(a) {
        var j;
        var cal_ids = [];
        var unique_requested_ids = {};
        for (j=0; j < a.length; j++) {
            this.doc.calendarData[a[j].id] = a[j];
            cal_ids.push(a[j].id);
            // calendar data has specific categories or statuses,
            // get them.
            if (a[j].new_ticket_category_id && 
                a[j].new_ticket_category_id !== 0) {
                this.doc.catLoadTask.start(a[j].new_ticket_queue_id);
            }
            if (a[j].refresh_category_id &&
                a[j].refresh_category_id !== 0) {
                this.doc.catLoadTask.start(a[j].refresh_ticket_queue_id);
            }
            if (a[j].new_ticket_status_id &&
                a[j].new_ticket_status_id !== 0) {
                this.doc.statLoadTask.start(a[j].new_ticket_queue_id);
            }
            if (a[j].refresh_status_id &&
                a[j].refresh_status_id !== 0) {
                this.doc.statLoadTask.start(a[j].refresh_status_id);
            }
            // only make call to fetch category and status data if it
            // hasn't already been fetched or isn't duplicated.
            var new_queue_int = parseInt(a[j].new_ticket_queue_id,10);
            var tckt_queue_int = parseInt(a[j].tckt_queue_id,10);
            var refresh_queue_int = parseInt(a[j].refresh_ticket_queue_id,10);
            if (typeof new_queue_int === "number" && 
                !isNaN(new_queue_int)) {
                unique_requested_ids[new_queue_int] = true;
            }
            if (typeof tckt_queue_int === "number" &&
                !isNaN(tckt_queue_int)) {
                unique_requested_ids[tckt_queue_int] = true;
            }
            if (typeof refresh_queue_int === "number" &&
                !isNaN(refresh_queue_int)) {
                unique_requested_ids[refresh_queue_int] = true;
            }
        }
        // retreive subcategory and status data.
        var i;
        for (i in unique_requested_ids) {
            if (! unique_requested_ids.hasOwnProperty(i)) {
                continue;
            }
            // a queue_id coming from this calendar does not have 
            // its subcategory data cached. make the call.
            if (!this.doc.subCatData.hasOwnProperty(i)) {
                this.doc.catLoadTask.start(parseInt(i,10));
            }
            // a queue_id coming from this calendar does not have
            // its status data cached. make the call.
            if (!this.doc.statusData.hasOwnProperty(i)) {
                this.doc.statLoadTask.start(parseInt(i,10));
            }
        }
        if (cal_ids.length === 1) {
            this.doc.fireEvent('calendarloaded',cal_ids[0]);
        } else {
            this.doc.fireEvent('calendarloaded',cal_ids);
        }
    }
});


