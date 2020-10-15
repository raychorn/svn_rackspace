/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.options');

Rack.app.maintcal.options = function () {
    Ext.data.Store.call(this);
    this.connection = new Ext.data.Connection({timeout : 60000});
    this.addEvents({
        dataready : true,
        widgetready : true,
        dataerror : true
    });
    this.on('dataready', this.handleDataReady, this);
    // pass a single 'dataerror' event for all data load errors
    this.on('loadexception', this.handleLoadError, this);
    this.on('loaderror', this.handleLoadError, this);

};

Ext.extend(Rack.app.maintcal.options, Ext.data.Store, {

    load : function () {
        this.fireEvent('load');
        this.fireEvent('datachanged');
    },

    reader : new Ext.data.JsonReader({
        idProperty : 'value',
        fields : [
            {name: 'value', type: 'int'},
            {name: 'name', type: 'string'}
        ]

    }),

    handleDataReady : function () {
        this.connection.request({
            url:        '/maintcal/maintenances/durations/',
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
            throw "handleResponse: Json object not found";
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

    handleLoadError : function (r, o) {
        this.fireEvent('dataerror', r);
    }
});  

