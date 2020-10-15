/**
*   This is the dialog that is displayed so that the user
*   can confirm a scheduled maintenance.
*/

Ext.namespace('Rack.app.maintcal.confirmationDialog');

Rack.app.maintcal.confirmationDialog = function (schedule_view, maint_opts, devices_panel, dt_confirm, tentative_view) {
    this.schedule_view = schedule_view;
    this.tentativeDialog = tentative_view;
    this.maintenance_options = new Ext.Panel({
        frame: true,
        html: maint_opts
    });
    this.dateTimeConfirm =  new Ext.Panel({
        frame: true,
        html: dt_confirm
    });
    var config = {
        width: 700,
        autoScroll: true,
        draggable: false,
        resizable: false,
        shadow: true,
        closeAction: 'close',
        title: 'Confirm Scheduled Maintenance',
        plain: true,
        frame: true,
        modal: true,
        layoutConfig: {autoWidth: false},
        buttons: [{
            text: 'Confirm',
            handler: this.confirmMaintenance,
            scope: this
        }, {
            text: 'Cancel',
            handler: this.cancelMaintenance,
            scope: this
        }],
        items: [
            this.maintenance_options,
            devices_panel,
            this.dateTimeConfirm
        ]
    };

    Ext.Window.call(this, config);
};

Ext.extend(Rack.app.maintcal.confirmationDialog, Ext.Window, {

    confirmMaintenance : function () {
        var task = new Rack.app.maintcal.confirmMaintenance(this);
        task.start();
    },

    cancelMaintenance : function () {
        //window.close();
        this.close();
        this.tentativeDialog.show();
    }
});

