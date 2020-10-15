/*extern Ext, Rack, parseWSGIError */

Rack.app.maintcal.queuePickerGrid = function () {

    this.groupViewTemplate = '{text} ({[values.rs.length]}' +
                        '{[values.rs.length > 1 ? " Items" : " Item"]})';

    this.GroupingView = new Ext.grid.GroupingView({
        showGroupName: false,
        forceFit: true,
        startCollapsed : true,
        enableNoGroups: false, // REQUIRED!
        hideGroupedColumn: true,
        groupTextTpl: this.groupViewTemplate
                    
    });
    
    // setup the store
    this.queueStore = new Ext.data.GroupingStore({
                reader: new Ext.data.JsonReader({
                    idProperty: 'id',
                    fields : [
                        {name: 'id', type : 'int'},
                        {name: 'name', type : 'string'},
                        {name: 'group_letter', type : 'string' }
                    ]
                }),
                sortInfo:{field: 'name', direction: "DSC"},
                groupField:'group_letter'
        });
    var config = {
        store: this.queueStore,
        columns: [{
            header: "Enter a Queue Name by picking it from the list.",
            dataIndex: 'name',
            renderer: this.valueRenderer,
            resizable: false,
            hideable: false
        },{
            sortable: false,
            dataIndex: 'group_letter',
            resizable: false
        }],
        autoShow : true,
        view: this.GroupingView,
        frame: true
    };
    Ext.grid.GridPanel.call(this, config);
    // enable typeAhead browsing.
    this.taTask = new Ext.util.DelayedTask(this.onTypeAhead,this);
    this.currentQuery = '';

};

Ext.extend(Rack.app.maintcal.queuePickerGrid, Ext.grid.GridPanel, {

    valueRenderer : function (val,metadata,record,rowIdx,colIdx,store) {
        if (record.get('interal') === 2) {
            val = val + '<span class="mc-qp-subLabel"> (Internal) </span>';
        }
        return val; 
    }

    /*onKeyUp : function(e) {
        if(e.isChar) {
            this.currentQuery = this.currentQuery + e.getkey();
            var resIdx = this.queueStore.find('name',this.currentQuery,0);
            if (resIdx !== -1) {
                this.GroupingView.focusRow(resIdx);
                return
            }
        }
        var k = e.getKey();
        else if (k === this.RETURN) {

        }

    }*/


}); 

Rack.app.maintcal.queuePicker = Ext.extend(Ext.Window, {

    height : 420,

    width : 680,

    modal: true,

    draggable : false,

    layout : 'fit',

    closable : false,

    scrollable : true,

    resizable: false,

    initComponent : function() {

        Rack.app.maintcal.queuePicker.superclass.initComponent.call(this);
        this.addEvents({
            picked : true
        });
        this.thisPicker = new Rack.app.maintcal.queuePickerGrid();
        this.thisPicker.on('celldblclick',this.handleSelectAndClose,this);
        //this.thisPicker.on('cellclick',this.handleSelect,this);
        this.on('show',this.addPicker,this);
        this.addButton('OK',this.handleOK,this);
        this.addButton('Cancel',this.handleCancel,this);

    },

    handleSelectAndClose : function(g,r,c,e) {
        e.stopEvent();
        var sm = this.thisPicker.getSelectionModel();
        var val = sm.getSelected();
        if (val) {
            this.fireEvent('picked',val.get('id'));
            this.hide();
        }
    },

    handleOK : function() {
        var sm = this.thisPicker.getSelectionModel();
        var val = sm.getSelected();
        if (val) {
            this.fireEvent('picked',val.get('id'));
            this.hide();
        }
        else {
            Ext.MessageBox.show({
                title:'Alert',
                msg: "Please pick a queue",
                buttons: Ext.MessageBox.OK,
                width:250
            });
        }

    },

    handleCancel : function() {
        // this might require other sorts of cleanup actions
        this.hide();
    },

    addPicker : function() {
        
        this.add(this.thisPicker);
        this.doLayout();
        //window.addEventListener("keyup",this.onKeyUp,false);
        //this.thisPicker.GroupingView.focusRow(0);
        //this.thisPicker.autoHeight();
    }
});



