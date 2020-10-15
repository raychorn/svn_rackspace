/**
*   This represents a single ticket.
*/

Rack.app.maintcal.TicketBox = Ext.extend(Ext.Toolbar, {
    dateFormat : "M. d, Y",
    timeWeight: 0.5,
    label: '',
    ticket: new Ext.data.Record({}),
    isAdmin: false,
    doc : '',

    constructor: function (config) {
        this.addEvents({
            statechange: true
        });

        this.currentTZ = config.currentTZ;

        Ext.apply(config, {
            autoShow: true,
            autoWidth: true
        });

        Ext.Toolbar.constructor.call(this, config);
    },

    afterRender : function () {
        Rack.app.maintcal.TicketBox.superclass.afterRender.call(this);
        this.addText({
            xtype: 'tbtext',
            text: this.label
        });
        this.addFill();
        this.addButton({
            xtype: 'tbbutton',
            tooltipType: 'qtip',
            cls : 'mc-ticket-view-button',
            handleMouseEvents: false,
            tooltip: 'Show Ticket Quick View',
            autoShow: true,
            handler: this.loadMaintenanceInfoForPopWindow,
            scope: this
        });
        // init the cancellation Dialog
        this.cancelDialog = new Rack.app.maintcal.cancelDialog();
        this.decorateHeader(this.ticket.data.state_id);

        //init the cancelorclose dialog
        this.cancelOrCloseDialog = new Rack.app.maintcal.cancelOrCloseDialog();
    },

    layoutTicketInfo: function (record, maintenance_info) {
        var tpl = [];
        tpl.push('<table class="mc-ti">',
            '<tr><td class="mc-ti-heading">',
            'Ticket #',
            '</td><td class="mc-ti-data">',
            '<a href="javascript:loadParent(',
            "'", record.data.ticket_url, "'",
            ',0,1)">', record.data.ticket,
            '</a></td></tr>',
            '<tr><td class="mc-ti-heading">',
            'Account #',
            '</td><td class="mc-ti-data">',
            record.data.account_name,
            ' (<a href="javascript:loadParent(', "'", record.data.account_url, "'",
            ',0,1)">', record.data.account_id, '</a>)',
            '</td></tr>',
            '<tr><td class="mc-ti-heading">',
            'Server(s)<img src="/maintcal/shared/resources/images/plus.gif" class="mc-ti-heading-buttonUp" />',
            '<img src="/maintcal/shared/resources/images/minus.gif" class="mc-ti-heading-buttonDown" />',
            '</td><td class="mc-ti-data">',
            '<ul class="mc-ti-data-serverlist" style="list-style-type:none">');
        var serverDoc = record.data.servers;
        var sc;
        for (sc = 0; sc < serverDoc.length; sc++) {
            tpl.push('<li><a href="javascript:loadParent(', "'",
            serverDoc[sc][0], "'",
            ',0,1)">', serverDoc[sc][1], '</a> ',
            serverDoc[sc][2], ' ', serverDoc[sc][3],
            '</li>'); 
        }
        /*serverDoc.each(function (r) {
            tpl.push('<li><a href="javascript:loadParent(', "'" ,
            r.data.server_url, "'",
            ',0,1)">', r.data.id, '</a> ',
            r.data.name, ' ', r.data.os,
            '</li>');
        });*/

        tpl.push(
            '</ul></td></tr>',
            '<tr><td class="mc-ti-heading">',
            'Service Type',
            '</td><td class="mc-ti-data">',
            record.data.service_type , '(',
            (timeTupleToDate(record.data.end_time_time_tuple) - timeTupleToDate(record.data.start_time_time_tuple))/60000,
            ' min )</td></tr>',
            '<tr><td class="mc-ti-heading">',
            'Description',
            '</td><td class="mc-ti-data">',
            'General Description:<br/>',
            newline2Break(record.data.general_description),
            '<br/>Special Instructions:<br/>',
            newline2Break(record.data.description),
            '</td></tr>',
            '<tr><td class="mc-ti-heading">',
            'Scheduled By',
            '</td><td class="mc-ti-data">',
            record.data.contact, ' ',
            ' (', timeTupleToDate(record.data.date_assigned_time_tuple).format(this.dateFormat), ') ',
            '</td></tr>',
            '<tr><td class="mc-ti-heading">',
            'Status',
            '</td><td class="mc-ti-data">',
            record.data.state,
            '</td></tr>');

        //  Add Customer Contact Info
        //  Also, save a copy of it for later

        this.notify_customer_before             = maintenance_info.notify_customer_before;
        this.notify_customer_after              = maintenance_info.notify_customer_after;
        this.notify_customer_department         = maintenance_info.notify_customer_department;
        this.notify_customer_department_name    = maintenance_info.notify_customer_department_name;
        this.notify_customer_name               = maintenance_info.notify_customer_name;
        this.notify_customer_info               = maintenance_info.notify_customer_info;

        this.calendar_id                        = record.data.calendar_id;

        if (this.notify_customer_before || this.notify_customer_after) {
            if (this.notify_customer_department == record.data.calendar_id) {
                tpl.push(
                    '<tr><td class="mc-ti-heading">',
                    'Contact Customer Before Maintenance:',
                    '</td><td class="mc-ti-data">',
                    this.notify_customer_before ? 'True' : 'False',
                    '</td></tr>',

                    '<tr><td class="mc-ti-heading">',
                    'Contact Customer After Maintenance:',
                    '</td><td class="mc-ti-data">',
                    this.notify_customer_after ? 'True' : 'False',
                    '</td></tr>',

                    '<tr><td class="mc-ti-heading">',
                    'Department that should contact Customer:',
                    '</td><td class="mc-ti-data">',
                    this.notify_customer_department_name,
                    '</td></tr>',

                    '<tr><td class="mc-ti-heading">',
                    'Customer Contact Name:',
                    '</td><td class="mc-ti-data">',
                    this.notify_customer_name,
                    '</td></tr>',

                    '<tr><td class="mc-ti-heading">',
                    'Customer Contact Information:',
                    '</td><td class="mc-ti-data">',
                    this.notify_customer_info,
                    '</td></tr>'
                );
            }
        }

        tpl.push('</table>');

        return tpl.join('');
    },

    loadMaintenanceInfoForPopWindow: function () {
        var loadTask = new Rack.app.maintcal.ticket.loadMaintenanceInfoForTicket(this);
        loadTask.start(this.ticket, this.currentTZ);
    },

    popWindow : function (maintenance_info) {
        // get the height of the body to dynamically size the window.
        var thisDocument = Ext.getBody();
        var ht = thisDocument.getHeight() / 1.1;
        var windowHTML = this.layoutTicketInfo(this.ticket, maintenance_info);
        var thisConfig = {};
        // set buttons config based on admin privledges and state.
        var buttonArray;
        var exitButton = new Ext.Button({
            text: "Exit",
            handler: function() {
                this.currentPop.close();
            },
            scope: this
        });
        if ((this.ticket.data.state_id === 4 || this.ticket.data.state_id === 5 || this.ticket.data.state_id === 7 || this.ticket.data.state_id === 8) || !this.ticket.data.is_admin) {
            buttonArray = [
                {
                    text: 'Complete or Cancel Service',
                    disabled: true
                },
                exitButton
            ];
        } else {
            buttonArray = [
                {
                    text: 'Complete or Cancel Service',
                    handler: this.cancelOrCloseDialog.show,
                    scope: this.cancelOrCloseDialog
                },
                exitButton
            ];
        }

        thisConfig = {
            width: 600,
            autoScroll: true,
            draggable: false,
            border: false,
            closeAction: 'close',
            title: this.label,
            plain: true,
            modal: 'true',
            constrain: true,
            resizable: false,
            layout: 'fit',
            html: windowHTML,
            buttons: buttonArray
        };

        this.currentPop = new Ext.Window(thisConfig);
        this.cancelDialog.on('cancelclicked',this.cancelService,this);
        this.cancelOrCloseDialog.on('closingclicked', this.runCloseOrCancelServiceTask, this);
        this.currentPop.show();
        if (this.currentPop.getFrameHeight() + this.currentPop.getInnerHeight() > ht) {
            this.currentPop.setHeight(ht);
        }
        // hide the expand and contract servers button on start.
        Ext.select('img.mc-ti-heading-buttonUp').each(function (el) {
            el.setVisibilityMode(Ext.Element.DISPLAY);
            el.hide();
        });

        Ext.addBehaviors({
            'img.mc-ti-heading-buttonDown@click': function (e, t) {
                e.stopEvent();
                var realt = Ext.get(t);
                realt.setVisibilityMode(Ext.Element.DISPLAY);
                realt.hide();
                Ext.select('img.mc-ti-heading-buttonUp').each(function (el) {
                    el.setVisibilityMode(Ext.Element.DISPLAY);
                    el.show();
                });
                Ext.select('ul.mc-ti-data-serverlist').each(function (i) {
                    i.setVisibilityMode(Ext.Element.DISPLAY);
                    i.hide();
                });
            },

            'img.mc-ti-heading-buttonUp@click': function (e, t) {
                e.stopEvent();
                var realt = Ext.get(t);
                realt.setVisibilityMode(Ext.Element.DISPLAY);
                realt.hide();
                Ext.select('img.mc-ti-heading-buttonDown').each(function (el) {
                    el.setVisibilityMode(Ext.Element.DISPLAY);
                    el.show();
                });
                Ext.select('ul.mc-ti-data-serverlist').each(function (i) {
                    i.show();
                });
            }
        });
    },
    
    decorateHeader : function (state_id) {
        var thisEl = this.getEl();
        // this will only get the correct button if the toolbar doesnt get modified.
        var popButton = this.items.get(2);
        var thisMaxIcon = popButton.getEl();
        if (state_id === 4) {
            // add appropriate panel decoration.
            thisEl.dom.style.border = "1px solid #E89AC4";
            thisEl.dom.style.color = "#8B154F";
            thisEl.dom.style.background = "transparent url(/maintcal/shared/resources/images/lt-red-hd.gif) repeat-x scroll 0pt -9px";
            thisMaxIcon.removeClass('mc-ticket-view-button');
            thisMaxIcon.addClass('mc-ticket-view-button-cancel');
        }
        // completed service
        if (state_id === 5) {
            // add appropriate panel decoration.
            thisEl.dom.style.border = "1px solid #9AE8BF";
            thisEl.dom.style.color = "#158B52";
            thisEl.dom.style.background = "transparent url(/maintcal/shared/resources/images/lt-green-hd.gif) repeat-x scroll 0pt -9px";
            thisMaxIcon.removeClass('mc-ticket-view-button');
            thisMaxIcon.addClass('mc-ticket-view-button-complete');
                   
        } 
    },

    maybeDisplayContactCustomerDialog: function(reasons, unsuccessful, feedback) {
        if (     this.notify_customer_after 
            &&  (this.notify_customer_department == this.calendar_id)) {
                var contactCustomerDialog = new Rack.app.maintcal.contactCustomerDialog(this, 'After',
                        this.ticket.store.connection, this.maintenance_id, reasons, unsuccessful, feedback);
                contactCustomerDialog.setContactInfo({
                        'department_name':   this.notify_customer_department_name,
                        'customer_name':     this.notify_customer_name,
                        'customer_info':     this.notify_customer_info
                    });
                contactCustomerDialog.show();
        } else {
            this.runCompleteServiceTask(reasons, unsuccessful, feedback);
        }
    },

    runCompleteServiceTask : function (reasons, unsuccessful, feedback) {
        if (reasons != null) {
            if (unsuccessful) 
                var thisCompleteTask = new Rack.app.maintcal.ticket.unsuccessfulService(this.ticket);
            else
                var thisCompleteTask = new Rack.app.maintcal.ticket.completeServiceWithIssues(this.ticket);

            thisCompleteTask.start(this.ticket.data.id,this, reasons, feedback);
        } else {
            var thisCompleteTask = new Rack.app.maintcal.ticket.completeService(this.ticket);
            thisCompleteTask.start(this.ticket.data.id,this);
        }
        this.currentPop.close();
    },

    cancelService : function (thisCancelDialog) {
        var thisCompleteTask = new Rack.app.maintcal.ticket.cancelService(this.ticket);
        thisCompleteTask.start(this.ticket.data.id,
                                this,
                                thisCancelDialog.getCancelReason());
        thisCancelDialog.close();
        this.currentPop.close();
    },

    runCloseOrCancelServiceTask : function (closeOrCancelDialogRef) {
        var form = closeOrCancelDialogRef.getCancelOrClosingReason();
        
        if(form.getForm().items.get('completeService').value == 1) { //Successful
            this.maybeDisplayContactCustomerDialog();
            closeOrCancelDialogRef.close();
        }
        else if(form.getForm().items.get('completeService').value == 3 || form.getForm().items.get('completeService').value == 2) { 
            //Successful With Issues or Unsuccessful
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
            if (no_reasons == 0) {
               Ext.MessageBox.alert('ALERT', "You must select at least one reason");
               return;
            }
            if (feedback != null) {
                closeOrCancelDialogRef.close();
                this.maybeDisplayContactCustomerDialog(String(reasons), unsuccessful, feedback);
            } else {
                closeOrCancelDialogRef.close();
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
            if (no_reasons == 0) {
               Ext.MessageBox.alert('ALERT', "You must select at least one reason");
               return;
            }
            var cancelServiceTask = new Rack.app.maintcal.ticket.cancelService(this.ticket);
            if(feedback != null) {
                cancelServiceTask.start(this.ticket.data.id, this, String(reasons),feedback);
            } else {
                cancelServiceTask.start(this.ticket.data.id, this, String(reasons));
            }
            closeOrCancelDialogRef.close();
        }
        this.currentPop.close();
    }

});

