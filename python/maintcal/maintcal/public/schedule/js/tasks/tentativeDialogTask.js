/**
*
*/

Rack.app.maintcal.gatherTentativeDialog = function (schedule_view) {

    this.start = function () {
        var fstring = [];
        fstring.push('<div class="mc-sv-tentative-text">You have selected');
        fstring.push(' <span>' + 
               schedule_view.selectedServiceTypeRecord.json.name + '</span> ');
        if (schedule_view.selectedDevices.length > 1) {
            fstring.push('for <span>' +
                    schedule_view.selectedDevices.length + '</span> devices');
        }
        else {
            fstring.push('for a <span>single</span> device');
        }
        fstring.push('</div>');
        fstring.push(
                '<div class="mc-sv-tentative-text">Total length of maintenance: ');
        if (schedule_view.selectedServiceTypeRecord.json.length_hours !== 1) {
            fstring.push('<span>' +
                   schedule_view.selectedServiceTypeRecord.json.length_hours +
                   ' hours<span>'); 
        }
        else {
            fstring.push('<span>1 hour</span>');
        }
        fstring.push('</div>');
        fstring.push('<div class="mc-sv-tentative-text">Lead time required: ');
        if (schedule_view.options.expediteCheckBox.getValue()) {
            fstring.push('<span class="mc-sv-tentative-ex">Expedite</span>');
        }
        else {
            if (schedule_view.selectedServiceTypeRecord.json.lead_time_hours !== 1) {
                fstring.push('<span>' + 
                    schedule_view.selectedServiceTypeRecord.json.lead_time_hours +
                    ' hours</span>');
            }
            else {
                fstring.push('<span> 1 hour</span>');
            }
        }
        return fstring.join('');
    };
};

Rack.app.maintcal.validateContact = function (tentativeDialog_view) {
    this.start = function () {
        tentativeDialog_view.contactInfoLabel.setText('Verifying this Username ...');
        tentativeDialog_view.schedule_view.doc.connection.request({
            url: '/maintcal/maintenances/checkValidUserName',
            method: 'POST',
            success: this.contactValid,
            failure: this.handleError,
            scope: this,
            params: {
                user_string : tentativeDialog_view.contactField.getValue()
            }
        });
    };
    this.contactValid = function (r) {
        tentativeDialog_view.contactInfoLabel.setText('Valid Contact');
        tentativeDialog_view.contactIsDirty = false;
    };
    this.handleError = function (r) {
        if (r.responseText) {
            tentativeDialog_view.contactInfoLabel.setText(parseWSGIError(r.responseText));
        }
        else {
            tentativeDialog_view.contactInfoLabel.setText("Unknown error occured");
        }
        tentativeDialog_view.contactField.setValue(tentativeDialog_view.schedule_view.doc.contact);
        tentativeDialog_view.contactIsDirty = false;
    };
};

