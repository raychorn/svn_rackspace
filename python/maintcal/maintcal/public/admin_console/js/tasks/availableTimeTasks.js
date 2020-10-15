/*extern Ext, Rack, global_doc*/

Rack.app.maintcal.adminConsole.loadAvailableDefaults = function (view) {
    this.doc = view;
    this.view = view;
    Ext.util.Observable.call(this);
};

Ext.extend(Rack.app.maintcal.adminConsole.loadAvailableDefaults,
            Rack.app.maintcal.adminConsole.baseTask,{

    start : function(cal_id) {
        if(this.view.el && !this.view.el.isMasked()) {
            this.view.el.mask('Loading ...');
        }
        var base_string = '/maintcal/available_defaults/' + cal_id;
        this.doc.connection.request({
            method: 'GET',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this
        });
    },

    handleLoadResponse : function(the_response) {
        var json = the_response.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows) {
            the_response.reponseText = "Data Failed to load from the server.";
            this.view.fireEvent('dataerror',the_response);
            throw "handleResponse: Json object not found";
        }
        this.view.loadAvailableDefaults(o.rows[0]);
    }
});

Rack.app.maintcal.adminConsole.saveAvailableDefaults = function (view) {
    this.doc = view;
    this.view = view;
    Ext.util.Observable.call(this);
};
Ext.extend(Rack.app.maintcal.adminConsole.saveAvailableDefaults,
            Rack.app.maintcal.adminConsole.baseTask,{

    start : function(cal_id, calendar_data) {
        this.view.el.mask('Saving ...');
        var base_string = '/maintcal/available_defaults/' + cal_id + "/update";
        var post_params =  {
                admin_console : true,
                calendar_data : Ext.util.JSON.encode(calendar_data)
            };
        this.doc.connection.request({
            method: 'POST',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this,
            params: post_params
        });
    },

    handleLoadResponse : function(the_response) {
        var json = the_response.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows) {
            the_response.reponseText = "Data Failed to save to the server.";
            this.view.fireEvent('dataerror',the_response);
            throw "handleResponse: Json object not found";
        }
        this.view.savedAvailableDefaults(o.rows[0]);
    }
});

/**
*
*/
Rack.app.maintcal.adminConsole.loadAvailableExceptions = function (view) {
    this.doc = view;
    this.view = view;
    Ext.util.Observable.call(this);
};

Ext.extend(Rack.app.maintcal.adminConsole.loadAvailableExceptions,
            Rack.app.maintcal.adminConsole.baseTask,{

    start : function(cal_id,js_start_date,js_end_date) {
        if(this.doc.connection.isLoading()) {
            return;
        }
        // mask if necessary and possible
        if(this.view.el && !this.view.el.isMasked()) {
            this.view.el.mask('Loading ...');
        }
        var base_string = '/maintcal/available_exceptions/' + cal_id;
        this.doc.connection.request({
            method: 'POST',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this,
            params: {
                start_year : js_start_date.format('Y'),
                start_month : js_start_date.format('n'),
                start_day : js_start_date.format('j'),
                end_year : js_end_date.format('Y'),
                end_month : js_end_date.format('n'),
                end_day :  js_end_date.format('j'),
                tzname : global_doc.calendarData[cal_id].timezone
           }
        });
    },

    handleLoadResponse : function(the_response) {
        var json = the_response.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows) {
            the_response.reponseText = "Data Failed to load from the server.";
            this.view.fireEvent('dataerror',the_response);
            throw "handleResponse: Json object not found";
        }
        // we could cache the available Time data in the calendar data-structure and only
        // show when asked ... 
        this.view.loadAvailableExceptions(o.rows[0]);
    }
});

Rack.app.maintcal.adminConsole.saveAvailableExceptions = function (view) {
    this.doc = view;
    this.view = view;
    Ext.util.Observable.call(this);
};
Ext.extend(Rack.app.maintcal.adminConsole.saveAvailableExceptions,
            Rack.app.maintcal.adminConsole.baseTask,{

    start : function(cal_id, calendar_data) {
        if(this.doc.connection.isLoading()) {
            return;
        }
        // mask if necessary and possible
        if(this.view.el && !this.view.el.isMasked()) {
            this.view.el.mask('Saving ...');
        }
        var base_string = '/maintcal/available_exceptions/' + cal_id + "/update";
        var post_params =  {
                admin_console : true,
                calendar_data : Ext.util.JSON.encode(calendar_data)
            };
        this.doc.connection.request({
            method: 'POST',
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this,
            params: post_params
        });
    },

    handleLoadResponse : function(the_response) {
        var json = the_response.responseText;
        var o = eval("(" + json + ")");
        if (!o || !o.rows) {
            the_response.reponseText = "Data Failed to save to the server.";
            this.view.fireEvent('dataerror',the_response);
            throw "handleResponse: Json object not found";
        }
        this.view.loadAvailableExceptions(o.rows[0]);
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
        this.view.el.unmask();
    }

});


