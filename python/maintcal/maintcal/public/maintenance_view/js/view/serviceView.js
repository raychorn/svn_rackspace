/**
*   This class represents the right-side of the screen
*   that displays an accordian-type view of services.
*/

Ext.namespace('Rack.app.maintcal.serviceView');

Rack.app.maintcal.serviceView = function (config) {
    config = config || {};

    Ext.apply(config, {
        autoScroll: true,
        frame:      true
    });

    this.maintenance_view = config.maintenance_view;
    this.cancelOrCloseDialog = new Rack.app.maintcal.cancelOrCloseDialog();
    this.cancelOrCloseDialog.on('closingclicked', this.runCloseOrCancelServiceTask, this);
    Ext.Panel.call(this, config);
};

Ext.extend(Rack.app.maintcal.serviceView, Ext.Panel, {

    composeAndAdd : function (o, active_service_index) {
        var s;
        for (s = 0; s < o.length; s++) {
            var tpl = [];
            tpl.push('<table class="mc-ti">',
                '<tr><td class="mc-ti-heading">',
                'Calendar',
                '</td><td class="mc-ti-data">',
                o[s].calendar,
                '</td></tr>',
                '<tr><td class="mc-ti-heading">',
                'Ticket #',
                '</td><td class="mc-ti-data">',
                '<a href="javascript:loadParent(',
                "'", o[s].ticket_url, "'",
                ',0,1)">', o[s].ticket,
                '</a></td></tr>',
                '<tr><td class="mc-ti-heading">',
                'Description',
                '</td><td class="mc-ti-data">',
                'Special Instructions:<br/>',
                newline2Break(o[s].description),
                '</td></tr>',
                '<tr><td class="mc-ti-heading">',
                'Status',
                '</td><td class="mc-ti-data">',
                o[s].status,
                '</td></tr></table>');

            var thisServicePanel = new Ext.Panel({
                title : o[s].calendar + ' - ' + o[s].status,
                autoScroll: true,
                html : tpl.join('')
            });

            thisServicePanel.service_id = o[s].service_id;
            thisServicePanel.calendar_id = o[s].calendar_id;
            thisServicePanel.dataObj    = o[s];

            thisServicePanel.addButton({
                text:       'Complete or Cancel Service',
                handler:    this.cancelOrCloseDialog.show,
                scope:      this.cancelOrCloseDialog
            });

            thisServicePanel.decorateServicePanel = function () {
                var panelEl = this.getEl();
                var panelHeader = panelEl.first();
                var panelToggleButton = panelHeader.first();
                // a canceled service
                if (this.dataObj.status_id === 4) {
                    // lose all status changing buttons
                    var b;
                    for (b = 0; b < this.buttons.length; b++) {
                        this.buttons[b].disable();
                    }
                    // add appropriate panel decoration.
                    panelHeader.dom.style.border = "1px solid #E89AC4";
                    panelHeader.dom.style.color = "#8B154F";
                    panelHeader.dom.style.background = "transparent url(/maintcal/shared/resources/images/lt-red-hd.gif) repeat-x scroll 0pt -9px";
                    panelToggleButton.addClass('mc-tool-cancel');
                }
                // completed service
                if (this.dataObj.status_id === 5) {
                    // lose all status changing buttons
                    var b;
                    for (b = 0; b < this.buttons.length; b++) {
                        this.buttons[b].disable();
                    }
                    // add appropriate panel decoration.
                    panelHeader.dom.style.border = "1px solid #9AE8BF";
                    panelHeader.dom.style.color = "#158B52";
                    panelHeader.dom.style.background = "transparent url(/maintcal/shared/resources/images/lt-green-hd.gif) repeat-x scroll 0pt -9px";
                    panelToggleButton.addClass('mc-tool-complete');
                   
                }
                this.setTitle(this.dataObj.calendar + 
                                    ' - ' + this.dataObj.status);
                var statusNode = panelEl.select('td.mc-ti-data').item(3); 
                if (statusNode) {
                    statusNode.dom.innerHTML = this.dataObj.status;
                }
            };

            thisServicePanel.on('render', thisServicePanel.decorateServicePanel, thisServicePanel);
            thisServicePanel.on('expand', this.markCurrentItem, this);

            this.add(thisServicePanel);
        }

        this.current_panel = this.items.get(active_service_index);
    },

    markCurrentItem: function (current_panel) {
        this.current_panel = current_panel;
    },

    runCloseOrCancelServiceTask: function (cancelDialogRef) {
        var form = cancelDialogRef.getCancelOrClosingReason();
        if(form.getForm().items.get('completeService').value == 1) { //Successful
            this.maybeDisplayContactCustomerDialog();
            cancelDialogRef.close();
        }
        else if(form.getForm().items.get('completeService').value == 3 || form.getForm().items.get('completeService').value == 2) { //Successful With Issues or Unsuccessful
            var unsuccessful = 0;
            if (form.getForm().items.get('completeService').value == 3) {
                var cancelReasonCheck = Ext.getCmp('successFulWithIssues');
            } else {
                var cancelReasonCheck = Ext.getCmp('unsuccessfulReasons');
                unsuccessful = 1;
            }
            var cnt = 0;
            var feedback = null;
            var reasons = [];
            var no_reasons = 0;
            for (cnt = 0;cnt<cancelReasonCheck.items.getCount();cnt++) {
                item = cancelReasonCheck.items.items[cnt];
                if(item.checked == true) {
                    reasons.push(item.boxLabel);
                    no_reasons++;
                }

                if (item.name == 'feedback') {
                    feedback = item.getRawValue();
                }
            }
            if (no_reasons == 0)
            {
               Ext.MessageBox.alert('ALERT', "You must select at least one reason");
               return;
            }
            
            if(feedback != null) {
                cancelDialogRef.close();
                this.maybeDisplayContactCustomerDialog(String(reasons), unsuccessful, feedback);
            }
            else {
                cancelDialogRef.close();
                this.maybeDisplayContactCustomerDialog(String(reasons), unsuccessful);
            }
        }
        else if(form.getForm().items.get('completeService').value == 4) { //Cancelled
            var cancelReasonCheck = Ext.getCmp('cancelReason');
            var cnt = 0;
            var feedback = null;
            var reasons = [];
            var no_reasons = 0;
            for (cnt = 0;cnt<cancelReasonCheck.items.getCount();cnt++) {
                item = cancelReasonCheck.items.items[cnt];
                if(item.checked == true) {
                    reasons.push(item.boxLabel);
                    no_reasons++;
                }
                if (item.name == 'feedback') {
                    feedback = item.getRawValue();
                }
            }
            if (no_reasons == 0)
            {
               Ext.MessageBox.alert('ALERT', "You must select at least one reason");
               return;
            }
            var cancelServiceTask = new Rack.app.maintcal.cancelService(this.maintenance_view);
            if (feedback != null) {
               cancelServiceTask.start(this.current_panel.service_id, this.current_panel, String(reasons),feedback);
            }
            else {
               cancelServiceTask.start(this.current_panel.service_id, this.current_panel, String(reasons));
            }
            cancelDialogRef.close();
        }
    },

    maybeDisplayContactCustomerDialog: function(reasons, unsuccessful, feedback) {
        if (     this.maintenance_view.notify_customer_after 
            &&  (this.maintenance_view.notify_customer_department == this.current_panel.calendar_id)) {

                var contactCustomerDialog = new Rack.app.maintcal.contactCustomerDialog(this, 'After', 
                        this.maintenance_view.connection, this.maintenance_view.maintenance_id, reasons, unsuccessful, feedback);
                contactCustomerDialog.setContactInfo({
                        'department_name':   this.maintenance_view.notify_customer_department_name,
                        'customer_name':     this.maintenance_view.notify_customer_name,
                        'customer_info':     this.maintenance_view.notify_customer_info
                    });
                contactCustomerDialog.show();
        } else {
            this.runCompleteServiceTask(reasons, unsuccessful, feedback);
        }
    },

    runCompleteServiceTask: function (reasons, unsuccessful, feedback) {
        if(reasons != null) {
            if (unsuccessful)
                var completeServiceTask = new Rack.app.maintcal.unsuccessfulService(this.maintenance_view);
            else 
                var completeServiceTask = new Rack.app.maintcal.completeServiceWithIssues(this.maintenance_view);
                
            completeServiceTask.start(this.current_panel.service_id, this.current_panel, reasons, feedback);
        }
        else {
            var completeServiceTask = new Rack.app.maintcal.completeService(this.maintenance_view);
            completeServiceTask.start(this.current_panel.service_id, this.current_panel);
        }
    }
});

