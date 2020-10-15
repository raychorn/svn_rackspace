/*extern Ext, Rack, tznames */

Rack.app.maintcal.pickerWidget = Ext.extend(Ext.Container,{

    autoEl : 'div',

    width : 262,

    disabled : false,

    disabledClass : '',

    loadTask : false,

    initComponent : function() {
        Rack.app.maintcal.pickerWidget.superclass.initComponent.call(this);
        this.addEvents({
            'valid'     : true,
            'invalid'   : true,
            'change'    : true,
            'fetchdata' : true,
            'loaddata'  : true
        });
        switch(this.editorType) {
            case "tz" :
                this.pickerUI = new Rack.app.maintcal.tzPicker({
                    title : 'Select a Timezone',
                    closeAction : 'hide',
                    encodeValue : false
                });
                break;

            case "queue":
                this.pickerUI = new Rack.app.maintcal.queuePicker({
                    closeAction : 'hide'
                });
                break;

            case "category":
                this.pickerUI = new Rack.app.maintcal.categoryPicker({
                    closeAction : 'hide'
                });
                break;

        }
        if(this.editorType === "tz") {
            // need to init a custom store for tz data.
            this.PickerData =  new Ext.data.Store({
                reader: new Ext.data.JsonReader({
                    idProperty: 'id',
                    fields : [
                        {name: 'id', type : 'string'},
                        {name: 'name', type : 'string'}]
                }),
                sortInfo:{field: 'name', direction: "DSC"}
            });
        }
        else {
            this.PickerData =  new Ext.data.Store({
                reader: new Ext.data.JsonReader({
                    idProperty: 'id',
                    fields : [
                        {name: 'id', type : 'int'},
                        {name: 'name', type : 'string'},
                        {name: 'group_letter', type : 'string' }
                    ]
                }),
                sortInfo:{field: 'name', direction: "DSC"}
            });
        }
        this.editorWidget = new Ext.form.ComboBox({
            store : this.PickerData,
            mode : 'local',
            hideTrigger : true,
            cls : 'mc-mark-dirty',
            triggerAction : 'all',
            listWidth : this.width,
            disabled : this.disabled,
            typeAhead : true,
            allowBlank : !this.required,
            valueField : "id",
            valueNotFoundText : "Not set",
            blankText : "This option is required.",
            displayField : "name"
        });
               
        this.pickerUI.on('picked',this.setValue,this);
        this.editorWidget.on('change',this.fireChangeEvent,this);
        this.value = this.editorWidget.getValue;
        this.initUsePickerLabel();
        if(this.disabled){
            this.usePicker.disable();
        }
        this.add(this.editorWidget);
        this.add(this.usePicker);
        this.on('render',this.doAfterRender,this);
        if(this.loadTask){
            this.loadTask.on('dataloaded',this.loadData,this);
        };
        this.on('fetchdata',this.fetch,this);
        // set a default value if one is specified
        // needs to be run after data is loaded.
        /*if (this.defaultValue) {
            this.setValue(this.defaultValue);
            this.editorWidget.originalValue = this.defaultValue;
        }*/
        // value of the Queue to which this picker is bound.
        this._pickerQueueID = 0;
    },

    initUsePickerLabel : function() {
        var labelValue = '<a href="javascript:' + 
                    '(function(){return})();" >' +
                    'use Picker </a>';
        var disabledValue = '<span class="x-item-disabled">use Picker</span>';
        this.usePicker = new Rack.app.maintcal.Label({
            enableClick : true,
            disabledText : disabledValue,
            cls : 'use-picker-button',
            html : labelValue
        });
    }, 

    fetch : function(queue_id) {
        this.markLoading();
        // check to see if this is a tz picker.
        // if so data is directly loaded.
        if(this.editorType === "tz"){
            this.loadData();
            return;
        }
        // set this instances' _pickerQueueID
        this._pickerQueueID = queue_id;
        this.loadTask.start(queue_id);
    },

    loadData : function(obj) {
        var val;
        switch(this.editorType) {
            case "tz" :
                var rArray = [];
                for (var i in tznames) {
                    var j;
                    for (j=0;j<tznames[i].length;j++) {
                        var safe_val = [i,'/',tznames[i][j]].join('');
                        val = [i,'/',tznames[i][j].replace(/_/,' ')].join('');
                        rArray.push({'name':val,'id':safe_val});
                    }
                }
                this.PickerData.loadData(rArray);
                break;
            case "queue" :
                var all_queues = [];
                for ( val in obj ) {
                    all_queues.push({'id' : obj[val],
                                     'name' : val,
                                     'group_letter' : val.charAt(0)
                                    }); 
                }
                this.pickerUI.thisPicker.queueStore.loadData(all_queues);
                this.PickerData.loadData(all_queues);
                break;
            case "category" :
                var these_cats = [];
                obj = obj[this._pickerQueueID]
                // check to see if the dataloaded event has the
                // _pickerQueueID we are interested in.
                if(obj === undefined){
                    return;
                }
                for (var k=0; k < obj.length; k++) {
                    var cat_name = [obj[k][1],'/',obj[k][3]].join('');
                    these_cats.push({'id' : obj[k][2],
                                     'name' : cat_name,
                                     'category_id' : obj[k][0],
                                     'category_name' : obj[k][1],
                                     'subcategory_letter' : obj[k][3].charAt(0)
                                    }); 
                }
                this.pickerUI.thisPicker.categoryStore.loadData(these_cats);
                this.PickerData.loadData(these_cats);
                break;
        }
        if (this.hasOwnProperty('defaultValue')) {
            this.setOriginalValue(this.defaultValue);
        }
    },

    /*flattenZonename : function() {
        var rArray = [];
        for (var i in tznames) {
            var j;
            for (j=0;j<tznames[i].length;j++) {
                var val = [i,'/',tznames[i][j].replace(/_/,/ /)].join('');
                rArray.push({name:val,id:val});
            }
        }
        return rArray
    },*/

    /*transformQueueData : function() {
        var rArray = [];
        for (var i in this.dataStruct) {
            rArray.push([this.dataStruct[i].name,this.dataStruct[i].id]);
        }
        return rArray

    },

    transformCategoryData : function() {
        var rArray = [];
        for (var i in this.dataStruct) {
            rArray.push([this.dataStruct[i].subcategory_name,this.dataStruct[i].subcategory_name]);
        }
        return rArray


    },*/

    fireChangeEvent : function(combo,new_value,old_value) {
        this.editorWidget.suspendEvents();
        this.fireEvent('change',new_value);
        this.editorWidget.resumeEvents();

    },
    doAfterRender : function() {
        this.usePicker.on('click',this.showPicker,this);
        this.editorWidget.on('valid',this.fireValid,this);
        this.editorWidget.on('invalid',this.fireInvalid,this);
    },

    setValue : function(arg) {
        this.editorWidget.suspendEvents();
        if (this.PickerData.getCount() > 0) {
            this.editorWidget.setValue(arg);
            this.editorWidget.markDirty();
            this.fireEvent('change',this,arg);
        }
        this.usePicker.enable();
        this.editorWidget.resumeEvents();
    },

    setOriginalValue : function(arg) {
        this.editorWidget.setOriginalValue(arg);
        this.editorWidget.enable();
        this.usePicker.enable();
    },

    markLoading : function() {
        this.editorWidget.disable();
        this.usePicker.disable();
    },

    getValue : function() {
        return this.editorWidget.getValue();
    },

    fireValid : function() {
        this.fireEvent('valid');
    },

    fireInvalid : function() {
        this.fireEvent('invalid');
    },

    validate : function() {
        return this.editorWidget.validate();
    },

    showPicker : function() {
        this.pickerUI.show();
    },

    isDirty : function() {
        return this.editorWidget.isDirty();
    },

    reset : function() {
        this.editorWidget.reset();
    }
});

    
