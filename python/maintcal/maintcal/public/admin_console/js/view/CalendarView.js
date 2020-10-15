/*extern Ext, Rack */

/* CalendarView the main window for the calendar*/

Ext.namespace('Rack.app.maintcal.CalendarView');

// Constants used by various components for sizing and layout
Rack.app.maintcal.DAY_MINUTES = 24 * 60;
Rack.app.maintcal.GRANULARITY = 30;
Rack.app.maintcal.TOTAL_QUANTA = Rack.app.maintcal.DAY_MINUTES / Rack.app.maintcal.GRANULARITY;
Rack.app.maintcal.PIXELS_PER_QUANTA = 20;
Rack.app.maintcal.TITLE_HEIGHT = 27; // For Firefox 3.5 may be different for other browsers
Rack.app.maintcal.STARTING_DAY_OF_WEEK = 1;   // Monday

Rack.app.maintcal.Clipboard = null;

Rack.app.maintcal.CalendarView = function(config) {
    this.connection = new Ext.data.Connection({timeout: 60000});
    
    // do an initial setsize
    this.do_setSize = false;
    
    var default_config = {
        autoScroll: true,
        layout: 'fit',
        buttonAlign: "right",
        buttons: [
            {
                xtype: "button",
                text: "Save",
                disabled : config.disableCalendar,
                handler: this.saveHandler,
                scope: this
            }
        ]
    };
    Ext.apply(this, config, default_config);
    Ext.Panel.call(this);
    this.calenderId = config.calendarId;
    // bind the resizing events
    this.on('resize',this.sizePerParent,this);
    //this.on('render',this.sizePerParent,this);
    this.on('beforeshow',this.handleShown,this); 
    // probably need to remove this.
    //this.on('deactivate',this.checkIsDirty,this);
    // creating an exceptions calendar instead of of available defaults calendar.
    if (config.calendarMode && config.calendarMode === 'exceptions') {
        // bind these tasks to the global_doc so they can be started from the global doc by events bound to this
        // object. actually don't do this, pass references around to the parent widgets instead.
        // figure out the correct start of the week we are currently on.
         // Need to move the start date to fall on the designated
        // starting day of the week.
        var now = new Date(); // this should probably be gotten from the server, not the client. 
        var dow = now.format("w"); //returns DOW
        var offset = -1 * (dow - Rack.app.maintcal.STARTING_DAY_OF_WEEK);
        this.start_dt = now.add(Date.DAY, offset);
        this.end_dt = this.start_dt.add(Date.DAY,6);
        this.loadExceptionsTask = new Rack.app.maintcal.adminConsole.loadAvailableExceptions(this);
        this.loadExceptionsTask.start(this.calendarId,this.start_dt,this.end_dt);
    } else {
        this.loadDefaultsTask = new Rack.app.maintcal.adminConsole.loadAvailableDefaults(this);
        this.loadDefaultsTask.start(this.calendarId);
    }

};

