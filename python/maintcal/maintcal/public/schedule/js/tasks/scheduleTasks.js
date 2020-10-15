/**
*   Top-level schedule tasks.
*/

Rack.app.maintcal.schedule.getMaintInfo = function (schedule_view, model) {
    this.widgetReadyCount = 0;

    this.start = function () {
        var ticket_number = getURLParam('ref_no');
        schedule_view.setPageTitle(ticket_number);
        model.connection.request({
                url: '/maintcal/tickets/' + ticket_number + '.json',
                method: 'GET',
                success: this.getWidgetData,
                failure: this.handleDataError,
                scope: this
            });
    };

    this.getWidgetData = function (r, o) {
        this.widgetReadyCount++;
        this.advancePageDataProgress();

        model.handleAccountData(r, o);

        model.serviceTypes.on('widgetready', this.handleWidgetReady, this);
        model.devices.on('widgetready', this.handleWidgetReady, this);
        model.options.on('widgetready', this.handleWidgetReady, this);

        model.serviceTypes.fireEvent('dataready', model.serviceTypes);
        model.devices.fireEvent('dataready', model.devices,
                                model.ticket_devices);
        model.options.fireEvent('dataready', model.options);
    };

    this.handleDataError = function (r, o) {
        model.fireEvent('dataerror', r, o);
    };

    this.handleWidgetReady = function () {
        this.widgetReadyCount++;
        this.advancePageDataProgress();


        if (this.widgetReadyCount === 4) {
            model.handleWidgetReady();
        }
    };

    this.advancePageDataProgress = function () {
        schedule_view.updatePageDataProgress(0.25 * this.widgetReadyCount);
    };
};

/**
*
*/
Rack.app.maintcal.schedule.createMaintenance = function (schedule_view, model) {
    this.start = function () {
        schedule_view.centerPanel.body.mask('Calculating Available Times ...');
        var theseParams =  {
            master_ticket: model.master_ticket,
            service_type_id: schedule_view.selectedServiceType,
            servers: schedule_view.selectedDevices,
            expedite: schedule_view.options.expediteCheckBox.getValue().toString(),
            additional_duration_minutes: schedule_view.options.extendTimesCombo.getValue()
        };
        // only pass calendars if they have opened.
        if(schedule_view.calendar_overrides.getSelecteds().length){
            Ext.apply(theseParams,{
                calendars:schedule_view.calendar_overrides.getSelecteds()
            });
        }
        if (model.maintenance_id) {
            model.connection.request({
                url: '/maintcal/maintenances/update/' + model.maintenance_id,
                method: 'POST',
                success: this.updateAvailableTimes,
                failure: this.handleDataError,
                scope: this,
                params: theseParams
            });
        }
        else {
            model.connection.request({
                url: '/maintcal/maintenances/create/',
                method: 'POST',
                success: this.updateAvailableTimes,
                failure: this.handleDataError,
                scope: this,
                params: theseParams
            });
        }
    };

    this.updateAvailableTimes = function (r) {
        // remove the reference to the successfully completed task.
        delete schedule_view.createMaintenanceTask;
        if (r.responseText) {
            var json = r.responseText;
            var o = eval("(" + json + ")");
            if (!o) {
                throw "handleResponse: Json object not found";
            }
            if (o.maintenance_id && o.calendar_service_map) {
                model.maintenance_id = o.maintenance_id;
                model.calendar_service_map = o.calendar_service_map;

            }
            else {
                model.fireEvent('dataerror', r);
            }
        }
        else {
            // throw a generic error
            model.fireEvent('dataerror', '');
        }
        var passedtz = schedule_view.currentTZ;
        var dateNow = new Date();
        if (model.selectedZoneName) {
            passedtz = model.selectedZoneName;
        }
        // deprecated in favor of passing full year, and month.
        /*var monthNow = dateNow.getMonth();
        var dateSet = new Date(schedule_view.calendar.start_month_secs * 1000);
        var monthSet = dateSet.getMonth();
        var start_time_secs = dateNow.format('U');
        if (monthSet !== monthNow) {
            start_time_secs = schedule_view.calendar.start_month_secs;
        }
        var end_time_secs = schedule_view.calendar.end_month_secs;
        */
        var selectedYear = schedule_view.calendar.activeDate.getFullYear();
        var selectedMonth = schedule_view.calendar.activeDate.getMonth() + 1;
        var selectedDay = schedule_view.calendar.activeDate.getDate();
        model.connection.request({
                url: '/maintcal/maintenances/times_available/' + model.maintenance_id + 
                    '?start_year=' + selectedYear + 
                    '&start_month=' + selectedMonth +
                    '&tzname=' + passedtz,
                method: 'GET',
                success: schedule_view.updateCalendar,
                failure: schedule_view.showDataError,
                scope: schedule_view
            });

    };
    this.handleDataError = function (r) {
        model.fireEvent('dataerror', r);
    };

};

Rack.app.maintcal.schedule.changeTZ = function (schedule_view, model) {
    this.start = function (tzName) {
        // update the selected zone name.
        model.selectedZoneName = tzName;
        model.connection.request({
                url: '/maintcal/timezones/offset/?tzname=' + tzName,
                method: 'GET',
                success: this.updateTZView,
                failure: this.handleDataError,
                scope: this
            });

    };
    this.updateTZView = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            throw "updateTZView: Json object not found";
        }
        if (!'offset_hours' in o) {
            model.fireEvent('dataerror', r);
        }
        else {
            schedule_view.setHeadingTZName(model.selectedZoneName.replace(/_/g,' '));
            schedule_view.header.clock.update(o.offset_hours);
            schedule_view.calendar.currentOffset = o.offset_hours;
        }
    };
    this.handleDataError = function (r) {
        model.fireEvent('dataerror', r);
    };
};

Rack.app.maintcal.schedule.userChangeTZ = function (schedule_view, model) {
    this.start = function (tzName) {
        // update the selected zone name.
        model.selectedZoneName = tzName;
        model.connection.request({
                url: '/maintcal/timezones/offset/?tzname=' + tzName,
                method: 'GET',
                success: this.updateTZView,
                failure: this.handleDataError,
                scope: this
            });

    };
    this.updateTZView = function (r) {
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            throw "updateTZView: Json object not found";
        }
        if (!'offset_hours' in o) {
            model.fireEvent('dataerror', r);
        }
        else {
            schedule_view.setHeadingTZName(model.selectedZoneName.replace(/_/g,' '));
            schedule_view.header.clock.update(o.offset_hours);
            schedule_view.calendar.currentOffset = o.offset_hours;
            // re-update the maintenance after TZ change
            var thisTZUpdate = new Rack.app.maintcal.schedule.createMaintenance(schedule_view, model);
            thisTZUpdate.start();
        }
    };
    this.handleDataError = function (r) {
        model.fireEvent('dataerror', r);
    };
};

