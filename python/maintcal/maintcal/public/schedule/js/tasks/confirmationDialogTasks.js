/**
*   This file contains two tasks:
*
*       getConfirmationOptions
*       confirmMaintenance
*/

Ext.namespace('Rack.app.maintcal.getConfirmationOptions');

Rack.app.maintcal.getConfirmationOptions = function (schedule_view, schedule_model, tentative_view) {
    if (!schedule_model.selectedZoneName) {
        this.currentTZ = schedule_view.currentTZ;
    } else {
        this.currentTZ = schedule_model.selectedZoneName;
    }

    this.start = function () {
        schedule_model.connection.request({
                url: '/maintcal/maintenances/' + schedule_model.maintenance_id + 
                        '.sjson?tzname=' + this.currentTZ,
                method: 'GET',
                success: this.composeDialogData,
                failure: this.handleDataError,
                scope: this
            });
    };

    this.composeDialogData = function (r) {
        var ostring = [];
        var json = r.responseText;
        var o = eval("(" + json + ")");
        if (!o) {
            throw "composeDialogData: Json object not found";
        }

        if (o.maintenance_id === schedule_model.maintenance_id) {
            ostring.push('<div class="mc-sv-tentative-text">You have selected');
            ostring.push(' <span>' + o.service_type + '</span> ');
            if (o.devices.length && o.devices.length > 1) {
                ostring.push('for <span>' + o.devices.length + '</span> devices');
            } else {
                ostring.push('for a <span>single</span> device');
            }
            ostring.push('</div>');
            ostring.push(
                '<div class="mc-sv-tentative-text">Total length of maintenance: ');
            if (o.length !== 1) {
                ostring.push('<span>' + o.length + ' hours <span>'); 
            } else {
                ostring.push('<span>1 hour </span>');
            }
            if (o.additional_duration > 0) {
                ostring.push('with <span>' + o.additional_duration + '</span>');
                ostring.push(' minutes in addition.');
            }
            ostring.push('</div>');
            ostring.push('<div class="mc-sv-tentative-text">Lead time required: ');
            if (o.expedite) {
                ostring.push('<span class="mc-sv-tentative-ex">Expedite</span>');
            } else {
                if (o.lead_time !== 1) {
                    ostring.push('<span>' + o.lead_time + ' hours </span>');
                } else {
                    ostring.push('<span> 1 hour </span>');
                }
            }
        } else {
            schedule_model.fireEvent('dataerror', r);
        }

        this.optionsContent = ostring.join('');

        this.devicesGrid =  new Ext.grid.GridPanel({
            title: "Selected Devices",
            width: 681,
            height: 300,
            frame: true,
            viewConfig: {
                forceFit : true
            },
            store: new Ext.data.SimpleStore({
                fields : [
                    {
                        name: 'device_id',
                        type: 'int'
                    }, {
                        name: 'device_link',
                        type: 'string'
                    }, {
                        name: 'icon_url',
                        type: 'string'
                    }, {
                        name: 'name',
                        type: 'string'
                    }, {
                        name: 'os_type',
                        type: 'string'
                    }
                ],
                data : o.devices
            }),
            columns: [
                {
                    header : false,
                    width : 45,
                    dataIndex : 'device_link',
                    renderer : function (val) {
                        try{
                            parts = val.split('/');
                        }catch(e){
                            parts = [];
                        }
                        if (parts.length > 3) {
                            return '<a href="javascript:loadParent(' + 
                                "'" + val + "',0,1)" + '">' + 
                                parts[parts.length -1] + '</a>';
                        }
                        else {
                            return "";
                        }
                    }
                }, {
                    header : false,
                    dataIndex : 'icon_url',
                    width : 25,
                    renderer : function (val) {
                        if (val) {
                            return '<img src="' + val + '" />';
                        } else {
                            return '<img src="" />';
                        }
                    }
                }, {
                    header : false,
                    dataIndex : 'name'
                }, {
                    header: false,
                    dataIndex: 'os_type'
                }
            ]
        });

        var maint_start_time = timeTupleToDate(o.start_time_time_tuple);
        var maint_end_time = timeTupleToDate(o.end_time_time_tuple);

        var dtstring = [];
        dtstring.push('<table class="mc-sv-tentative-text" width=675><tr><td>Date: <span>');
        dtstring.push(maint_start_time.format('l - F j, Y') + '</span></td>');
        dtstring.push('<td align="right">Account: <span>' + o.account_id + ' - ' + Ext.util.Format.ellipsis(o.account_name,45) + '</span></td></tr>');
        dtstring.push('<tr><td>Time: <span>'); 
        dtstring.push(maint_start_time.format(schedule_view.timeFormat) + ' - ');
        dtstring.push(maint_end_time.format(schedule_view.timeFormat) + ' ');
        dtstring.push(decodeURIComponent(this.currentTZ) + '</span></td>');
        dtstring.push('<td align="right">SuperTicket: <span>' + o.master_ticket + '</span></td></tr></table>');  

        this.dateTimeContent = dtstring.join('');

        var confirmWindow = new Rack.app.maintcal.confirmationDialog(
                                        schedule_view,
                                        this.optionsContent,
                                        this.devicesGrid,
                                        this.dateTimeContent,
                                        tentative_view);
        Ext.getBody().unmask();
        confirmWindow.show();
    };

    this.handleDataError = function (r) {
        schedule_model.fireEvent('dataerror', r);
    };
};

Ext.namespace('Rack.app.maintcal.confirmMaintenance');

Rack.app.maintcal.confirmMaintenance = function (confirmationDialog_view) {
    this.start = function () {
        Ext.getBody().mask('Confirming Maintenance ...','',10000);
        confirmationDialog_view.schedule_view.doc.connection.request({
            url: '/maintcal/maintenances/confirm/' + confirmationDialog_view.schedule_view.doc.maintenance_id,
            method: 'POST',
            success: this.confirmConfirm,
            failure: confirmationDialog_view.schedule_view.showDataError
        });
    };

    this.confirmConfirm = function (r) {
        Ext.getBody().unmask();
        loadParent('',0,1);
        Ext.MessageBox.show({
                title: 'Success',
                msg: 'Your Maintenance has been successfully scheduled.',
                fn: globalCloseWindow,
                buttons: Ext.MessageBox.OK,
                width: 250
            });
    };
};

