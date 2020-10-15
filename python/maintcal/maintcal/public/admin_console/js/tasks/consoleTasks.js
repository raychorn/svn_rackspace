/*extern Ext, Rack, gem, global_view, global_doc*/

Rack.app.maintcal.adminConsole.baseTask = Ext.extend(Ext.util.Observable,{
    start: function () {
        // subclass needs to override this method.
        return 0;
    },

    maskView: function (this_view) {
        if (this_view.isVisible && this_view.body &&
                 this_view.body.mask &&
                 !this_view.body.isMasked()) {
            this_view.body.mask('Loading ... ');
        }
    },

    unmaskView : function (this_view) {
        if (this_view.body && this_view.body.isMasked()){
            this_view.body.unmask();
        }
    },

    handleLoadResponse : function (r) {
        // subclass needs to override this method.
        return 0;        

    },

    handleDataError : function (r, o) {
        // Ryan hates these alerts ... get rid of them
        global_view.handleDataError(r,o);

    }
});

Rack.app.maintcal.adminConsole.loadCalendars = function (view,doc,post_load) {
    // post_load indicates a reload of data
    this.post_load = !! post_load;
    this.doc = doc;
    this.view = view;
    Ext.util.Observable.call(this);
};

Ext.extend(Rack.app.maintcal.adminConsole.loadCalendars,
            Rack.app.maintcal.adminConsole.baseTask,
    {
    start: function () {
        var base_string = '/maintcal/calendars/show_calendar_info.json';
        this.doc.connection.request({
            method: 'POST',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this,
            params: {
                admin_console : true,
                allData : true
            }
        });
    },

    /**
    *  This creates the buttons on the left.
    */
    handleLoadResponse: function (r) {
        
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows) {
            r.reponseText = "Data Failed to load from the server.";
            this.view.fireEvent('dataerror',r);
            throw "handleResponse: Json object not found";
        }
        global_view.makeViewPort();
        // initially hide calendar navigation.
        // disable calendar navigation for iteration 1.
        //this.view.setCalendarNavigation('hide');

        // bind the returned object to the doc.
        this.doc.calendarData = o.rows[0];
        // add global configuration button
        // and bind them to the naviator
        global_view.west.makeSectionButtons();
        global_view.fireEvent('calendarsloaded');
    }
});

Rack.app.maintcal.adminConsole.displayGeneralData = function (view,doc) {
    this.doc = doc;
    this.view = view;
    Ext.util.Observable.call(this);
};

Ext.extend(Rack.app.maintcal.adminConsole.displayGeneralData,
            Rack.app.maintcal.adminConsole.baseTask,{
    
    start : function (cal_id) {
        this.requested_id = parseInt(cal_id,10);
        // load the calendar config panel if the data is there.
        if (this.doc.calendarData.hasOwnProperty(cal_id)) {
            global_view.generalDataLoad(cal_id);
        } else {
            global_view.center.el.mask('Loading ...');
            this.doc.on('calendarloaded', function(cal_id) { global_view.generalDataLoad(cal_id); });
        }
    }
});

/* This object was only being used in the global_view.doAsyncload method,
which has been disabled.
Rack.app.maintcal.adminConsole.loadCalendarData = function (view,doc,post_load) {
    
    // post_load indicates a reload of data
    if (post_load) {
        this.post_load = true;
    } else {
        this.post_load = false;
    }
    this.doc = doc;
    this.view = view;
    Ext.util.Observable.call(this);
};

Ext.extend(Rack.app.maintcal.adminConsole.loadCalendarData,
            Rack.app.maintcal.adminConsole.baseTask,{
    
    start : function (cal_id) {
        var base_string = '/maintcal/calendars/show_calendar_info.json';
        this.doc.connection.request({
            method: 'POST',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this,
            params: {
                admin_console : true,
                allData : true,
                calendars : cal_id
            }
        });
    },

    handleLoadResponse : function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows) {
            r.reponseText = "Data Failed to load from the server.";
            this.view.fireEvent('dataerror',r);
            throw "handleResponse: Json object not found";
        }
        this.view.setCalendarData(o.rows);
    }
});
*/
Rack.app.maintcal.adminConsole.loadQueueData = function (view,doc,post_load) {
    // post_load indicates a reload of data
    if (post_load) {
        this.post_load = true;
    } else {
        this.post_load = false;
    }
    this.addEvents({
        'dataloaded' : true
    });
    this.doc = doc;
    this.view = view;
    Ext.util.Observable.call(this);
};

