/**
*
*/
Rack.app.maintcal.loadMaintenanceView = function (maintenance_view) {

    this.start = function () {
        this.maintenance_view = maintenance_view;
        this.viewBody = Ext.get(document.body);

        if (this.viewBody) {
            this.viewBody.mask('Loading ...');
        }

        this.maintenance_id = getURLParam('mid');
        this.service_id = getURLParam('sid');
        if (!this.maintenance_id) {
            this.showDataError("no maintenance id found in the URL parameters.");
        }
        this.maintenance_view.connection.request({
                url: '/maintcal/maintenances/' + this.maintenance_id +
                    '.sjson?tzname=' + maintenance_view.currentTZ,
                method: 'GET',
                success: this.populateViews,
                failure: this.showDataError,
                scope: this
            });
    };

    this.populateViews = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            this.showDataError("populateViews: Json object not found");
            throw "populateViews: Json object not found";
        }

        if (o.maintenance_id && isArray(o.devices) && isArray(o.services)) {
            this.maintenance_view.maintenance_id = o.maintenance_id;
            maintenance_view.composeAndAdd(o, this.service_id);
        } else {
            this.showDataError("Data structure is missing key components");
        }
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
        if (this.viewBody.isMasked()) {
            this.viewBody.unmask();
        }
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    };
};

Rack.app.maintcal.cancelMaintenance = function (maintenance_view) {

    this.start = function (cancelReasonText) {
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Canceling Maintenance ...');
        var requestConfig = {
            url: '/maintcal/maintenances/cancel/' + maintenance_view.maintenance_id,
            method: 'POST',
            success: this.handleSuccessCancel,
            failure: this.showDataError,
            scope: this
        };
        // make the request either with or without a reason if present.
        if (cancelReasonText.length >= 1) {
            requestConfig.params = {cancel_message: cancelReasonText};
        }
            
        maintenance_view.connection.request(requestConfig);
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
        loadParent('',0,1);

        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Maintenance has been successfully cancelled.',
            fn: globalCloseWindow,
            buttons: Ext.MessageBox.OK,
            width: 250
        });
    };
};

Rack.app.maintcal.cancelService = function (maintenance_view) {
    this.start = function (service_id, panel_ref, reasons, cancelReasonText) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Canceling Service ...');
        var requestConfig = {
            url: '/maintcal/services/cancel/' + service_id,
            method: 'POST',
            success: this.handleSuccessCancel,
            failure: this.showDataError,
            scope: this
        };
        // make the request either with or without a reason if present.
        if (cancelReasonText != null && cancelReasonText.length >= 1) 
            requestConfig.params = {cancel_message: cancelReasonText,
                                    'reasons': reasons};
        else
            requestConfig.params = {'reasons': reasons};
        maintenance_view.connection.request(requestConfig);

    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
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
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    };

    this.handleSuccessCancel = function (r) {
        this.viewBody.unmask();
        loadParent('',0,1);
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been successfully canceled.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };

    this.modifyServicePanelState = function () {
        this.viewBody.unmask();
        var json = this.successResponse;
        var o = eval("(" + json + ")");
        if (!o.status_type) {
            this.showDataError("modifyServicePanelState: Json object not found");
        }
        if (o.status_type === 'maintenance') {
            Ext.MessageBox.show({
                title: 'Notice',
                msg: 'The last service on this maintenance has been canceled. The maintenance will be canceled.',
                fn : globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });

        }
        else {
            if (o.status_id) {
                this.panel_ref.dataObj = Ext.apply(this.panel_ref.dataObj,o);
                this.panel_ref.decorateServicePanel();
                globalCloseWindow(); //closes maintenance calendar
            }
            else {
                this.showDataError("Data structure is missing key components");
            }
            
        }        
    };
};

Rack.app.maintcal.completeService = function (maintenance_view) {
    this.start = function (service_id, panel_ref) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Completing Service ...');
        maintenance_view.connection.request({
            url: '/maintcal/services/complete/' + service_id,
            method: 'POST',
            success: this.handleSuccessComplete,
            failure: this.showDataError,
            scope: this
        });
    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
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
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    };

    this.handleSuccessComplete = function (r) {
        this.viewBody.unmask();
        loadParent('',0,1);
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been successfully completed.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };
 
    this.modifyServicePanelState = function () {
        this.viewBody.unmask();
        var json = this.successResponse;
        var o = eval("(" + json + ")");
        if (!o.status_type) {
            this.showDataError("modifyServicePanelState: Json object not found");
        }
        if (o.status_type === 'maintenance') {
            Ext.MessageBox.show({
                title: 'Notice',
                msg: 'The last service on this maintenance has been completed. The maintenance will be completed.',
                fn : globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });

        }
        else {
            if (o.status_id) {
                this.panel_ref.dataObj = Ext.apply(this.panel_ref.dataObj,o);
                this.panel_ref.decorateServicePanel();
                globalCloseWindow(); //closes maintenance calendar
            }
            else {
                this.showDataError("Data structure is missing key components");
            }
            
        }
    };
};