Rack.app.maintcal.updateMaintenanceDescriptions = function (tentativeDialog_view) {
    this.POSTsuccesses = 0;
    this.calendarCount = tentativeDialog_view.calendarTabs.items.getCount();

    //  Use the schedulingView's document for communication.

    this.start = function () {

        Ext.getBody().mask('Scheduling Maintenance ...', '', 10000);

        var tzvalue = tentativeDialog_view.schedule_view.currentTZ; 
        if (tentativeDialog_view.schedule_view.doc.selectedZoneName) {
            tzvalue = tentativeDialog_view.schedule_view.doc.selectedZoneName;
        }

        var params_obj = {};

        //  Get the time in seconds from UTC

        var start_tuple = tentativeDialog_view.selected_time.get('start_tuple');

        params_obj.start_year                   = start_tuple[0]; // year
        params_obj.start_month                  = start_tuple[1]; // month
        params_obj.start_day                    = start_tuple[2]; // day
        params_obj.start_hour                   = start_tuple[3]; // hour
        params_obj.start_minute                 = start_tuple[4]; // minute
        params_obj.is_dst                       = start_tuple[9]  // dst_flag

        params_obj.tzname                       = tzvalue;

        params_obj.contact                      = tentativeDialog_view.contactField.getValue();
        params_obj.description                  = tentativeDialog_view.generalNotes.getValue();

        params_obj.contactCustomerBefore        = tentativeDialog_view.contactCustomerBeforeField.getValue();
        params_obj.contactCustomerAfter         = tentativeDialog_view.contactCustomerAfterField.getValue();
        params_obj.contactCustomerName          = tentativeDialog_view.contactCustomerNameField.getValue();
        params_obj.contactCustomerInfo          = tentativeDialog_view.contactCustomerInfoField.getValue();
        params_obj.contactCustomerDepartment    = tentativeDialog_view.contactCustomerDepartmentField.getValue();

        tentativeDialog_view.schedule_view.doc.connection.request({
            url:        '/maintcal/maintenances/schedule/' + tentativeDialog_view.schedule_view.doc.maintenance_id,
            method:     'POST',
            success:    this.postServiceDescriptions,
            failure:    function() { var scope = tentativeDialog_view.schedule_view; tentativeDialog_view.schedule_view.showDataError.apply(scope, arguments); },
            scope:      this,
            params:     params_obj
                
        });       
    };

    this.postServiceDescriptions = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            this.fireEvent('dataerror', this, r);
            throw "postServiceDescriptions: Json object not found";
        }
        var t;
        var service_id = '';
        for (t = 0; t < tentativeDialog_view.calendarTabs.items.getCount(); t++) {
            if (! o[tentativeDialog_view.calendarTabs.items.item(t).calendar_id]) {
                var error = "Cannot find a service that matches calendar id:" + 
                    tentativeDialog_view.calendarTabs.items.item(t).calendar_id;
                tentativeDialog_view.schedule_view.showDataError(error);
                return;
            }
            else {
                service_id =  o[tentativeDialog_view.calendarTabs.items.item(t).calendar_id];
            }
            tentativeDialog_view.schedule_view.doc.connection.request({
                url: '/maintcal/services/update/' + service_id, // need to calendar_id to services_map here instead.
                method: 'POST',
                success: this.collectAndConfirm,
                failure: this.handleFailure, 
                scope: this,
                params: {
                    description: tentativeDialog_view.calendarTabs.items.item(t).getValue()
                }
            });
                
        }

    };
    this.handleScheduleFailure = function (r){
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
        if (r.status == 409) {            
            Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: this.reCalcAvailTimes,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
        }
        else {
            tentativeDialog_view.doc.fireEvent('dataerror',r);
        }
    };
    
    this.reCalcAvailTimes = function (r){
        tentativeDialog_view.close();
        tentativeDialog_view.schedule_view.sendMaintenanceData();               
    };
    
    this.handleFailure = function(r) {
        tentativeDialog_view.doc.fireEvent('dataerror',r);
    };
    
    this.collectAndConfirm = function (r) {
        this.POSTsuccesses++;
        if (this.POSTsuccesses === this.calendarCount) {
            tentativeDialog_view.hide();
            tentativeDialog_view.confirmMaintenance();
            return 1;
        }
    };
};

Rack.app.maintcal.cancelMaintenance = function (model) {

    this.start = function (maintenance_tab_id,cancelReasonText) {
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Canceling Maintenance ...');
        var requestConfig = {
            url: '/maintcal/maintenances/cancel/' + model.maintenance_id,
            method: 'POST',
            success: this.handleSuccessCancel,
            failure: this.showDataError,
            scope: this
        };
       // make the request either with or without a reason if present.
        if (cancelReasonText.length >= 1) {
            requestConfig.params = {cancel_message: cancelReasonText};
        }
            
        model.connection.request(requestConfig);
        model.maintenance_id = null;
    };

    this.showDataError = function (r) {
        var msgResponse;
        if (typeof r === "string") {
            msgResponse = r;
        }
        else {
            if (typeof r.responseText === 'undefined') {
                msgResponse = this.genericDataErrorText;
            }
            else {
                msgResponse = parseWSGIError(r.responseText);
            }
        }
        this.viewBody.unmask();
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    };

    this.handleSuccessCancel = function () {
        this.viewBody.unmask();
    };
};

