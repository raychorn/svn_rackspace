
Ext.namespace('Rack.app.maintcal.ticket');

Rack.app.maintcal.ticket = function (calendarDoc) {
    this.connection = new Ext.data.Connection({timeout : 60000});
    Ext.data.Store.call(this);
};

Ext.extend(Rack.app.maintcal.ticket, Ext.data.GroupingStore, {
    groupField: 'start_date',
    sortInfo: {field: 'start_date', direction: 'ASC'},
    // Maintain the state of the store
    hidden_states: "",
    calendar_id: null,
    start_date: new Date().clearTime(),
    end_date: new Date().clearTime().add(Date.DAY, 1),
    range_start: new Date().clearTime(),
    range_end: new Date().clearTime().add(Date.DAY, 1),
    currentTZ: null,
    appending: false,
    callbackFn: null,
    filter_start: new Date(),
    filter_end: new Date(),
 
    reader: new Ext.data.JsonReader({
        idProperty: 'ticket',
        fields: [
            {name: 'id', type: 'int'},
            {name: 'ticket', type: 'string'},
            {name: 'ticket_url', type: 'string'},
            {name: 'ticket_assignee', type: 'string'},
            {name: 'start_time_time_tuple', type: 'auto'},
            {name: 'start_date', type: 'string'},
            {name: 'end_time_time_tuple', type: 'auto'},
            {name: 'account_id', type: 'string'},
            {name: 'account_name', type: 'string'},
            {name: 'account_url', type: 'string'},
            {name: 'support_team', type: 'string'},
            {name: 'servers', type:'auto'}, 
            {name: 'service_type', type: 'string'},
            {name: 'recurrence_id', type: 'int'},
            {name: 'general_description', type: 'string'},
            {name: 'description', type: 'string'},
            {name: 'contact', type: 'string'},
            {name: 'date_assigned_time_tuple', type: 'auto'},
            {name: 'is_admin', type: 'boolean'},
            {name: 'is_UTC', type: 'boolean'},
            {name: 'state_id', type: 'int'},
            {name: 'state', type: 'string'},
            {name: 'maintenance_id', type: 'string'},
            {name: 'calendar_id', type: 'string'}
        ]
    }),
 
    getTicketsByDateRange: function (start_date, end_date, calendar_id, currentTZ, hidden_states, appending) {
        // Make sure that the main parameters haven't changed.
        if (appending !== undefined) {
            this.appending = appending;
        } else {
            this.appending = ((calendar_id === this.calendar_id) && (currentTZ === this.currentTZ) && (hidden_states === this.hidden_states));
        }
        this.currentTZ = currentTZ;
        this.calendar_id = calendar_id;
        this.hidden_states = hidden_states;
        this.filter_start = start_date;
        this.filter_end = end_date;
        if (!this.appending || this._needMoreData()) {
            // This will call _filterTicketsByDate() in its load handler
            this._getTicketsFromServer();
        } else {
            // Nothing to load, so just do the filter
            this._filterTicketsByDate();
        }
    },

    // TODO: Pull currentTZ from the TZ setter
    // TODO: Pull calendar_id from the calendar selector
    _buildURL: function (start_date, end_date) {
        var range_args = "&range_start=" + start_date.format("Ymd") + "&range_end=" + end_date.format("Ymd");
        var call_args = range_args + "&tzname=" + this.currentTZ;
        var hidden_args = this.hidden_states.join(":");
        if (hidden_args !== "") {
            call_args = call_args + "&states=" + encodeURIComponent(hidden_args);
        }
        return "/maintcal/services.json?calendar=" + this.calendar_id + call_args;
    },

    _needMoreData: function () {
        var needStart = (this.filter_start < this.range_start);
        var needEnd = (this.filter_end > this.range_end);
        return (needStart || needEnd);
    },

    _getTicketsFromServer: function () {
        // Adjust document date range and query date range
        // to avoid pulling too much data
        start_target = this.filter_start;
        end_target = this.filter_end;
        // The new filter range can be larger than the current range on *both* ends
        // If the new dates are only on one side or the other, adjust the date range
        // to only grab what is not already in the store.
        if ((start_target < this.range_start) && (end_target <= this.range_end)) {
            end_target = this.range_start;
            this.range_start = start_target;
        } else if ((end_target > this.range_end) && (start_target >= this.range_start)){
            start_target = this.range_end;
            this.range_end = end_target;
        } else if ((start_target < this.range_start) && (end_target > this.range_end)) {
            // Need to grab all the data, so clear the appending setting
            this.appending = false;
        }
        this.viewBody = Ext.get(document.body);
        if (!this.viewBody.isMasked()) {
            this.viewBody.mask("Getting Calendar data ...");
        } else {
            this.viewBody = null;
        }
        this.connection.request({
            url: this._buildURL(start_target, end_target),
            method: 'GET',
            success: this._querySuccess,
            failure: this._handleDataError,
            scope: this
        });
    },

    _filterTicketsByDate: function () {
        this.clearFilter();
        var filter = function (record, id) {
            var ticketStartDate = timeTupleToDate(record.get('start_time_time_tuple'));
            var ticketEndDate = timeTupleToDate(record.get('end_time_time_tuple'));
            var startOK = (ticketStartDate <= this.filter_end);
            var endOK = (ticketEndDate >= this.filter_start);
            return (startOK && endOK);
        };
        this.filterBy(filter);
        this.fireEvent("ticketsloaded");
    },

    _querySuccess: function(response) {
        var json = response.responseText;
        var data = eval("(" + json + ")");
        if (!data) {
            this.fireEvent('dataerror', this, response);
            throw "handleResponse: Json object not found";
        }
        if (data.metaData) {
            if (!this.appending) {
                delete this.reader.ef;
                this.reader.meta = data.metaData;
                this.reader.meta.sortInfo = this.sortInfo;
                //this.reader.recordType = Ext.data.Record.create(data.metaData.fields);
                this.reader.onMetaChange(this.reader.meta, this.reader.recordType, data);
            } 
            this.on("load", this._onLoad, this);
            this.loadData(data, this.appending);
        }
        if (this.viewBody && this.viewBody.isMasked()) {
            this.viewBody.unmask();
        }
    },

    _handleDataError: function (response) {
        if (this.viewBody && this.viewBody.isMasked()) {
            this.viewBody.unmask();
        }
        view.fireEvent('dataerror', response);
    },

    _onLoad: function() {
        this.un("load", this._onLoad);
        Ext.util.DelayedTask(this._filterTicketsByDate);
    }
});



Ext.namespace('Rack.app.maintcal.ticket.devices');
Rack.app.maintcal.ticket.devices = function () {
    Ext.data.Store.call(this);
    this.connection = new Ext.data.Connection({timeout: 60000});
};

Ext.extend(Rack.app.maintcal.ticket.devices, Ext.data.Store, {

    reader: new Ext.data.JsonReader({
            idProperty: 'id',
            fields: [
                {name: 'id', type: 'int'},
                {name: 'os', type: 'string'},
                {name: 'icon', type: 'string'},
                {name: 'server_url', type: 'string'},
                {name: 'datacenter', type: 'string'},
                {name: 'name', type: 'string'},
                {name: 'segment', type: 'string'},
                {name: 'has_managed_storage', type: 'string'},
                {name: 'managed_storage_type', type: 'string'},
                {name: 'has_managed_backup', type: 'string'},
                {name: 'attached_devices', type: 'string'},
                {name: 'is_in_ticket', type: 'boolean'}
            ]
    })
});

