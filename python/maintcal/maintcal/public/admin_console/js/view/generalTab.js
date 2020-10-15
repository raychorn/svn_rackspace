/*extern Ext, Rack, gem, global_doc, global_view */

Ext.namespace('Rack.app.maintcal.generalTab');

Rack.app.maintcal.generalTab = Ext.extend(Ext.Panel, {

    data : {},

    name : 'Calendar',

    autoScroll : true,

    initComponent : function () {
        Rack.app.maintcal.generalTab.superclass.initComponent.call(this);

        this.html = this.drawThyself();
        
        // a convenience array to store all the editors in. Instead of having to iterate over items and identify 
        // an 'editor' widget.
        this.editors = [];

        this.addEvents({
            bodyupdate: true
        });
        this.catLoadTask = global_doc.catLoadTask;
        this.statLoadTask = global_doc.statLoadTask;
        this.updateCalendarTask = 
            new Rack.app.maintcal.adminConsole.updateCalendars(this,global_doc);
        this.on('bodyupdate',this.loadEditables,this);
        global_doc.on('calendarloaded',this.refreshView,this);

    },

    drawThyself : function () {
        var outs = [
        '<div class="col-1-1">',
        '<table class="mc-calendar-detail">',
            '<tr><th colspan="3">' + this.name + '</th></tr>',
            '<tr>',
                '<td class="mc-c-detail-label">Name:</td>',
                '<td id="name_edit_container_' + this.id + '" class="mc-c-detail-data">',
               '</td>',
                '<td class="mc-c-detail-edit">',
                '</td>',
            '</tr>',
            '<tr>',
                '<td class="mc-c-detail-label">Description:</td>',
                '<td id="desc_edit_container_' + this.id + '" class="mc-c-detail-data">',
               '</td>',
                '<td class="mc-c-detail-edit">',
                '</td>',
            '</tr>',
            '<tr>',
                '<td class="mc-c-detail-label">Time Zone:</td>',
                '<td id="zone_editor_' + this.id + '" class="mc-c-detail-data"',
                '</td>',
            '</tr>',
            '<tr>',
                '<td class="mc-c-detail-label">CATS Queue Reference:</td>',
                '<td id="queue_editor_' + this.id + '" class="mc-c-detail-data"',
                '</td>',
                '</tr></table>',
            '</div>',
            '<div class="col-1-2">',
            '<table class="mc-calendar-detail">',
                '<tr><th>Active</th></tr>',
                    '<td id="mc_calendar_activator_' + this.id + '" class="mc-c-detail-data"></td>',
            '</tr></table>',
            '</div><div class="clear" />',
            '<div class="col-2-2">',
            '<table class="mc-calendar-detail">',
            '<tr>',
            '<th colspan="2">Maintenance Ticket Creation</th></tr>',
            '<tr>',
                '<td class="mc-c-detail-label">Queue:</td>',
                '<td id="new_tckt_queue_editor_' + this.id + '" class="mc-c-detail-data">',
                '</td></tr>',
                '<tr>',
                '<td class="mc-c-detail-label">Queue Sub-Category:</td>',
                '<td id="new_tckt_category_editor_' + this.id + '" class="mc-c-detail-data">',
                '</td></tr>',
                '<td class="mc-c-detail-label">Status:</td>',
                '<td id="new_tckt_status_container_' + this.id + '" class="mc-c-detail-data">',
                '</td>',
            '</tr></table></div>',
            '<div class="col-1-2">',
            '<table class="mc-calendar-detail">',
            '<tr>',
            '<th colspan="2">Time Before Ticket Refresh</th></tr>',
            '<tr>',
                '<td class="mc-c-detail-label">Hours:</td>',
                '<td id="refresh_delta_container_' + this.id + '" class="mc-c-detail-data">',
                '</td><tr></table>',
            '</div>',
            '<div class="clear" />',
            '<div class="col-2-2">',
            '<table class="mc-calendar-detail">',
            '<tr>',
            '<th colspan="2">Maintenance Ticket Refresh</th></tr>',
            '<tr>',
                '<td class="mc-c-detail-label">Queue:</td>',
                '<td id="refresh_tckt_queue_editor_' + this.id + '" class="mc-c-detail-data">',
                '</td></tr>',
                '<tr>',
                '<td class="mc-c-detail-label">Queue Sub-Category:</td>',
                '<td id="refresh_tckt_category_editor_' + this.id + '" class="mc-c-detail-data">',
                '</td></tr>',
                '<td class="mc-c-detail-label">Status:</td>',
                '<td id="refresh_tckt_status_container_' + this.id + '" class="mc-c-detail-data">',
                '</td>',
            '</tr></table></div>',
            '<div class="col-1-2">',
            '<table class="mc-calendar-detail">',
            '<tr>',
            '<th colspan="2">Unassign Ticket on Refresh ?</th></tr>',
            '<tr>',
                '<td id="refresh_assignment_container_' + this.id + '" class="mc-c-detail-label"> </td>',
                '<td class="mc-c-detail-note">',
                'Uncheck to keep the current ticket owner, check to unassign ticket on refresh.',
                '</td><tr>',
            '</div>'
            ];
        return outs.join("");
    },

    loadEditables : function() {
        this.activate = new Ext.form.Checkbox({
            checked : this.data.active,
            dataKey : 'active',
            disabled : !this.data.is_admin,
            renderTo: 'mc_calendar_activator_' + this.id
        });
        this.editors.push(this.activate);

        this.nameEdit = new Ext.form.TextField({
            name: 'name-edit-field',
            allowBlank : false,
            cls : 'mc-mark-dirty',
            dataKey : 'name',
            blankText : "Calendar Name cannot be blank",
            value: this.data.name,
            editable: false,
            disabled : !this.data.is_admin,
            width: this.data.name.length * 9,
            renderTo: 'name_edit_container_' + this.id
        });
        this.editors.push(this.nameEdit);

        this.descEdit = new Ext.form.TextField({
            name: 'desc-edit-field',
            allowBlank : true,
            cls : 'mc-mark-dirty',
            dataKey : 'description',
            value : this.data.description,
            editable: false,
            disabled : !this.data.is_admin,
            width: this.data.description.length.toString() * 9,
            renderTo : 'desc_edit_container_' + this.id
        });
        this.editors.push(this.descEdit);
        
        this.queuePicker = new Rack.app.maintcal.pickerWidget({
            editorType: 'queue',
            cls : 'edit-container',
            dataKey : 'tckt_queue_id',
            loadTask : global_view.loadQueueDataTask,
            defaultValue : this.data.tckt_queue_id,
            disabled : !this.data.is_admin,
            required : false,
            renderTo : 'queue_editor_' + this.id
        });
        this.queuePicker.fetch();
        this.editors.push(this.queuePicker);

        this.newQueuePicker = new Rack.app.maintcal.pickerWidget({
            editorType : 'queue',
            cls : 'edit-container',
            dataKey : 'new_ticket_queue_id',
            loadTask : global_view.loadQueueDataTask,
            defaultValue : this.data.new_ticket_queue_id,
            disabled : !this.data.is_admin,
            required : false,
            renderTo : 'new_tckt_queue_editor_' + this.id
        });
        this.newQueuePicker.on('change',this.loadNewPickerData,this);
        this.newQueuePicker.fetch();
        this.editors.push(this.newQueuePicker);

        this.refreshQueuePicker = new Rack.app.maintcal.pickerWidget({
            editorType : 'queue',
            cls : 'edit-container',
            dataKey : 'refresh_ticket_queue_id',
            loadTask : global_view.loadQueueDataTask,
            defaultValue : this.data.refresh_ticket_queue_id,
            disabled : !this.data.is_admin,
            required : false,
            renderTo : 'refresh_tckt_queue_editor_' + this.id
        });
        this.refreshQueuePicker.on('change',this.loadRefreshPickerData,this);
        this.refreshQueuePicker.fetch();
        this.editors.push(this.refreshQueuePicker);

        this.newCatPicker = new Rack.app.maintcal.pickerWidget({
            editorType : 'category',
            cls : 'edit-container',
            dataKey : 'new_ticket_category_id',
            loadTask : this.catLoadTask,
            defaultValue : this.data.new_ticket_category_id,
            disabled : !this.data.is_admin,
            required : false,
            renderTo : 'new_tckt_category_editor_' + this.id
        });
        this.editors.push(this.newCatPicker);
        this.newCatPicker.fetch(this.data.new_ticket_queue_id);

        this.refreshCatPicker = new Rack.app.maintcal.pickerWidget({
            editorType : 'category',
            cls : 'edit-container',
            dataKey : 'refresh_category_id',
            loadTask : this.catLoadTask,
            defaultValue : this.data.refresh_category_id,
            disabled : !this.data.is_admin,
            required : false,
            renderTo : 'refresh_tckt_category_editor_' + this.id
        });
        this.editors.push(this.refreshCatPicker);
        this.refreshCatPicker.fetch(this.data.refresh_ticket_queue_id);

        this.tzPicker = new Rack.app.maintcal.pickerWidget({
            editorType: 'tz',
            cls : 'edit-container',
            dataKey : 'timezone',
            defaultValue : this.data.timezone,
            disabled : !this.data.is_admin,
            required : false,
            renderTo : 'zone_editor_' + this.id
        });
        this.tzPicker.fetch(); // the tzPicker doesn't require passed data.
        this.editors.push(this.tzPicker);

        this.newStatusSelector = new Rack.app.maintcal.statusPicker({ 
            disabled : !this.data.is_admin,
            value : this.data.new_ticket_status_id,
            loadTask : this.statLoadTask,
            dataKey : 'new_ticket_status_id',
            tabId: this.id,
            renderTo : 'new_tckt_status_container_' + this.id
        });
        this.editors.push(this.newStatusSelector);
        this.newStatusSelector.fetch(this.data.new_ticket_queue_id);

        this.refreshDelta =  new Ext.form.TextField({
            name : 'book-edit-field',
            allowBlank: false,
            cls : 'mc-mark-dirty',
            dataKey : 'time_before_ticket_refresh',
            value : this.data.time_before_ticket_refresh,
            defaultValue: this.data.time_before_ticket_refresh,
            editable : false,
            disabled : !this.data.is_admin,
            width : 36,
            renderTo : 'refresh_delta_container_' + this.id,
            vtype : 'delta'
        });
        this.editors.push(this.refreshDelta);

        this.serviceAssignment = new Ext.form.Checkbox( {
            checked : this.data.refresh_ticket_assignment,
            dataKey : 'refresh_ticket_assignment',
            disabled : !this.data.is_admin,
            renderTo: 'refresh_assignment_container_' + this.id
        });
        this.editors.push(this.serviceAssignment);

        this.refreshStatusSelector = new Rack.app.maintcal.statusPicker({ 
            dataKey : 'refresh_status_id',
            disabled : !this.data.is_admin,
            loadTask : this.statLoadTask,
            value : this.data.refresh_status_id,
            tabId: this.id,
            renderTo : 'refresh_tckt_status_container_' + this.id
        });
        this.editors.push(this.refreshStatusSelector);
        this.refreshStatusSelector.fetch(this.data.refresh_ticket_queue_id)
        
        var calendar_id_only = this.id.slice(12);
        global_view.fireEvent('contentready',calendar_id_only);

        /*//this.newStatusSelector.select(0);
        if(this.data.is_admin) {
            var edit_els = this.body.select("a.modal-editor-handler");
            edit_els.on('click',this.handleEdit,this);
        }*/
    },

    // override the default Panel afterRender to be able to fire bodyupdate
    // event. 
    afterRender : function(){
        Rack.app.maintcal.generalTab.superclass.afterRender.call(this);
        this.fireEvent('bodyupdate',this);
    },

    loadNewPickerData : function() {
        var queue_id = this.newQueuePicker.getValue();
        this.newCatPicker.fetch(queue_id);
        this.newStatusSelector.fetch(queue_id);
    },

    loadRefreshPickerData : function() {
        var queue_id = this.refreshQueuePicker.getValue();
        this.refreshCatPicker.fetch(queue_id);
        this.refreshStatusSelector.fetch(queue_id);
    },

    save : function() {
        // although referencing el directly can be a bad idea, this el is 
        // always going to be present at this point.
        var cal_id = this.id.slice(12);
        global_view.center.el.mask('Saving ...');
        var update_params = {};
        var editor_count = 0;
        for(var i=0;i<this.editors.length;i++) {
            var edit_ref = this.editors[i];
            if(!edit_ref.validate()){
                global_view.center.el.unmask();
                edit_ref.focus();
                return;
            }
            if (edit_ref.hasOwnProperty('dataKey') && edit_ref.isDirty()) {
                update_params[edit_ref.dataKey] = edit_ref.getValue();
                editor_count++;
            }
        }
        if(editor_count === 0){
            global_view.center.el.unmask();
            global_view.handleDataError("Nothing to Save.");
        }
        else {
            this.updateCalendarTask.start(cal_id,update_params);
        }
    },

    revert : function() {
        var i;
        for(i=0;i<this.editors.length;i++) {
            var edit_ref = this.editors[i];
            edit_ref.reset();
        }
    },

    checkIsDirty : function() {
        var i;
        for (i=0;i<this.editors.length;i++) {
            var edit_ref = this.editors[i];
            if (edit_ref.isDirty()) {
                return true;
            }
        }
        return false;
    },

    markClean : function() {
        this.revert();
    },

    refreshView : function(cal_id) {
        var this_cal_id = this.id.slice(12);
        // this message isn't meant for us.
        if(this_cal_id !== cal_id) {
            return;
        }; 
        for(var i=0;i<this.editors.length;i++) {
            var edit_ref = this.editors[i];
            var cal_data = global_doc.calendarData[cal_id];
            var orig_value = cal_data[edit_ref['dataKey']];
            edit_ref.setOriginalValue(orig_value);
        };
        if (global_view.center.el.isMasked()) {
            global_view.center.el.unmask();
        };

    }

    /*handleEdit : function(e) {
        // put ids on each target and handlers here.
        var tgt = e.getTarget('',10,true);
        if (tgt.id === 'queue_editor_' + this.id) {
            this.queuePicker.show();
        }

        if (tgt.id === 'category_editor_' + this.id) {
            this.catPicker.show();
        }

        if (tgt.id === 'zone_editor_' + this.id) {
            this.tzPicker.show();
        }

    }*/

});

