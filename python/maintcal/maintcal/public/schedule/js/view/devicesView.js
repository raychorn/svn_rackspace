/*extern Ext, Rack */

Rack.app.maintcal.devicesView = function (model, ticket_number) {
    this.doc = model;
    this.addEvents({
        focusdevices : true,
        unregister : true
    });
    this.moreDevicesFired = false;
    this.lastScrollValue = 0;
    this.deviceBehindFired = false;
    this.attachedManagedStorageFired = false;
    this.allAttachedDevices = [];
    this.hasPaged = false;
    this.hasBeenExpanded = false;
    this.lastSelected = false;
    this.gv = new Ext.grid.GridView(this.viewConfig);
    this.loadDevices = new Rack.app.maintcal.devices.load(this.doc);
    this.loadAllDevicesTask = new Rack.app.maintcal.devices.pagedLoad(this.doc); 
    this.gridSelectionModel = new Ext.grid.CheckboxSelectionModel();
    this.moreDevicesLimit = 4;

    this.maskText = "Getting Devices ...";

    this.moreDevicesWarning = "You have included 4 or more servers in this " +
                        "request. Please contact the associated groups to" +
                       " confirm the appropriate time required to complete " +
                       "this maintenance. Please increase the maintenance " +
                       "duration to accommodate the extra servers.";
    
    this.loadAllErrorText = "There has been an error while trying to get data. " +
                        "Please try reloading the page again.";

    this.deviceBehindText =  "One or more of these devices has other devices " +
                            "behind them. Would you like to add these devices now ?" +
                            "( Managed Storage devices will be added automatically. )";

    var config = {
            ds: this.doc,
            columns: [
                this.gridSelectionModel,
                {
                    dataIndex: 'server_url',
                    width: 45,
                    renderer: this.renderServerNumber,
                    resizable: false,
                    fixed: true,
                    hideable: false
                }, {
                    sortable: false,
                    resizable: false,
                    fixed: true,
                    width: 25,
                    renderer: this.renderIcon,
                    dataIndex: 'icon'
                }, {
                    sortable: false,
                    resizable: false,
                    fixed: true,
                    width: 171,
                    dataIndex: 'name'
                }
            ],
            sm: this.gridSelectionModel,
            view: this.gv,
            frame: true,
            autoScroll: true,
            animCollapse: false,
            trackMouseOver: false,
            title: 'Selected Devices',
            id: 'deviceView_id',
            tools: [{id: 'gear',
                    //tooltipType: 'qtip',
                    qtip: 'Click to view all Account Devices',
                    handler: this.showAllServers,
                    scope: this
            }]
        };
    
    Ext.grid.GridPanel.call(this, config);
    // add Listeners
    this.on('expand', this.checkReMask, this);
    this.gridSelectionModel.on('rowselect', this.rowListener, this);
    this.doc.on('load',this.handleLoad,this);
    this.doc.on('dataerror',this.showDataError,this);
    this.on('render', this.handleLoad, this);
    this.doc.on('unregister',this.unregisterPaging,this);
};

