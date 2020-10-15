/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.overridesView');

Rack.app.maintcal.overridesView = function (model, schedule_view) {
    this.schedule_view = schedule_view;
    this.doc = model;
    this.addEvents({
        dataerror: true
    });
    this.hasBeenExpanded = false;
    this.gridSelectionModel = new Ext.grid.CheckboxSelectionModel();
    this.loadTask = new Rack.app.maintcal.overrides.load(this,this.doc);

    var config = {
            ds: this.doc,
            columns: [
                this.gridSelectionModel,
                {
                    dataIndex: 'name',
                    resizable: false,
                    hideable: false
                }
            ], 
            sm: this.gridSelectionModel,
            frame: true,
            viewConfig: {forceFit: true},
            autoScroll: true,
            animCollapse: false,
            trackMouseOver: false,
            id: 'overridesView_id',
            title: 'Override Calendars'
        };

    Ext.grid.GridPanel.call(this, config);
    // add Listeners
    this.on('dataerror', this.showDataError, this);
    this.on('beforeexpand', this.checkRequireds, this);
    this.on('expand', this.getData, this);

};

Ext.extend(Rack.app.maintcal.overridesView, Ext.grid.GridPanel, {

    noServiceTypeError : "You must select a service type.",

    noDevicesError : "You must select at least one device.",

    maskThis: function (verbage) {
        if (!this.body.isMasked()) {
            this.body.mask(verbage);
        }
    },

    unmaskThis: function () {
        if (this.body.isMasked()) {
            this.body.unmask();
        }
    },

    getData : function () {
        this.hasBeenExpanded = true;
        this.maskThis.defer(1,this,['Loading ...']);
        this.loadTask.start();
    },

    checkRequireds : function () {
        // function to ensure that devices and a service type exist 
        // before trying to call the calendar selector.
        if(!this.schedule_view.selectedServiceTypeRecord) {
            this.showUIError(this.noServiceTypeError);
            return false
        }
        if(!this.schedule_view.selectedDevices.length) {
            this.showUIError(this.noDevicesError);
            return false
        }
        return true
    },

    showUIError : function (msgText){
        this.body.unmask();
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgText,
                buttons: Ext.MessageBox.OK,
                width: 250
        });
    },

    showDataError : function (msgText){
        this.body.unmask();
        Ext.MessageBox.show({
                title: 'Alert',
                fn: globalCloseWindow,
                msg: msgText,
                buttons: Ext.MessageBox.OK,
                width: 250
        });
    },

    getSelecteds : function (){
        var currentSelections = this.gridSelectionModel.getSelections();
        var current_calendars = [];
        for(var i=0;i < currentSelections.length;i++){
           current_calendars.push(currentSelections[i].get('id')); 
        }
        return current_calendars;
    }

});