Rack.app.maintcal.completeServiceWithIssues = function (maintenance_view) {
    this.start = function (service_id, panel_ref, reasons, feedback) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Completing Service ...');
        var requestConfig = {
            url: '/maintcal/services/completeWithIssues/' + service_id,
            method: 'POST',
            success: this.handleSuccessComplete,
            failure: this.showDataError,
            scope: this
        };
        if (feedback != null && feedback.length >= 1) 
            requestConfig.params = {feedback: feedback,
                                    'reasons': reasons};
        else
            requestConfig.params = {'reasons': reasons};
        maintenance_view.connection.request(requestConfig);

    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
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
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    };

    this.handleSuccessComplete = function (r) {
        this.viewBody.unmask();
        loadParent('',0,1);
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been successfully completed.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };
 
    this.modifyServicePanelState = function () {
        this.viewBody.unmask();
        var json = this.successResponse;
        var o = eval("(" + json + ")");
        if (!o.status_type) {
            this.showDataError("modifyServicePanelState: Json object not found");
        }
        if (o.status_type === 'maintenance') {
            Ext.MessageBox.show({
                title: 'Notice',
                msg: 'The last service on this maintenance has been completed. The maintenance will be completed.',
                fn : globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });

        }
        else {
            if (o.status_id) {
                this.panel_ref.dataObj = Ext.apply(this.panel_ref.dataObj,o);
                this.panel_ref.decorateServicePanel();
                globalCloseWindow(); //closes maintenance calendar
            }
            else {
                this.showDataError("Data structure is missing key components");
            }
            
        }
    };
};

Rack.app.maintcal.unsuccessfulService = function (maintenance_view) {
    this.start = function (service_id, panel_ref, reasons, feedback) {
        this.panel_ref = panel_ref;
        this.viewBody = Ext.get(document.body);
        this.viewBody.mask('Completing Service ...');
        var requestConfig = {
            url: '/maintcal/services/unsuccessful/' + service_id,
            method: 'POST',
            success: this.handleUnsuccessful,
            failure: this.showDataError,
            scope: this
        };
        if (feedback != null && feedback.length >= 1) 
            requestConfig.params = {feedback: feedback,
                                    'reasons': reasons};
        else
            requestConfig.params = {'reasons': reasons};
        maintenance_view.connection.request(requestConfig);

    };

    this.showDataError = function (r) {
        this.viewBody.unmask();
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
        Ext.MessageBox.show({
                title: 'Alert',
                msg: msgResponse,
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    };

    this.handleUnsuccessful = function (r) {
        this.viewBody.unmask();
        loadParent('',0,1);
        if (typeof r.responseText === 'undefined') {
            this.showDateError("There has been an error getting status information");
            return
        }
        else  {
            this.successResponse = r.responseText;
        }
        Ext.MessageBox.show({
            title: 'Success',
            msg: 'This Service has been failed.',
            fn : this.modifyServicePanelState,
            buttons: Ext.MessageBox.OK,
            width: 250,
            scope : this
        });
    };
 
    this.modifyServicePanelState = function () {
        this.viewBody.unmask();
        var json = this.successResponse;
        var o = eval("(" + json + ")");
        if (!o.status_type) {
            this.showDataError("modifyServicePanelState: Json object not found");
        }
        if (o.status_type === 'maintenance') {
            Ext.MessageBox.show({
                title: 'Notice',
                msg: 'The last service on this maintenance has been completed. The maintenance will be completed.',
                fn : globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });

        }
        else {
            if (o.status_id) {
                this.panel_ref.dataObj = Ext.apply(this.panel_ref.dataObj,o);
                this.panel_ref.decorateServicePanel();
                globalCloseWindow(); //closes maintenance calendar
            }
            else {
                this.showDataError("Data structure is missing key components");
            }
            
        }
    };
};


