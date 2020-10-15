/**
*   This class represents the main view window for the 
*   calendar_view application.
*/

Ext.namespace("Rack.app.maintcal.calendarView");

Rack.app.maintcal.calendarView = function (doc) {
    this.doc = doc;

    this.addEvents({
        dataerror: true
    });

    this.tzMan = new Rack.app.maintcal.tzManager({
        initialLoad: true
    });

    this.tzMan.on("currenttz",  this.handleTZSet, this);
    this.doc.on("load",         this.handleWidgetsReady, this);
    this.doc.on("dataerror",    this.showDataError, this);

    Ext.onReady(this.getCurrentTZ, this);
};

Ext.extend(Rack.app.maintcal.calendarView, Ext.util.Observable, {
    genericDataErrorText: "There has been an undefined error. Please try again.",

    getCurrentTZ: function () {
        /*
        if (!UASCheck()) {
            // run a check of user agent check for Firefox2.x or IE
            return false;
        }
        */
        this.currentTZ = this.tzMan.check();
        if (!this.currentTZ) {
            this.tzMan.show();
        } else {
            this.getPageData();
        }
    },

    handleTZSet: function (tz_val, initial_load) {
        this.currentTZ = tz_val;
        if (initial_load) {
            this.getPageData();
        } else {
            ReloadWindow();
            this.runCalendarTasks();
        }
    },

    handleTZChangeRequest: function () {
        this.tzMan = new Rack.app.maintcal.tzManager({
            initialLoad: false
        });
         // event listeners.
        this.tzMan.on("currenttz", this.handleTZSet, this);
        this.tzMan.show();
    }, 

    getPageData: function () {
        this.doc.body = Ext.get(document.body);
        this.doc.body.mask("Loading ...");
        var task = new Rack.app.maintcal.calendar.getCalendars(this, this.doc);
        task.start();
    },

    switchCalendarView: function (obj, selected) {
        if (!selected) {
            return;
        }
        var newView = obj.inputValue;
        if (newView === "month") {
            this.centerPanel.layout.setActiveItem(0);
            this.monthView.fireEvent("activate");
        } else if (newView === "list") {
            this.centerPanel.layout.setActiveItem(1);
            this.listView.fireEvent("activate");
        }
    },

    // begin private method collection resulting from major refactoring
    createChangeTZButton: function () {
        this.changeTZButton = new Rack.app.maintcal.Label({
            tag: "button",
            cls: "mc-tz-change-button",
            enableClick: true,
            html: "Change TZ",
            title: "Current Timezone: " + decodeURIComponent(this.currentTZ.replace(/_/g,' ')) +
                ". Click to Change."
        });
        this.changeTZButton.on("click", this.handleTZChangeRequest, this);
    },

    createViewSelectorMonthButton: function () {
        this.monthButton = new Ext.form.Radio({
            boxLabel: "Month View",
            inputValue: "month",
            checked: true
        });
        this.monthButton.on("check",this.switchCalendarView,this);
    },

    createViewSelectorListButton: function () {
        this.listButton = new Ext.form.Radio({
            boxLabel: "List View",
            inputValue: "list"
        });
        this.listButton.on("check",this.switchCalendarView,this);
    },

    createCalendarViewSelector: function () {
        this.createViewSelectorMonthButton();
        this.createViewSelectorListButton();
        this.calendarViewSelector = new Ext.Panel({
            border: false,
            cls: "mc-calendar-view-selector",
            defaults: {
                hideLabel: true,
                labelSeparator: "",
                name: "view-selector-option"
            },
            items: [this.monthButton,this.listButton]
        });

    },

    createButtonContainer: function () {
        this.createCalendarViewSelector();    
        this.createChangeTZButton();
        this.buttonContainer = new Ext.Container({
            autoEl: "div",
            cls: "mc-button-container",
            autoHeight: true,
            items: [this.calendarViewSelector, this.changeTZButton]
        });
    },

    createCalendarSelector: function() {
        this.calendarSelector = new Ext.form.ComboBox({
            store: this.doc,
            emptyText: "Select a Calendar",
            mode: "local",
            displayField: "name",
            valueField: "id",
            listWidth: 200,
            triggerAction: "all",
            forceSelection: true,
            editable: false
        });
        this.calendarSelector.on("select", this.loadCurrentCalendar, this);
    },

    createCalendarSelectorContainer: function () {
        this.createCalendarSelector();
        this.selectorContainer = new Ext.Container({
            autoEl: "div",
            cls: "mc-selector-container",
            /*layout: "fit", */
            width: 788,
            items: [this.calendarTitle, this.calendarSelector]
        });
    },

    createHeader: function () {
        this.calendarTitle = new Rack.app.maintcal.Label({html:"Maintenance Calendar for"});
        this.createButtonContainer();
        this.createCalendarSelectorContainer();
        this.header = new Ext.Panel({
            region: "north",
            height: 100,
            border: false,
            collapsible: false,
            cls: "mc-heading",
            layout: "column",
            items: [this.selectorContainer, this.buttonContainer]
        });
    },

    buildMonthView: function () {
        this.monthView = new Rack.app.maintcal.MonthView(this, {
            timeFormat: this.timeFormat
        });

        this.monthCalendar = this.monthView.calendar;
        // listen to month change events from the calendar and handle them.
        this.monthCalendar.on("monthchange", this.updateCalendarView, this);
        // listen to selection events and handle them for when the user switches calendars
        this.monthCalendar.on("select", this.updateTickets, this);
        // listen for activate events to update the filters on the ticket view
        this.monthView.on("activate", this.monthView.onActivate, this.monthView);
    },

    buildListView: function () {
        this.listView = new Rack.app.maintcal.ListView(this);
        this.listView.fillListTask = this.fillListTask;
        this.listView.on("activate", this.listView.onActivate, this.listView);
    },

    createCenterPanel: function () {
        this.buildMonthView();
        this.buildListView();
        this.ticketView = this.monthView.ticketView;
        this.ticketView.on("ticketstatechange", this.handleTicketStateChange, this);
        this.centerPanel = new Ext.Panel({
            region: "center",
            layout: "card",
            items: [this.monthView, this.listView],
            activeItem: 1
        });
    },

    createViewPort: function () {
        this.createHeader();
        this.createCenterPanel();
        // create the outer viewport (container of everything else)
        this.viewPort = new Ext.Viewport({
            layout: "border",
            items: [this.header, this.centerPanel]
        });
        // alias this.layout to something less overloaded
        // TODO: reassign all refs from this.layout to this.viewPort
        //this.viewPort = this.layout;
    },

    getAdminStatus: function () {
        if (this.calendarSelector.currentRecord && 
            this.calendarSelector.currentRecord.get("is_admin")) {
            return true;
        }
        return false;
    },
    getToday: function () {
        var today = new Date().clearTime();
        var year = today.getFullYear();
        var month = today.getMonth() + 1;
        var day = today.getDate();
        return {"year": year, "month": month, "day": day};
    },
    setDefaultCalId: function () {
        var isAdmin = this.getAdminStatus();
        var today = this.getToday();
        var initialDC = getURLParam("datacenter");
        if (initialDC) {
            this.setCurrentCalId("tckt_queue_id", parseInt(initialDC, 10));
        } else {
            // load today's tickets
            this.ticketView.fireEvent("loadtickets", 
                today.year,
                today.month, 
                today.day,
                this.getCurrentCalId(),
                this.currentTZ,
                isAdmin);
        }
    },
    setDefaultRefreshInterval: function () {
        this.currentInterval = setInterval(
            this.refreshViews.createDelegate(this, []), 600000
        );
    },

    handleWidgetsReady: function () {
        // This method is where we assemble the viewport (all visuals)

        // This task refreshes the local store with data from the servier
        // This is called by an event in the code below in this method
        // TODO: Refactor to avoid side effects
        this.fillCalendarsTask = new Rack.app.maintcal.calendar.fillCalendars(
            this, this.doc);
        this.fillListTask = new Rack.app.maintcal.calendar.fillList(
            this, this.doc.tickets);

        this.setTimeFormat();
        this.createViewPort();
        Ext.QuickTips.init();
        this.setDefaultRefreshInterval();
        this.setDefaultCalId();
        this.setPageTitle();
        this.doc.body.unmask();  
    },

    syncCalendar: function(dt) {
        var modDate = dt.clearTime();
        this.monthCalendar.update(modDate);
        this.monthCalendar.setValue(modDate);
    },

    loadCurrentCalendar: function (c, record, i) {
        if (!record.data.id) {
            // skip loading calendar data for a blank.
            return;
        } 
        this.calendarSelector.currentRecord = record;
        this.calendarName = record.data.name;
        this.runCalendarTasks();
    },

    runCalendarTasks: function() {
        var currentCalID = this.getCurrentCalId();
        this.fillListTask.start(this.monthCalendar.activeDate.getFullYear(),
            this.monthCalendar.activeDate.getMonth() + 1, 
            currentCalID, 
            this.currentTZ,
            this.ticketView.showHideMenu.current_selections);
        this.fillCalendarsTask.start(this.monthCalendar.activeDate.getFullYear(),
            this.monthCalendar.activeDate.getMonth() + 1, 
            currentCalID, 
            this.currentTZ,
            this.ticketView.showHideMenu.current_selections);
        // reload the ticketView
        var today = this.getToday();
        // load today's tickets
        this.ticketView.fireEvent("loadtickets",
            today.year,
            today.month,
            today.day,
            currentCalID,
            this.currentTZ,
            this.calendarSelector.currentRecord.get("is_admin")
        );

        this.setPageTitle(this.calendarName);
    },

    updateTickets: function (s, selectedDay) {
        // remember that the select returns the localtime date
        // and that .format("U") returns seconds since epoch in localtime.
        this.selectedDay = selectedDay;
        // load tickets for selected day
        this.ticketView.fireEvent("loadtickets",
            selectedDay.getFullYear(),
            selectedDay.getMonth() + 1,
            selectedDay.getDate(),
            this.getCurrentCalId(),
            this.currentTZ,
            this.calendarSelector.currentRecord.get("is_admin")
        );
    },

    updateCalendarView: function () {
        this.fillCalendarsTask.start(
            this.monthCalendar.activeDate.getFullYear(),
            this.monthCalendar.activeDate.getMonth() + 1,
            this.getCurrentCalId(),
            this.currentTZ,
            this.ticketView.showHideMenu.current_selections
        );
    },

    handleTicketStateChange: function () {
        this.updateCalendarView();
        this.updateTickets(this, this.ticketView.currentStartTime.clearTime());
    },

    // Not sure if this will do what I want
    getCurrentCalName: function() {
        return this.calendarSelector.getRawValue();
    },

    // This WILL need to be changed ... load calendar Selector first.
    getCurrentCalId: function () {
        if (this.calendarSelector && this.calendarSelector.getValue &&
                this.calendarSelector.getValue()) {
            return this.calendarSelector.getValue();
        } else {
            // return a zero to get an invalid calendar selection.
            return 0;
        }
    },

    setCurrentCalId: function (target_record_value, new_val) {
        this.doc.each(function (r) {
            if (r.get(target_record_value) === new_val) {
                this.calendarSelector.setValue(r.get("id"));
                this.calendarSelector.fireEvent("select",
                    this.calendarSelector, r);
                return false;
            }
        }, this);
    },

    setTimeFormat: function () {
        this.timeFormat = "G:i"; // 24 hour display
        var tdate = new Date();
        var localOffset = tdate.getTimezoneOffset() / 60;
        if (localOffset <= 8 || localOffset >= 4) {
            this.timeFormat = "g:i A"; // US-style AM/PM 12 hour display.
        }
    },

    showDataError: function (r) {
        var msgResponse;
        if (typeof r === "string") {
            msgResponse = r;
        } else {
            if (typeof r.responseText === "undefined") {
                msgResponse = this.genericDataErrorText;
            } else {
                msgResponse = parseWSGIError(r.responseText);
            }
        }
        if (this.doc.body.isMasked()){
            this.doc.body.unmask();
        }
        Ext.MessageBox.show({
                title: "Alert",
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    },

    setPageTitle: function(cal) {
        if (cal) {
            document.title = "Maintenance Calendar: Calendar View for - " + cal;
        } else {
           document.title = "Maintenance Calendar: Calendar View";
        } 
    },

    addTickets: function() {
        // This is called by the onLoad handler for the ticket store.
        // Pass the call on to the ticketView.
        this.ticketView.addTickets();
    },

    refreshViews: function() {
        if (this.ticketView.body.isMasked() || 
            this.centerPanel.body.isMasked()) {
            clearInterval(this.currentInterval);
            this.currentInterval = setInterval(
                this.refreshViews.createDelegate(this, []), 600000
            );
        } else {
            var currentSelectorRecord = false;
            if (this.calendarSelector.currentRecord) {
                currentSelectorRecord = this.calendarSelector.currentRecord.get("is_admin");
            }
            this.updateCalendarView();
            this.fillListTask.restart();
            this.ticketView.fireEvent("loadtickets",
                // load tickets by ticket views currently selected time
                this.ticketView.currentStartTime.getFullYear(),
                this.ticketView.currentStartTime.getMonth() + 1,
                this.ticketView.currentStartTime.getDate(),
                this.getCurrentCalId(),
                this.currentTZ,
                currentSelectorRecord);
        }
    },

    showHelp: function () {
        this.helpWindow = window.open("/maintcal/shared/help.htm#calendar_view");
    }
});

