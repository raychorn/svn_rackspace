/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.statusPicker');

Rack.app.maintcal.statusPicker = Ext.extend(Ext.form.ComboBox, {
        
        mode: 'local',

        loadTask : false,

        allowBlank : false,

        displayField: 'name',

        cls : 'mc-mark-dirty',

        valueField: 'id',

        listWidth: 200,

        disabled : false,

        triggerAction: 'all',

        forceSelection: true,

        editable: false,

        value : 0,

        valueNotFoundText : "Not set", 

        dataKey : '',

        renderTo : '',
  
        _pickerQueueID : 0, 
             
        initComponent : function () {
            Rack.app.maintcal.statusPicker.superclass.initComponent.call(this);
            if(this.loadTask){
                this.loadTask.on('dataloaded',this.loadStatusData,this);
            }
            this.store = new Ext.data.Store({
                reader : new Ext.data.JsonReader({
                    idProperty: 'id',
                    fields : [
                        {name : 'name', type :'string'},
                        {name : 'id', type : 'int'}
                    ]
                })
            }),

            this.store.on('load',this.handleLoaded,this);
        },

        fetch : function(queue_id) {
            this._pickerQueueID = queue_id;
            this.disable();
            this.loadTask.start(queue_id);
        },

        loadStatusData : function(statusObj) {
            // check to see if the event that triggered this load
            // is one we are interested in.
            obj = statusObj[this._pickerQueueID];
            if(obj === undefined){
                return;
            }
            // obj is all status data.
            this.store.loadData(obj);
        },
        
        handleLoaded : function() {
            var cal_id = this.tabId.slice(12);
            this.setOriginalValue(global_doc.calendarData[cal_id][this.dataKey]);
            this.enable();

        }

}); 