Ext.extend(Rack.app.maintcal.adminConsole.loadQueueData,
            Rack.app.maintcal.adminConsole.baseTask,
    {
    
    start : function (cal_id) {
        for( val in this.doc.queueData){
            if(this.doc.queueData[val] === 1){
                this.fireEvent('dataloaded',this.doc.queueData);
                return;
            }
        }
        var base_string = '/maintcal/xmlrpcproxy/Ticket/getQueues';
        this.doc.connection.request({
            method: 'GET',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this
        });
    },

    handleLoadResponse : function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows || o.rows.length != 1) {
            r.reponseText = "Data Failed to load from the server.";
            this.view.fireEvent('dataerror',r);
            throw "handleResponse: Json object not found";
        }

        this.doc.queueData = o.rows[0];
        this.fireEvent('dataloaded', this.doc.queueData);
    }

});

Rack.app.maintcal.adminConsole.loadSubCategory = function (doc) {
    Ext.util.Observable.call(this);
    this.addEvents({
        'catloaded' : true
    });
    this.doc = doc;
};

Ext.extend(Rack.app.maintcal.adminConsole.loadSubCategory,
            Rack.app.maintcal.adminConsole.baseTask,
    {
    
    start : function (queue_id,fire_event) {
        this.queue_id = queue_id;
        // passed true to fire an event when the load is complete.
        this.fire_event = fire_event;
        var base_string ='/maintcal/xmlrpcproxy/Ticket/system_getQueueSubCategories';
        base_string = base_string + '?queue_id=' + this.queue_id.toString();
        this.doc.connection.request({
            method: 'GET',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this
        });
    },

    handleLoadResponse : function (r) {

        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows || !o.metaData.queue_id) {
            r.reponseText = "Data Failed to load from the server.";
            global_view.fireEvent('dataerror',r);
            throw "handleResponse: Json object not found";
        }
        //var anon_obj = {};
        //anon_obj[this.queue_id] = o.rows;
        global_doc.subCatData[o.metaData.queue_id] = o.rows;
        //Ext.apply(global_doc.subCatData,anon_obj);
        if (this.fire_event) {
            this.fireEvent('catloaded');
        }
    }

});

Rack.app.maintcal.adminConsole.categoriesAsNeeded = function(doc) {
    Ext.util.Observable.call(this);
    this.addEvents({
        'dataloaded' : true
    });
    this.catsRequested = [];
    this.loadTask = new Rack.app.maintcal.adminConsole.loadSubCategory(doc);
    this.doc = doc;
    this.loadTask.on('catloaded',this.handleCatLoaded,this);

};

Ext.extend(Rack.app.maintcal.adminConsole.categoriesAsNeeded,
    Rack.app.maintcal.adminConsole.baseTask,{
    start : function(cats) {
        if (cats instanceof Array) {
            for (var a=0; a<cats.length;a++) {
                // requested category is either in process or has 
                // been loaded already.
                if (this.doc.subCatData.hasOwnProperty(cats[a]) ||
                    (this.catsRequested.indexOf(cats[a]) !== -1)) {
                    this.handleCatLoaded(cats[a]); 
                }
                else {
                    // make the request
                    this.catsRequested.push(cats[a]);
                    this.loadTask.start(cats[a],true);
                }
            }
        } 
        else if (typeof cats === "number") {
            // this category id is being loaded.
            if (this.doc.subCatData.hasOwnProperty(cats) ||
                (this.catsRequested.indexOf(cats) !== -1)) {
                this.handleCatLoaded(cats); 
            }
            else {
                this.catsRequested.push(cats);
                //make the call.
                this.loadTask.start(cats,true);
            }
        } 
        else {
            throw "Not a valid data type.";
        }
    },

    handleCatLoaded : function() {
        // check to see if this task is process.
        if(this.loadTask.doc.connection.isLoading()){
            return;
        }
        this.fireEvent('dataloaded',this.doc.subCatData);
        this.catsRequested = [];
    }
});

Rack.app.maintcal.adminConsole.loadStatuses = function (doc) {
    Ext.util.Observable.call(this);
    this.addEvents({
        'statusloaded' : true
    });
    this.doc = doc;
};

