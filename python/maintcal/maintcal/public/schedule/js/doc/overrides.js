/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.overrides');

Rack.app.maintcal.overrides = function () {
    Ext.data.Store.call(this);
    this.connection = new Ext.data.Connection({timeout: 60000});
    this.addEvents({
        dataerror: true
    });
};

Ext.extend(Rack.app.maintcal.overrides, Ext.data.Store, {
    reader: new Ext.data.JsonReader({
        idProperty: 'id',
        fields: [
            {name: 'id', type: 'int'},
            {name: 'name', type: 'string'},
            {name: 'description', type: 'string'},
            {name: 'is_selected', type: 'boolean'},
            {name: 'is_error', type: 'boolean'},
        ]

    })
});

