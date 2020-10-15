/*extern Ext, Rack, parseWSGIError, globalCloseWindow, global_view, notImplemented */

Ext.namespace('Rack.app.maintcal.eGroupingView');
Ext.namespace('Rack.app.maintcal.serviceTypeAdminView');
Ext.namespace('Rack.app.maintcal.checkColumn');

Rack.app.maintcal.checkColumn = new Ext.grid.CheckColumn({
                            header: "Active",
                            dataIndex: 'active',
                            width: 15 });


Rack.app.maintcal.eGroupingView = Ext.extend(Ext.grid.GroupingView,{

    initComponent : function() {
        Rack.app.maintcal.eGroupingView.superclass.initComponent.call(this);
        this.addEvents({'grouptoggle' : true});
    },

    toggleGroup : function(group, expanded){
        this.grid.stopEditing();
        group = Ext.getDom(group);
        var gel = Ext.fly(group);
        expanded = expanded !== undefined ?
                expanded : gel.hasClass('x-grid-group-collapsed');

        this.state[gel.dom.id] = expanded;
        gel[expanded ? 'removeClass' : 'addClass']('x-grid-group-collapsed');
        var gidArray = this.humanizeGid(gel.dom.id);
        this.fireEvent('grouptoggle',gidArray[0],gidArray[1]);
    },

    humanizeGid : function(gid) {
        var grpFld =  this.getGroupField();
        var beginSliceIdx = gid.indexOf(grpFld);
        var endSliceIdx = beginSliceIdx + grpFld.length + 1;
        var groupString = gid.slice(endSliceIdx);
        return [grpFld,groupString];
        
    }
});

