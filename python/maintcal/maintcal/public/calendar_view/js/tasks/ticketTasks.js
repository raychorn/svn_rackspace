/**
*   Ticket-related tasks.
*/

Ext.namespace('Rack.app.maintcal.ticket');

Rack.app.maintcal.ticket.getTickets = function (view, doc) {
    this.start = function (range_start, range_end, calendar_id, currentTZ, hidden_states, append) {
        this.viewBody = Ext.get(document.body);
        if (!this.viewBody.isMasked()) {
            this.viewBody.mask("Loading ...");
        } else {
            this.viewBody = null;
        }
        
        this.appending = (append === true);
        var date_range_format = "Ymd";
        var call_args = '&tzname=' + currentTZ;
        var start_args = "";
        var hidden_args = hidden_states.join(":");
        var range_args = "";
        if ((range_start !== undefined) && (range_end !== undefined)) {
            range_start = new Date(Math.min(range_start, doc.range_start));
            range_end = new Date(Math.max(range_end, doc.range_end));
            range_args = "range_start=" + range_start.format(date_range_format) + "&range_end=" + range_end.format(date_range_format);
        }
        if (!range_args) {
            if ((start_year !== undefined) && (start_month !== undefined)) {
                start_args = "start_year=" + start_year + "&start_month=" + start_month + "&start_day=" + start_day;
            }
        }
        if (start_args !== "") {
            call_args = call_args + "&" + start_args;
        }
        if (range_args !== "") {
            call_args = call_args + "&" + range_args;
        }
        if (hidden_args !== "") {
            call_args = call_args + "&states=" + encodeURIComponent(hidden_args);
        }
        var url_arg = "/maintcal/services.json?calendar=" + calendar_id + call_args;

        doc.range_start = range_start;
        doc.range_end = range_end;
        doc.hidden_args = hidden_args;
        doc.calendar_id = calendar_id;
        doc.currentTZ = currentTZ;
        doc.connection.request({
            url: url_arg,
            method: 'GET',
            success: this.getWidgetData,
            failure: this.handleDataError,
            scope: this
        });
    };

    this.getWidgetData = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            doc.fireEvent('dataerror', doc, r);
            throw "handleResponse: Json object not found";
        }
        if (o.metaData) {
            delete doc.reader.ef;
            doc.reader.meta = o.metaData;
            doc.reader.meta.sortInfo = doc.sortInfo;
            //doc.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            doc.reader.onMetaChange(doc.reader.meta, doc.reader.recordType, o);
            doc.loadData(o, this.appending);
        }
        if (this.viewBody && this.viewBody.isMasked()) {
            this.viewBody.unmask();
        }
    };

    this.handleDataError = function (r) {
        view.fireEvent('dataerror', r);
    };


    this.onLoad = function () {
        doc.un("load", this.onLoad);
        view.addTickets();
    };
};

Rack.app.maintcal.ticket.getDevices = function (doc) {
    this.start = function (id) {
        doc.connection.request({
            url: '/maintcal/devices/' + id + '.json',
            method: 'GET',
            success: this.getWidgetData,
            failure: this.handleLoadError,
            scope: this
        });
    };

    this.getWidgetData = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            doc.fireEvent('dataerror', doc, r);
            throw "handleResponse: Json object not found";
        }
        if (o.metaData) {
            delete doc.reader.ef;
            doc.reader.meta = o.metaData;
            doc.reader.meta.sortInfo = doc.sortInfo;
            //doc.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            doc.reader.onMetaChange(doc.reader.meta, doc.reader.recordType, o);
            doc.loadData(o, true);
        }
    };
    this.handleDataError = function (r) {
        view.fireEvent('dataerror', r);
    };
};

Rack.app.maintcal.ticket.loadMaintenanceInfoForTicket = function (ticketbox) {

    this.start = function (ticket, currentTZ) {
        this.maintenance_id = ticket.data.maintenance_id;
        this.ticketbox = ticketbox;
        this.currentTZ = currentTZ;

        if (!this.maintenance_id) {
            this.showDataError("no maintenance id found in the URL parameters.");
        }

        this.ticketbox.ticket.store.connection.request({
                url: '/maintcal/maintenances/' + this.maintenance_id +
                    '.sjson?tzname=' + currentTZ,
                method: 'GET',
                success: this.populateViews,
                failure: this.showDataError,
                scope: this
            });
    };

    this.populateViews = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            this.showDataError("populateViews: Json object not found");
            throw "populateViews: Json object not found";
        }

        if (o.maintenance_id && isArray(o.devices) && isArray(o.services)) {
            this.ticketbox.maintenance_id = o.maintenance_id;
            this.ticketbox.popWindow(o);
        } else {
            this.showDataError("Data structure is missing key components");
        }
    };
                
    this.showDataError = function (r) {
        var msgResponse;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText === 'undefined') {
                msgResponse = this.genericDataErrorText;
            }
            else {
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
    };
};


