/*extern Ext, Rack */
// add a namespace to the standard EXTJS GroupStore.

Ext.namespace('Rack.app.maintcal.serviceTypes');

Rack.app.maintcal.serviceTypes = function () {
    Ext.data.GroupingStore.call(this);
    this.connection = new Ext.data.Connection({timeout : 60000});
    this.addEvents({
        dataready : true,
        widgetready : true,
        dataerror : true
    });
    this.on('dataready', this.onPageLoad);

};

Ext.extend(Rack.app.maintcal.serviceTypes, Ext.data.GroupingStore, {

    groupField : 'maintenance_category',

    sortInfo: {
        field : "id",
        direction : "ASC"
    },

    reader : new Ext.data.JsonReader({
        idProperty: 'id',
        fields: [
            {name: 'maintenance_category_id', type: 'int'},
            {name: 'maintenance_category', type: 'string'},
            {name: 'id', type: 'int'},
            {name: 'description', type: 'string'},
            {name: 'name', type: 'string'},
            {name: 'service_category', type: 'string'},
            {name: 'length_hours', type: 'float'},
            {name: 'lead_time_hours', type: 'float'},
            {name: 'modifcation_date', type: 'string'},
            {name: 'modification_contact', type: 'string'},
            {name: 'active', type: 'bool'}
        ]
    }),

    onPageLoad : function (e, a, t) {
        this.connection.request({
            url:        '/maintcal/servicetypes.json?active=true',
            method:     'GET',
            success:    this.handleLoadResponse,
            failure:    this.handleLoadError,
            scope:      this
        });
    },

    handleLoadResponse : function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            this.fireEvent('dataerror', this, r);
            throw "handleResponse : Json object not found";
        }
        if (o.metaData) {
            delete this.reader.ef;
            this.reader.meta = o.metaData;
            this.reader.meta.sortInfo = this.sortInfo;
            this.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            this.reader.onMetaChange(this.reader.meta, this.reader.recordType, o);
            this.loadData(o);
            this.fireEvent('widgetready', this);
        }
        
    },

    handleLoadError: function (r, o) {
        this.fireEvent('dataerror', r);
    }
});