Rack.app.maintcal.serviceTypeAdminView =  Ext.extend(Ext.grid.EditorGridPanel, {

    columns: [
    {
        id: 'id',
        header: "Service Type",
        dataIndex: 'name',
        width:55,
        renderer : function(val) {
            if (val.length > 40) {
                return "<span title='" + val + "'>" + 
                    Ext.util.Format.ellipsis(val,40) + "</span>";
            }
            else {
                return val;
            }
        },
        resizable:false,
        hideable: false,
        editor: new Ext.form.TextField({
            allowBlank: false
        })
    },{
        header: "Category",
        sortable: false,
        dataIndex: 'maintenance_category'
    },
        /* Service Categories are deprecated.
        {
        header: "Service Category",
        resizable:false,
        width:30,
        sortable: false,
        dataIndex: 'service_category',
        editor: new Ext.form.TextField({
            allowBlank: false
        })
    },*/
    {
        header: "Length",
        sortable: false,
        width:20,
        dataIndex: 'length_hours',
        renderer : function(v){
            if(v !== 1) {
                return v + ' hours';
            }
            else {
                return v +' hour';
            }
        },
        editor: new Ext.form.TextField({
                allowBlank: false,
                vtype: 'delta'
            })
    },{
        header: "Lead Time",
        sortable: false,
        width:20,
        dataIndex: 'lead_time_hours',
        renderer : function(v) {
            if(v !== 1){
                return v + ' hours';
            }
            else {
                return v +' hour';
            }
        },
        editor: new Ext.form.TextField({
            allowBlank: false,
            vtype: 'delta'
        })
    },{
        header:"Modified By",
        width:30,
        sortable:false,
        dataIndex:'modification_contact',
        groupable:false
    },Rack.app.maintcal.checkColumn],
    view: new Rack.app.maintcal.eGroupingView({
            showGroupName: false,
            forceFit:true,
            enableNoGroups:false, // REQUIRED!
            hideGroupedColumn: true,
            startCollapsed:true,
            groupTextTpl: '{text} ({[values.rs.length]}' +
                        '{[values.rs.length > 1 ? " Items" : " Item"]})'
    }),

    frame: true,

    clicksToEdit: 2,

    animCollapse: false,

    trackMouseOver: false,

    plugins: Rack.app.maintcal.checkColumn,

    addSTText :'Add Service Type',

    noSelectedSTError : 'You must select a category before you can add a' + 
                        ' service type',

    loadAllErrorText: 'There has been an error while trying to get data. ' + 
                    'Please try reloading the page again.',

    updateErrorText: 'There has been an error while trying to save your ' + 
                    'changes. Please try reloading the page and saving again.',

    initComponent : function() {

        this.tbar = [{
            text : 'New Maintenance Category',
            // deactivate for iteration 1. 
            // handler: this.addMaintenanceCategory,
            handler : notImplemented,
            scope : this
        },'-',{
            text : 'Add Service Type',
            handler : this.addServiceType,
            scope : this
        }];

        Rack.app.maintcal.serviceTypeAdminView.superclass.initComponent.call(this);
        this.doc.on('load',this.showServiceTypes,this);
        this.doc.on('loadexception',this.showLoadError,this);
        this.doc.on('loaderror',this.showLoadError,this);
        this.doc.on('updateerror',this.showUpdateError,this);
        this.doc.on('updatecomplete',this.unmaskThis,this);
        this.view.on('grouptoggle',this.handleGroupToggle,this);
    },
    /* deprecated
    getGroupingView : function(){
            return new Ext.grid.GroupingView({
                showGroupName: false,
                forceFit:true,
                enableNoGroups:false, // REQUIRED!
                hideGroupedColumn: true,
                startCollapsed:true,
                groupTextTpl: this.groupViewTemplate
            });
    },
    */
    handleGroupToggle : function(groupField,groupName) {
        var grpFirstIdx = this.doc.find(groupField,groupName);
        if (grpFirstIdx !== -1) {
            this.lastGrpIndex = grpFirstIdx;
        }
    },

    showServiceTypes : function() {
        this.ct.add(this);
        this.show();
        this.unmaskThis();
        this.ct.layout.setActiveItem(this.id);

    },

    save:function(){
        var modifieds = this.doc.getModifiedRecords();
        if (modifieds.length === 0) {
            Rack.msg('','Nothing to be saved');
        }
        else {
            var task = new Rack.app.maintcal.serviceTypeStore.update(this,this.doc);
            task.start();
        }
    },

    reset:function(){
        var task = new Rack.app.maintcal.serviceTypeStore.reset(this,this.doc);
        task.start();
    },

    addMaintenanceCategory : function(){
        Ext.MessageBox.prompt('Category','Enter a new Category',
            function(b,t){
                if (b === "ok") {
                    if (this.doc.find('maintenance_category',t,0) === -1) {
                        var p = new Ext.data.Record({
                            name: 'New Service Type',
                            maintenance_category:t,
                            service_category:'General',
                            length_hours:0,
                            lead_time_hours:0,
                            modification_contact:'System Administrator'
                        });
                        this.stopEditing();
                        this.doc.addSorted(p);
                        this.startEditing(0, 0);
                    }
                    else {
                        Ext.MessageBox.alert("New Categories must be unique.");
                    }
                }
            },this);
    },

    addServiceType:function(){
        if(typeof this.lastGrpIndex === 'undefined'){
            Ext.MessageBox.show({
                title:'Alert',
                msg:this.noSelectedSTError,
                buttons: Ext.MessageBox.OK,
                width:250
            });
        }
        else{
            var s = this.getStore();
            var robj = s.getAt(this.lastGrpIndex);
            var p = new Ext.data.Record({
                name: 'New Service Type',
                maintenance_category: robj.get('maintenance_category'),
                maintenance_category_id : robj.get('maintenance_category_id'),
                length_hours:0,
                lead_time_hours:0,
                active : false
            });
            this.stopEditing();
            this.doc.insert(this.lastGrpIndex, p);
            //this.doc.groupBy('maintenance_category',true);
            this.startEditing(this.lastGrpIndex, 0);
        }
    },
    // not sure when this was used. Not correct either way.
    /*
    onPageLoad: function(){
        var task = new Rack.app.maintcal.stadmin.loadDemo(this,this.doc);
        task.start();
    },
    */
    maskThis: function(verbage){
        global_view.center.el.mask(verbage);
        //this.ct.body.mask(verbage);
    },

    unmaskThis: function(){
        global_view.center.el.unmask();
        //this.ct.body.unmask();
    },
     
    showLoadError:function(d,r){
        this.unmaskThis();
        Ext.MessageBox.show({
                title: 'Alert',
                msg: parseWSGIError(r.responseText),
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });

    },

    showUpdateError:function(d,r){
        this.unmaskThis();
        Ext.MessageBox.show({
                title:'Alert',
                msg: parseWSGIError(r.responseText),
                buttons: Ext.MessageBox.OK,
                width:250
            });

    }

});