Rack.app.maintcal.ticket.cancelService = function (doc) {
    this.start = function (service_id, panel_ref, reasons, cancelReasonText) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        if (!this.viewBody.isMasked()) {
            this.viewBody.mask('Canceling Service ...');
        } else {
            this.viewBody = null;
        }
        var requestConfig = {
            url: '/maintcal/services/cancel/' + service_id,
            method: 'POST',
            success: this.handleSuccessCancel,
            failure: this.showDataError,
            scope: this
        };
        // make the request either with or without a reason if present.
        if (cancelReasonText != null && cancelReasonText.length >= 1) {
            requestConfig.params = {'reasons': reasons, cancel_message: cancelReasonText};
        } else {
            requestConfig.params = {'reasons': reasons};
        }
            
        doc.store.connection.request(requestConfig);
    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
        var msgResponse;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText === 'undefined') {
                msgResponse = this.genericDataErrorText;
            }
            else {
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
    };

    this.handleSuccessCancel = function (r) {
        this.viewBody.unmask();
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return;
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been successfully canceled.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };

    this.modifyServicePanelState = function () {
       this.panel_ref.fireEvent('statechange',this.panel_ref); 
            
    };
};

Rack.app.maintcal.ticket.completeService = function (doc) {

    this.start = function (service_id, panel_ref) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Completing Service ...');
        doc.store.connection.request({
            url: '/maintcal/services/complete/' + service_id,
            method: 'POST',
            success: this.handleSuccessComplete,
            failure: this.showDataError,
            scope: this
        });
    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
        var msgResponse;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText === 'undefined') {
                msgResponse = this.genericDataErrorText;
            }
            else {
                msgResponse = parseWSGIError(r.responseText);
            }
        }
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: window.close,
                buttons: Ext.MessageBox.OK,
                width: 250,
                scope: window
            });
    };

    this.handleSuccessComplete = function (r) {
        this.viewBody.unmask();
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return;
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been successfully completed.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };
 
    this.modifyServicePanelState = function () {
       this.panel_ref.fireEvent('statechange',this.panel_ref); 
    };
};


Rack.app.maintcal.ticket.completeServiceWithIssues = function (doc) {

    this.start = function (service_id, panel_ref, reasons, feedback) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Completing Service ...');
        var requestConfig = {
            url: '/maintcal/services/completeWithIssues/' + service_id,
            method: 'POST',
            success: this.handleSuccessComplete,
            failure: this.showDataError,
            scope: this
        };
        if (feedback != null && feedback.length >= 1)
            requestConfig.params = {feedback: feedback, reasons: reasons};
        else
            requestConfig.params = {'reasons': reasons};
         
        doc.store.connection.request(requestConfig);
    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
        var msgResponse;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText === 'undefined') {
                msgResponse = this.genericDataErrorText;
            }
            else {
                msgResponse = parseWSGIError(r.responseText);
            }
        }
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: window.close,
                buttons: Ext.MessageBox.OK,
                width: 250,
                scope: window
            });
    };

    this.handleSuccessComplete = function (r) {
        this.viewBody.unmask();
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return;
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been successfully completed.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };
 
    this.modifyServicePanelState = function () {
       this.panel_ref.fireEvent('statechange',this.panel_ref); 
    };
};

Rack.app.maintcal.ticket.unsuccessfulService = function (doc) {

    this.start = function (service_id, panel_ref, reasons, feedback) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Completing Service ...');
        var requestConfig = {
            url: '/maintcal/services/unsuccessful/' + service_id,
            method: 'POST',
            success: this.handleUnsuccessful,
            failure: this.showDataError,
            scope: this
        };
        if (feedback != null && feedback.length >= 1)
            requestConfig.params = {feedback: feedback, reasons: reasons};
        else
            requestConfig.params = {'reasons': reasons};
         
        doc.store.connection.request(requestConfig);
    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
        var msgResponse;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText === 'undefined') {
                msgResponse = this.genericDataErrorText;
            }
            else {
                msgResponse = parseWSGIError(r.responseText);
            }
        }
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: window.close,
                buttons: Ext.MessageBox.OK,
                width: 250,
                scope: window
            });
    };

    this.handleUnsuccessful = function (r) {
        this.viewBody.unmask();
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return;
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been failed.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };
 
    this.modifyServicePanelState = function () {
       this.panel_ref.fireEvent('statechange',this.panel_ref); 
    };
};