Ext.extend(Rack.app.maintcal.CalendarView, Ext.Panel,{
    /**
    *  This is called with the results of the ajax call to load
    *  the available defaults data.
    */
    loadAvailableDefaults: function(data) {
        this.viewBody = new Rack.app.maintcal.ViewBody({data : data, disableView : this.disableCalendar});
        this.add(this.viewBody);
        this.doLayout();
    },

    savedAvailableDefaults : function(data) {
       this.remove(this.viewBody);
       this.viewBody = new Rack.app.maintcal.ViewBody({data : data, disableView : this.disableCalendar});
       this.add(this.viewBody);
       this.doLayout();
       this.unMask();  
    },

    unMask : function() {
        if (this.el.isMasked()) {
            this.el.unmask();
        }
    },

    handleShown : function() {
        // also as per David Schrader reset the start time back to the default.
        if(this.calendarMode === 'exceptions') {
            this.navigate('now');
        }
    },

    sizePerParent : function() {
        var parentSz = this.ownerCt.getSize();
        if (this.do_setSize) {
            this.do_setSize = false;
            this.setSize(parentSz.width,parentSz.height - Rack.app.maintcal.TITLE_HEIGHT);
        }
    },

    //private ( ahhh HAHAHHAHA !!!)
    doInitialLoad : function(data) {
        this.viewBody = new Rack.app.maintcal.ViewBody({
            navigationParent : this,
            data : data,
            disableView : this.disableCalendar,
            startdate : this.start_dt,
            calendarMode : 'exception',
            navigation : true
        });
        this.add(this.viewBody);
    },

    //private ( ahhh HAHAHHAHA !!!)
    doPostLoad : function(data) {
        this.remove(this.viewBody);
        this.viewBody = new Rack.app.maintcal.ViewBody({
            navigationParent : this,
            data : data,
            disableView : this.disableCalendar,
            startdate : this.start_dt,
            calendarMode : 'exception',
            navigation : true
        });
        this.add(this.viewBody);
        this.doLayout();
        this.unMask();  
    },

    loadAvailableExceptions : function(data) {
        if(this.viewBody && this.viewBody.rendered) {
            this.doPostLoad(data);
        }
        else {
            this.doInitialLoad(data);
        }
    },

    getCalendarData: function() {
        // Returns the data for the current calendar
        return this.viewBody.getCalendarData();
    },

    saveHandler: function() {
        var data = this.getCalendarData();

        // explicity trap for the two valid calendarModes
        if(this.calendarMode === 'default') {
            this.saveDefaultsTask = new Rack.app.maintcal.adminConsole.saveAvailableDefaults(this);
            this.saveDefaultsTask.start(this.calendarId, data);
        } else if(this.calendarMode === 'exceptions') {
            this.saveExceptionsTask = new Rack.app.maintcal.adminConsole.saveAvailableExceptions(this);
            this.saveExceptionsTask.start(this.calendarId, data);
        }
    },

    markClean : function() {
        this.viewBody.dayContainer.dirty = false;
    },

    promptedSaveHandler : function(btn) {
        if (btn === 'yes') {
            this.saveHandler();
            return
        }
        this.markClean();
        this._okToNavigate();
    },

    checkIsDirty : function() {
        if (this.viewBody.dayContainer.dirty) {
            Ext.Msg.show({
                title: 'Save Changes?',
                msg: 'Your calendar has unsaved changes. Would you like to save your changes?',
                buttons: Ext.Msg.YESNO,
                fn: this.promptedSaveHandler,
                scope: this,
                icon: Ext.MessageBox.QUESTION
            });
        } else {
            this._okToNavigate();
        }
    },

    navigate : function(nav_direction) {
        this.nav_direction = nav_direction;
        this.checkIsDirty();
    },

    _okToNavigate: function() {
        if(this.nav_direction === 'forward') {
            this.start_dt = this.end_dt.add(Date.DAY,1);
            this.end_dt = this.start_dt.add(Date.DAY,6);
            this.loadExceptionsTask.start(this.calendarId,this.start_dt,this.end_dt);
        }
        if(this.nav_direction === 'back') {
            this.end_dt = this.start_dt.add(Date.DAY,-1);
            this.start_dt = this.start_dt.add(Date.DAY,-7);
            this.loadExceptionsTask.start(this.calendarId,this.start_dt,this.end_dt);
        }
        if(this.nav_direction === 'now') {
            // Need to move the start date to fall on the designated
            // starting day of the week.
            var js_now = new Date();
            var dow = js_now.format("w"); //returns DOW
            var offset = -1 * (dow - Rack.app.maintcal.STARTING_DAY_OF_WEEK);
            this.start_dt = js_now.add(Date.DAY, offset);
            this.end_dt = this.start_dt.add(Date.DAY,6);
            this.loadExceptionsTask.start(this.calendarId,this.start_dt,this.end_dt);

        }
        this.nav_direction = null;
    }
    
});



