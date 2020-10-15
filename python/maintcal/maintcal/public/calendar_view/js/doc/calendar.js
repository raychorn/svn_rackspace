/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.calendar');

Rack.app.maintcal.calendar = function () {
    this.connection = new Ext.data.Connection({timeout: 60000});
    this.tickets = new Rack.app.maintcal.ticket(this);
    this.addEvents({
        dataerror: true,
        widgetsready: true
    });
    Ext.data.Store.call(this);
};

Ext.extend(Rack.app.maintcal.calendar, Ext.data.Store, {
    reader: new Ext.data.JsonReader({
        idProperty: 'id',
        fields: [
            {name : 'id', type: 'int'},
            {name : 'name', type: 'string'},
            {name : 'description', type: 'string'},
            {name : 'is_admin', type: 'boolean'},
            {name : 'tckt_queue_id', type: 'int'},
            {name : 'active', type: 'boolean'},
            {name : 'available_states', type : 'auto'}
        ]
    }),
    maskDocument: function (verbiage) {
        if (!this.body.isMasked()) {
            this.body.mask(verbiage);
        }
    },
    unmaskDocument: function () {
        if (this.body.isMasked()) {
            this.body.unmask();
        }
    }
});
