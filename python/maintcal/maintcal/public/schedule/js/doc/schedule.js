/**
*   This is the top-level model.
*
*   It contains one instance each of the other four models:
*
*       serviceTypes
*       devices
*       options
*       overrides
*
*/

Ext.namespace('Rack.app.maintcal');

Rack.app.maintcal.schedule = function () {

    this.connection         = new Ext.data.Connection({timeout : 60000});

    this.master_ticket      = '';
    this.account_name       = '';
    this.account_number     = '';
    this.maintenance_id     = '';
    this.contact            = '';
    this.selectedZoneName   = '';

    this.serviceTypes       = new Rack.app.maintcal.serviceTypes();
    this.devices            = new Rack.app.maintcal.devices(this);
    this.options            = new Rack.app.maintcal.options();
    this.overrides          = new Rack.app.maintcal.overrides();

    this.addEvents({
        dataerror:      true,
        widgetsready:   true
    });
};

Ext.extend(Rack.app.maintcal.schedule, Ext.util.Observable, {

    handleAccountData : function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            throw "handleAccountData: Json object not found";
        }

        if (!o.rows[0].account_number || 
            !o.rows[0].account_name || 
            !o.rows[0].ticket_number ||
            o.rows[0].account_number === "" ||
            o.rows[0].account_name === "" ||
            o.rows[0].ticket_number === "") {
            var error_string  = "No account information found. Either data" + 
            " sent from the server was invalid, or the ticket from which" + 
            " this maintenance was scheduled had no account.";
            this.fireEvent('dataerror', error_string);
        }
        else {
            this.master_ticket      = o.rows[0].ticket_number;
            this.account_name       = o.rows[0].account_name;
            this.account_number     = o.rows[0].account_number;
            this.ticket_url         = o.rows[0].ticket_url;
            this.account_url        = o.rows[0].account_url;
            this.contact            = o.rows[0].contact;
            this.ticket_devices     = o.rows[0].computers;
            this.notify_statuses    = o.rows[0].notify_statuses;
        }
    },

    handleWidgetReady : function () {
        this.fireEvent('widgetsready', this);
    },

    maskDocument: function (verbage) {
        if (!this.body.isMasked()) {
            this.body.mask(verbage);
        }
    },

    unmaskDocument: function () {
        if (this.body.isMasked()) {
            this.body.unmask();
        }
    }
});

