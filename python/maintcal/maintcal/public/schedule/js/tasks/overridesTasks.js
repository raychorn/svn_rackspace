/**
*   It looks like this task invokes the calendar selector.
*/

Rack.app.maintcal.overrides.load = function (overrides_view, model) {

    this.doc = model;
    this.view = overrides_view;
    
    this.start = function () {
        this.doc.connection.request({
                url: '/maintcal/calendars/selector.json',
                method: 'POST',
                success: this.handleLoadResponse,
                failure: this.handleLoadError,
                scope: this, 
                params: {
                    category_id : this.view.schedule_view.selectedServiceTypeRecord.get('maintenance_category_id'), 
                    service_id : this.view.schedule_view.selectedServiceTypeRecord.get('id'),
                    servers : this.view.schedule_view.selectedDevices
                }
 
            });
    };

    this.handleLoadResponse = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            this.view.handleLoadError(r);
            throw "handleResponse: Json object not found";
        }
        if (o.metaData) {
            delete this.doc.reader.ef;
            this.doc.reader.meta = o.metaData;
            this.doc.reader.meta.sortInfo = this.doc.sortInfo;
            this.doc.reader.recordType = Ext.data.Record.create(o.metaData.fields);
            //  TODO: replace bare model reference with this.doc 
            this.doc.reader.onMetaChange(model.reader.meta, model.reader.recordType, o);
            this.doc.loadData(o);
        }
        // check for inability to select default calendars
        if(this.doc.getAt(1).get('is_error')) {
            this.view.showUIError("Unable to select default calendars");
        }
        // get records with is_selected = True
        var default_calendars = this.doc.queryBy(
            function(r) {
                if(r.get('is_selected')){
                    return true
                }
            });
        // cast the Ext.MixedCollection into an array.
        var default_calendars_array = [];
        default_calendars.each(
            function (item,idx,len){
                default_calendars_array.push(item);
            });
        // set these records as selected.
        this.view.gridSelectionModel.selectRecords(default_calendars_array);
        /*var default_calendars_count = default_calendars.getCount();
        for(var i;i<default_calendars_count;i++){
            this.view.gridSelectionModel.selectRow(i);
        }*/
        // bad, bad code ...
        /*default_calendars.each(
            function (item,idx,len){
                this.view.gridSelectionModel.selectRow(idx);
        });*/ 
        // unmask the document
        this.view.unmaskThis();
    };

    this.handleLoadError = function (r) {
        this.view.showDataError(r.responseText);
    };

};

