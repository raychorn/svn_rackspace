/*extern Ext, Rack, parseWSGIError */

Rack.app.maintcal.serviceTypesView = function (model) {
    this.doc = model;
    this.groupViewTemplate = '{text} ({[values.rs.length]}' +
                        '{[values.rs.length > 1 ? " Items" : " Item"]})';

    this.loadAllErrorText = 'There has been an error while trying to get data. ' + 
                    'Please try reloading the page again.';

    this.GroupingView = new Ext.grid.GroupingView({
        showGroupName: false,
        forceFit: true,
        enableNoGroups: false, // REQUIRED!
        hideGroupedColumn: true,
        startCollapsed: true,
        groupTextTpl: this.groupViewTemplate
                    
    });
    var config = {
        ds: this.doc,
        columns: [{
            id: 'id',
            header: "Service Type",
            dataIndex: 'name',
            width: 60,
            renderer: this.stypeRenderer,
            resizable: false,
            hideable: false
        }, {
            header: "Length",
            dataIndex: 'length_hours',
            sortable: false,
            resizable: false,
            width: 15,
            hideable: false
        },{
            header: "Lead",
            dataIndex: 'lead_time_hours',
            sortable: false,
            resizeable: false,
            width: 15,
            hideable: false
        },{
            header: "Category",
            sortable: false,
            dataIndex: 'maintenance_category',
            resizable: false
        }],
        view: this.GroupingView,
        id: 'serviceTypesView_id',
        frame: true,
        animCollapse: false,
        trackMouseOver: false,
        title: 'Maintenance Category with Service Types'
    };    
    Ext.grid.GridPanel.call(this, config);     
};

Ext.extend(Rack.app.maintcal.serviceTypesView, Ext.grid.GridPanel, {

    filterByDeviceSegment : function (segment) {
        this.doc.filter('maintenance_category', segment);
        this.GroupingView.refresh();
    },

    setW : function () {
        this.setWidth(281);
    },

    stypeRenderer : function (val,metadata,record,rowIdx,colIdx,store) {
        return_string = val
        if (val.length > 28) {
            return "<span title='" + val + "'>" + 
                Ext.util.Format.ellipsis(val,28) + "</span>"
        }
        else {
            return val
        }
    }

}); 

