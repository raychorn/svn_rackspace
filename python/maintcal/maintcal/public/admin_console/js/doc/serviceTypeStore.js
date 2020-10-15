/*extern Ext, Rack */

// add a namespace to the standard EXTJS GroupStore.
Ext.namespace('Rack.app.maintcal.serviceTypeStore');

Rack.app.maintcal.serviceTypeStore = function() {
    Ext.data.GroupingStore.call(this);
    this.connection = new Ext.data.Connection({timeout: 60000});
    this.addEvents({
        loaderror:true,
        updateerror:true,
        updatecomplete:true
    });
    // used for determining if all updates were completed.
    this.currentUpdateCount = 0;
    this.currentConfirmCount = 0; 
};

Ext.extend(Rack.app.maintcal.serviceTypeStore, Ext.data.GroupingStore,{
    groupField:'maintenance_category',
    sortInfo: {
        field:"id",
        direction:"ASC"
    },
    reader:new Ext.data.JsonReader({
        idProperty:'id',
        fields: [
            {name: 'maintenance_category_id', type: 'int'},
            {name: 'maintenance_category', type: 'string'},
            {name: 'id', type: 'int'},
            {name: 'description', type: 'string'},
            {name: 'name', type: 'string'},
            {name: 'length_hours', type: 'float'},
            {name: 'lead_time_hours', type: 'float'},
            {name: 'modification_contact', type: 'string'},
            {name: 'active', type: 'bool'}
        ]

    }),
    //demo only method
    /*
    handleDemoResponse:function(r,o){
        //var json = r.responseText;
        //var o = eval("("+json+")");
        var o = r;
        if(!o) {
            throw "handleResponse: Json object not found";
        }
        if(o.metaData){
            delete this.reader.ef;
            this.reader.meta = o.metaData;
            this.reader.meta.sortInfo = this.sortInfo;
            this.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            this.reader.onMetaChange(this.reader.meta, this.reader.recordType, o);
            this.loadData(o);
        }
    },
    */
    handleLoadResponse:function(r,o){
        var json = r.responseText;
        var o = eval("("+json+")");
        if(!o) {
            throw "handleResponse: Json object not found";
        }
        if(o.metaData){
            delete this.reader.ef;
            this.reader.meta = o.metaData;
            this.reader.meta.sortInfo = this.sortInfo;
            this.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            this.reader.onMetaChange(this.reader.meta, this.reader.recordType, o);
            this.loadData(o);
        }
    },

    handleLoadError: function(){
        this.fireEvent('loaderror',this);
    },

    handleUpdateSuccess:function(r,o){
        var json = r.responseText;
        var o = eval("("+json+")");
        if(!o) {
            throw "handleResponse: Json object not found";
        }
        var task = new Rack.app.maintcal.serviceTypeStore.update(null,this);
        if (typeof o === "number") {
            task.confirmUpdate(o);
        } else {
            throw "updateSuccess: Received a non-integer from server";
        }
    },

    handleUpdateFailure: function(r){
        this.fireEvent('updateerror',this,r);
    },

    handleConfirmFailure: function(r){
         this.fireEvent('updateerror',this,r);
    },

    handleConfirmResponse: function(r,o){
        var json = r.responseText;
        var o = eval("("+json+")");
        if(!o) {
            throw "handleResponse: Json object not found";
        }
        if(o.metaData){
            delete this.reader.ef;
            this.reader.meta = o.metaData;
            this.reader.meta.sortInfo = this.sortInfo;
            this.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            this.reader.onMetaChange(this.reader.meta, this.reader.recordType, o);
            var jsonRecords = this.reader.readRecords(o);
            var recordToRemove = this.findBy(function(r){
                if(!r.hasOwnProperty('json') || r.json.id === o.rows[0].id){
                    return true;
                } else {
                    return false;
                }
            });
            this.remove(this.getAt(recordToRemove));
            this.addSorted(jsonRecords.records[0]);
        } else {
            throw "handleResponse: no metadata in object";
        }
        if(this.currentUpdateCount == this.currentConfirmCount + 1){
            this.currentUpdateCount = 0;
            this.currentConfirmCount = 0;
            this.fireEvent('updatecomplete',this);
        } else {
            this.currentConfirmCount +=1;
        }
   }
});
