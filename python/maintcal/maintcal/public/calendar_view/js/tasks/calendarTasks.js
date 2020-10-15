/*extern Ext, Rack */

Rack.app.maintcal.calendar.getCalendars = function (view, doc) {

    this.start = function () { 
        doc.connection.request({
            url: '/maintcal/calendars.json?active=true',
            method: 'GET',
            success: this.handleLoadResponse,
            failure: this.handleDataError,
            scope: this
        });
    };

    this.handleLoadResponse = function (r) {
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
            doc.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            doc.reader.onMetaChange(doc.reader.meta, doc.reader.recordType, o);
            doc.loadData(o);
        }

    };

    this.handleDataError = function (r, o) {
        doc.fireEvent('dataerror', r, o);
    };
};


Rack.app.maintcal.calendar.fillCalendars = function (view, doc) {

    this.start = function (start_year, start_month, calendar_id, 
            currentTZ, hidden_states) {
        this.viewBody = Ext.get(document.body);
        if (!this.viewBody.isMasked()) {
            this.viewBody.mask("Getting Calendar data ...");
        } else {
            this.viewBody = null;
        }
        var url_arg;
        // only send the 'states' argument if there are states to be hidden
        if (hidden_states.join(':') === "") {
            url_arg = '/maintcal/services.sjson?calendar=' + calendar_id +
                '&start_year=' + start_year + '&start_month=' +
                start_month + '&tzname=' + currentTZ;
        } else {
            url_arg =  '/maintcal/services.sjson?calendar=' + calendar_id +
                '&start_year=' + start_year + '&start_month=' +
                start_month + '&tzname=' + currentTZ + '&states=' +
                encodeURIComponent(hidden_states.join(':'));
        }
        doc.connection.request({
            url: url_arg,
            method: 'GET',
            success: this.updateCalendar,
            failure: this.handleDataError,
            scope: this
        });
    };

    this.updateCalendar = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o && !o.length && o[0].length !== 3) {
            doc.fireEvent('dataerror', doc, r);
            throw "updateCalendar: Json object not found";
        }
        view.monthView.addScheduleTime(o);
        if (this.viewBody && this.viewBody.isMasked()) {
            this.viewBody.unmask();
        }
    };

    this.handleDataError = function (r, o) {
        doc.fireEvent('dataerror', r, o);
    };
};