Ext.extend(Rack.app.maintcal.devicesView, Ext.grid.GridPanel, {

    maskThis: function (verbage) {
        // remask the control if necessary
        if (!this.body.isMasked()) {
            this.body.mask(verbage);
        }
        else {
            this.body.unmask();
            this.body.mask(verbage);
        }
    },
    unmaskThis: function () {
        if (this.body.isMasked()) {
            this.body.unmask();
        }
    },
    checkReMask : function () {
        if (this.body.isMasked() && this.doc.connection.isLoading()) {
            this.maskThis.defer(1,this,[this.maskText]);
        }
    },
    unregisterPaging : function () {
        this.un('bodyscroll',this.lazyLoadRecords,this);
    },
    selectAll : function () {
        this.gridSelectionModel.selectAll();
    },
    handleLoad : function () {
        this.gridSelectionModel.suspendEvents();
        // this method pre-checks for moreDevices limits and attached devices,
        // after a load, as the 'rowselect' event only appears to fire once.
        var recordsToSelect = [];
        var recordsToSelectWithAttachments = [];
        this.recordsToSelectWithAttachments = [];
        this.localAttachedDevices = [];
        this.remoteAttachedDevices = [];
        var hasManagedStorageDevices = [];
        this.doc.each(function(r) {
            if ( r.get('is_selected') ) {
                recordsToSelect.push(r);
                if ( r.get('attached_devices').length >= 1 ) {
                    recordsToSelectWithAttachments.push(r)
                }
            }
            if ( r.get('has_managed_storage') ) {
                hasManagedStorageDevices.push(r.id); 
            }
        });
        this.recordsToSelectWithAttachments = recordsToSelectWithAttachments;
        this.gridSelectionModel.selectRecords(recordsToSelect,true);

        if ( this.gridSelectionModel.getSelections().length >=
            this.moreDevicesLimit && !this.moreDevicesFired ) {
            Ext.MessageBox.alert('WARNING', this.moreDevicesWarning,
                this.handleLoad,this);
            this.moreDevicesFired = true;
            // try and unmask in case coming back from a non-initial call.
            this.unmaskThis();
            return true
        }
            /*this.gridSelectionModel.selectFirstRow();
            var nextRecord = this.gridSelectionModel.selectNext(true);
            var selectionCount = 1;
            while (nextRecord) {
                selectionCount++;
                if ((selectionCount >= this.moreDevicesLimit) && 
                    !this.moreDevicesFired) {
                    
                }
                nextRecord = this.gridSelectionModel.selectNext(true);
                
            } */
        var c;
        for (c=0; c < recordsToSelectWithAttachments.length; c++){
            var r = recordsToSelectWithAttachments[c];
            var theseDevices = r.get('attached_devices');
            if (theseDevices.length >= 1) {
                var a;
                for (a=0; a < theseDevices.length; a++) {
                    var testLocal = this.doc.getById(theseDevices[a]);
                    if (testLocal) {
                        this.localAttachedDevices.push(testLocal);
                    }
                    else {
                        if ( this.remoteAttachedDevices.indexOf(theseDevices[a]) === -1) {
                            this.remoteAttachedDevices.push(theseDevices[a]);
                        }
                    }
                }
                
            }
        } 
        if ((hasManagedStorageDevices.length >= 1) && (!this.attachedManagedStorageFired)) {
            this.attachedManagedStorageFired = true;
            this.body.mask(this.maskText);
            this.loadDevices.start(hasManagedStorageDevices,true)
            this.unmaskThis();
        }
        if ( this.localAttachedDevices.length >= 1) {
            this.gridSelectionModel.suspendEvents();
            this.gridSelectionModel.selectRecords(this.localAttachedDevices,true);
            this.gridSelectionModel.resumeEvents();
        }
        
        if (((this.remoteAttachedDevices.length >= 1) ||
             (this.localAttachedDevices.length >= 1)) && 
            (!this.deviceBehindFired) &&
             (this.recordsToSelectWithAttachments.length >= 1))  {
            Ext.MessageBox.confirm('ALERT', this.deviceBehindText,
                                    this.handleAddDeviceBehind, this);
            this.deviceBehindFired = true;
            this.gridSelectionModel.resumeEvents();
            // try and unmask in case coming back from a non-initial call.
            this.unmaskThis();
            return true
        }
        this.gridSelectionModel.resumeEvents();
        this.gv.refresh();
        this.unmaskThis();
    },
    /*filterTicketOnlyDevices : function () {
        this.doc.filter('is_in_ticket', 'true');
        this.gridSelectionModel.selectAll();
    },*/
    /*findDevicesByAttachments : function () {
        this.gridSelectionModel.suspendEvents();
        var sldvs = this.gridSelectionModel.getSelections();
        this.doc.each(function(r, i, l){
            sldvs.each();
    },*/
    /*addRowSelectListener : function () {
        if (!this.hasBeenExpanded) {
            this.hasBeenExpanded = true;
            var currentSelections = this.gridSelectionModel.getSelections();
            var cs;
            for (cs = 0; cs < currentSelections.length; cs++) {
                this.gridSelectionModel.fireEvent('rowselect', this.gridSelectionModel,
                                    currentSelections[cs].id, currentSelections[cs]);
            }
        }
    },*/
    rowListener : function (sm, i, r) {
        if ((this.gridSelectionModel.getCount() >= this.moreDevicesLimit) &&
            !this.moreDevicesFired) {
            Ext.MessageBox.alert('WARNING', this.moreDevicesWarning);
            this.moreDevicesFired = true;
        }
        if (r.data.attached_devices.length !== 0) {
            this.localAttachedDevices = [];
            this.remoteAttachedDevices = [];
            var b;
            var theseDevices = r.data.attached_devices;
            for ( b=0; b < theseDevices.length; b++) {
                var testLocal = this.doc.getById(theseDevices[b]);
                if ( testLocal ) {
                    this.localAttachedDevices.push(testLocal);
                }
                else {
                    this.remoteAttachedDevices.push(theseDevices[b]);
                }
            }
            Ext.MessageBox.confirm('ALERT', this.deviceBehindText,
                                    this.handleAddDeviceBehind, this);

        }
        return true       
    },
    handleAddDeviceBehind : function (id) {
        if (id === "yes") {
            this.fireEvent('focusdevices', this);
                        // var thisBody = this.getBody();
            if ( this.remoteAttachedDevices.length >= 1 ) {
                this.body.mask(this.maskText);
                //var devicesArray = this.lastSelected.data.attached_devices;
                this.loadDevices.start(this.remoteAttachedDevices);
            }
            if ( this.localAttachedDevices.length >= 1) {
                this.gridSelectionModel.suspendEvents();
                this.gridSelectionModel.selectRecords(this.localAttachedDevices,true);
                this.gridSelectionModel.resumeEvents();
            }
            /*var dBehindCollection = this.doc.queryBy(function (r, i) {
                    var da;
                    for (da = 0;da < devicesArray.length; da++) {
                        if (r.json.id === devicesArray[da]) {
                            return true;
                        }
                    }
                    return false;
                   
                });
            if (dBehindCollection.getCount() !== 0) {

                dBehindCollection.addAll(this.gridSelectionModel.getSelections());
                this.doc.filterBy( function (r,i) {
                    var db;
                    for (db = 0;db < dBehindCollection.getCount(); db++) {
                        if (dBehindCollection.contains(r)) {
                            return true;
                        }
                        
                    }
                    return false;
                });
                var gv = this.getView();
                gv.refresh();
                this.gridSelectionModel.selectRecords(dBehindCollection.getRange(), true);
            }*/
            //this.gridSelectionModel.resumeEvents();
            /*if ((this.gridSelectionModel.getCount() >= this.moreDevicesLimit) &&
                !this.moreDevicesFired) {
                Ext.MessageBox.alert('WARNING', this.moreDevicesWarning);
                this.moreDevicesFired = true;
            }*/
        }
        else {
            // dont do jack.
        }
    },
    lazyLoadRecords : function (l,t) {
        // the total height of the scrolled area.
        var totalHeight = this.gv.scroller.dom.scrollHeight;
        // the viewable area height.
        var vHeight = this.gv.scroller.getHeight();
        // number of pixels to start the load before the 
        // bottom of the view. 
        var buffer = 100;
        // grid panels bottom
        // grid panels body height
        // don't page unless within buffer pixels and don't page going
        // backwards.
        if ((t+vHeight > totalHeight-buffer) && t >= this.lastScrollValue) {
            // don't try and re-query if the task is already in progress
            if (this.doc.connection.isLoading()) {
                this.doc.loader_paused = true;
                this.body.mask(this.maskText);
                return false
            }
            else {
                this.body.mask(this.maskText);
                this.doc.loadFromCache();
            } 
        };
        this.lastScrollValue = t;
    },
    renderServerNumber : function (val) {
        try{
            var parts = val.split('/');
        } catch (e) {
            var parts = [];
        }
        if (parts.length > 3) {
            /* in new ui device number is always at last so last element can be safely assumed as device number */
            return '<a href="javascript:loadParent(' + "'"  + val + "'" + 
                    ',0,1)">' + parts[parts.length - 1] + '</a>';
        }
        else {
            return 'Not Available';
        }
    },
    renderIcon : function (val) {
        if (val) {
            return '<img src="' + val + '" />';
        }
        else {
            return '<img src="" />';
        }
    },
    showAllServers : function () {
        //var thisBody = this.getBody();
        this.on('bodyscroll',this.lazyLoadRecords,this);
        this.body.mask(this.maskText);
        this.loadAllDevicesTask.start(this.doc.schedule_doc.account_number,
            this.doc.currentPage,this.doc.pagedDevicesLimit);
    },
    showDataError : function (r) {
        Ext.getBody().unmask();
        var msgResponse = this.genericDataErrorText;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText !== 'undefined') {
                msgResponse = parseWSGIError(r.responseText);
            }
            
        }
        // handle recoverable errors
        if (r.status === 404) {
            Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: this.recoverAfterError,
                scope: this,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
        }
        else {
            Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
        }
    },
    recoverAfterError : function () {
        // other things might be required here.
        this.unmaskThis();
    }
});

