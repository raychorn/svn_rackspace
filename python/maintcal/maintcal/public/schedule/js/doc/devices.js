/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.devices');

Rack.app.maintcal.devices = function (schedule_model) {
    Ext.data.Store.call(this);
    this.connection = new Ext.data.Connection({timeout: 60000});
    this.addEvents({
        dataready: true,
        widgetready: true,
        dataerror: true,
        unregister : true
    });
    this.localDataCache = null;
    this.currentPage = 1;
    this.pagedDevicesLimit = 200;
    this.loader_paused = false;
    this.schedule_doc = schedule_model;
    this.on('dataready', this.onPageLoad);
    this.on('load', this.fireReady);

};

Ext.extend(Rack.app.maintcal.devices, Ext.data.Store, {
    reader: new Ext.data.JsonReader({
        idProperty: 'id',
        fields: [
            {name: 'id', type: 'int'},
            {name: 'os', type: 'string'},
            {name: 'icon', type: 'string'},
            {name: 'datacenter', type: 'string'},
            {name: 'name', type: 'string'},
            {name: 'segment', type: 'string'},
            {name: 'has_managed_storage', type: 'string'},
            {name: 'managed_storage_type', type: 'string'},
            {name: 'has_managed_backup', type: 'string'},
            {name: 'attached_devices', type: 'string'},
            {name: 'is_in_ticket', type: 'boolean'}
        ]

    }),
    onPageLoad: function (e, devices) {
        var task = new Rack.app.maintcal.devices.load(this);
        task.start(devices);
    },
    handleLoadResponse: function (r) {
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
            this.loadData(o,true);
        }
    },
    loadFromCache : function () {
        // try and load data from the local cache, if fail, fetch next page
        // of records.
        var o = this.localDataCache;
        if (o.metaData) {
            delete this.reader.ef;
            this.reader.meta = o.metaData;
            this.reader.meta.sortInfo = this.sortInfo;
            this.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            this.reader.onMetaChange(this.reader.meta, this.reader.recordType, o);
            this.loadData(o,true);
        }
        if (o.results < this.pagedDevicesLimit) {
            this.fireEvent('unregister',this);
        } 
        else {
            var cacheTask = new Rack.app.maintcal.devices.pagedLoad(this);
            cacheTask.start(this.schedule_doc.account_number,this.currentPage,
                this.pagedDevicesLimit);
        }
    
    },
    handlePagedResponse: function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            this.fireEvent('dataerror', this, r);
            throw "handleResponse: Json object not found";
        }
        
        if (o.metaData) {
            // check to see if this is the first time called.
            if (!this.localDataCache) {
                this.localDataCache = o;
                this.currentPage++;
                this.loadFromCache();
            }
            else {
                if (this.loader_paused) {
                    this.localDataCache = o;
                    this.currentPage++;
                    this.loader_paused = false;
                    this.loadFromCache();
                }
                else {
                    this.localDataCache = o;
                    this.currentPage++;
                    //this.loadFromCache();
                }
            }
        }
                
    },
    fireReady : function () {
        this.fireEvent('widgetready',this);
        // this method takes out all listed attached devices that are not in the 
        // entire device list.
        /*var allDeviceIDs = [];
        for (var di = 0;di < this.data.items.length;di++) {
            allDeviceIDs.push(this.data.items[di].data.id);
        }
        this.each(function (r) {
                var thisAttachedDevices = r.data.attached_devices.split(',');
                var parsed;
                r.data.attached_devices = [];
                var ad;
                for (ad = 0;ad < thisAttachedDevices.length;ad++) {
                    parsed = parseInt(thisAttachedDevices[ad], 10);
                    if (allDeviceIDs.indexOf(parsed) > -1) {
                        r.data.attached_devices.push(parsed);
                    }
                }
            });*/
        //this.fireEvent('widgetready', this);
    },
    handleLoadError: function (r) {
        this.fireEvent('dataerror', r);
    }
    
});