Ext.extend(Rack.app.maintcal.adminConsole.loadStatuses,
            Rack.app.maintcal.adminConsole.baseTask,
    {
    
    start : function (queue_id,fire_event) {
        this.queue_id = queue_id;
        // passed true to fire an event when the load is complete.
        this.fire_event = fire_event;
        var base_string ='/maintcal/xmlrpcproxy/Ticket/system_getStatuses';
        base_string = base_string + '?queue_id=' + this.queue_id.toString();
        this.doc.connection.request({
            method: 'GET',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this
        });
    },

    handleLoadResponse : function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows || !o.metaData.queue_id) {
            r.reponseText = "Data Failed to load from the server.";
            global_view.fireEvent('dataerror',r);
            throw "handleResponse: Json object not found";
        }
        global_doc.statusData[o.metaData.queue_id] = this.massageStatusData(o.rows);
        if (this.fire_event) {
            this.fireEvent('statusloaded');
        }
    },

    massageStatusData : function(d) {
        var new_container = [];
        var i;
        for (i=0;i<d.length;i++) {
            var j;
            for (j in d[i]) {
                new_container.push({name : j,id : d[i][j]});
            }
        }
        return new_container;
    }
});

Rack.app.maintcal.adminConsole.statusesAsNeeded = function(doc) {
    Ext.util.Observable.call(this);
    this.addEvents({
        'dataloaded' : true
    });
    this.statusesRequested = [];
    this.loadTask = new Rack.app.maintcal.adminConsole.loadStatuses(doc);
    this.doc = doc;
    this.loadTask.on('statusloaded',this.handleStatLoaded,this);
};

Ext.extend(Rack.app.maintcal.adminConsole.statusesAsNeeded,
    Rack.app.maintcal.adminConsole.baseTask,{
    start : function(stats) {
        if (stats instanceof Array) {
            var a;
            for (a=0; a<stats.length;a++) {
                if (this.doc.statusData.hasOwnProperty(stats[a]) ||
                    (this.statusesRequested.indexOf(stats[a]) !== -1)) {
                    this.handleStatLoaded(stats[a]);
                }
                else {
                    // make the request
                    this.statusesRequested.push(stats[a]);
                    this.loadTask.start(stats[a],true);
                }
            }
        }
        else if (typeof stats === "number") {
            if (this.doc.statusData.hasOwnProperty(stats) ||
                (this.statusesRequested.indexOf(stats) !== -1)) {
                    this.handleStatLoaded(stats);
            } 
            else {
                this.statusesRequested.push(stats)
                //make the call.
                this.loadTask.start(stats,true);
            }
        }
        else {
            throw "Not a valid data type.";
        }

    },

    handleStatLoaded : function() {
        if(this.loadTask.doc.connection.isLoading()) {
            return;
        }
        this.fireEvent('dataloaded',this.doc.statusData);
        this.statusesRequested = [];
    }
});

Rack.app.maintcal.adminConsole.updateCalendars = function (view,doc) {
    Ext.util.Observable.call(this);
    this.doc = doc;
    this.view = view;
};

Ext.extend(Rack.app.maintcal.adminConsole.updateCalendars,
            Rack.app.maintcal.adminConsole.baseTask,
    {
    
    start : function (cal_id,update_params) {
        var base_string ='/maintcal/calendars/update/';
        base_string = base_string + cal_id.toString();
        this.doc.connection.request({
            method: 'POST',
            url: base_string,
            params : update_params,
            success: this.handleUpdateResponse,
            failure: this.handleUpdateError,
            scope: this
        });
    },

    handleUpdateResponse : function (r) {
        // make sure the value coming back is in the list of calendars
        if(!global_doc.calendarData.hasOwnProperty(parseInt(r.responseText,10))) {
            this.handleUpdateError("Invalid Calendar id returned");
        }
        else {
            this.confirmUpdate(r.responseText);
        }
    },

    handleUpdateError : function(r) {
        this.handleDataError(r);
    },

    confirmUpdate : function(cal_id) {
        var base_string = '/maintcal/calendars/show_calendar_info.json';
        this.doc.connection.request({
            method: 'POST',
            url: base_string,
            success: this.handleConfirmResponse,
            failure: this.handleConfirmError,
            scope: this,
            params: {
                admin_console : true,
                allData : true,
                calendars : cal_id
            }
        });
    },

    handleConfirmResponse : function(r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows) {
            r.reponseText = "Data Failed to load from the server.";
            this.view.fireEvent('dataerror',r);
            throw "handleResponse: Json object not found";
        };
        // here key is the calendar id
        var cals = o.rows[0];
        for (key in cals) {
            this.doc.calendarData[key] = cals[key];
            global_doc.fireEvent('calendarloaded',key)
        }
    },

    handleConfirmError : function(r) {
        this.handleDataError(r);
    }
});

