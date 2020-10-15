/**
*   This is the main window for the maintenance view.
*/

Ext.namespace('Rack.app.maintcal.maintenanceView');

Rack.app.maintcal.maintenanceView = function () {

    this.connection     = new Ext.data.Connection({timeout : 60000});
    this.dateFormat     = "M. d, Y";
    this.maintenance_id = 0;

    this.cancelDialog = new Rack.app.maintcal.cancelDialog();
    this.cancelDialog.on('cancelclicked', this.submitCancel, this);

    this.addEvents({
        dataerror: true
    });

    this.tzMan = new Rack.app.maintcal.tzManager({
        initialLoad: true
    });
   
    Ext.onReady(this.getCurrentTZ, this);
};

Ext.extend(Rack.app.maintcal.maintenanceView, Ext.util.Observable, {
   
    genericDataErrorText: "There has been an undefined error. Please try again.",

    getCurrentTZ: function () {
        if (!UASCheck()) {
            // run a check of user agent check for Firefox2.x or IE
            return false;
        }
        this.tzMan.on('currenttz', this.handleTZSet, this);
        this.currentTZ = this.tzMan.check();
        if (!this.currentTZ) {
            this.tzMan.show();
        }
        else {
            this.getPageData();
        }
    },

    handleTZSet: function (tz_val, initial_load) {
        this.currentTZ = tz_val;
        if (initial_load) {
            this.getPageData();
        }
        else {
            // destroy the viewport for reloading the page.
            //this.layout.destroy();
            // reload the current window.
            var currentURL = window.location.href;
            window.location.href = currentURL;
        }
    },

    handleTZChangeRequest: function () {
        this.tzMan = new Rack.app.maintcal.tzManager({
            initialLoad : false
        });
        // add event listeners back in.
        this.tzMan.on('currenttz', this.handleTZSet, this);
        this.tzMan.show();
    }, 

    setTimeFormat: function () {
        this.timeFormat = "G:i"; // 24 hour display
        var tdate = new Date();
        var localOffset = tdate.getTimezoneOffset() / 60;
        if (localOffset <= 8 || localOffset >= 4) {
            this.timeFormat = "g:i A"; // US-style AM/PM 12 hour display.
        }
    },

    getPageData: function () {
        this.setTimeFormat();
        var loadTask = new Rack.app.maintcal.loadMaintenanceView(this);
        loadTask.start();
    },

    setPageTitle: function (ticket_num) {
        document.title = "Maintenance Calendar: Maintenance Details for : " + ticket_num;
    },

    showHelp: function () {
       this.helpWindow = window.open('/maintcal/shared/help.htm#maintenance_view');
    },

    submitCancel: function (cancelDialogRef) {
        var cancelTask = new Rack.app.maintcal.cancelMaintenance(this);
        cancelTask.start(cancelDialogRef.getCancelReason());
        cancelDialogRef.close();
    },

    composePage: function (o) {
        var headerHTML = [];

        headerHTML.push('<span>Maintenance View</span>',
                        '<button class="mc-tz-change-button"',
                        ' title="Current Timezone: ', 
                        decodeURIComponent(this.currentTZ),
                        '. Click to Change." > Change TZ</button>',
                        '<div id="mv-tckt-label">Ticket #: ',
                        '<a href="javascript:loadParent(', "'" ,
                        o.master_ticket_url, "'", ',0,1)">',
                        o.master_ticket, '</a></div>',
                        '<div id="mv-acct-label">',
                        o.account_name, '( ',
                        '<a href="javascript:loadParent(', "'" ,
                        o.account_url, "'", ',0,1)">', o.account_id,
                        '</a> )</div>');

        this.header = new Ext.Panel({
            region: 'north',
            height: 70,
            border: false,
            collapsible: false,
            baseCls: 'mc-heading',
            bodyStyle: 'text-align:center;',
            html: headerHTML.join('')
        });

        this.cancelButton = new Ext.Toolbar.Button({
            text:       'Cancel Maintenance',
            handler:    this.cancelDialog.show,
            scope:      this
        });

        // lay everything out.
        this.layout = new Ext.Viewport({
            layout: 'border',
            items: [this.header, this.maintenancePanel]
        });

        // apply event listener for the change Timezone button.
        var headerEl = this.header.getEl();
        var tzButton = headerEl.select('button.mc-tz-change-button');
        tzButton.on('click', this.handleTZChangeRequest, this);

        // apply event listener for help clicks
        var helpButton = headerEl.select('button.mc-help');
        helpButton.on('click', this.showHelp, this);

        // init quicktips.
        Ext.QuickTips.init();
        var thisViewBody = Ext.get(document.body);
        if (thisViewBody.isMasked()) {
            thisViewBody.unmask();
        }
    },

    composeAndAdd: function (o, service_id) {
        function getActiveServiceIndex(o, service_id) {
            if (o.length === 1) {
                return 0;
            }
            else {
                var s;
                for (s = 0; s < o.length; s++) {
                    if (o[s].service_id == service_id) {
                        return s;
                    }
                }
                return 0;
            }
        }

        var tpl = [];
        var activeItemIndex = getActiveServiceIndex(o.services, service_id);
        var dateTimeFormat = [this.dateFormat, this.timeFormat].join(' ');

        if (!o.start_time_time_tuple) {
            var this_start = "None";
            var this_end = "None";
        } else {
            var start_time = timeTupleToDate(o.start_time_time_tuple)
            var end_time = timeTupleToDate(o.end_time_time_tuple)

            var this_start = start_time.format(dateTimeFormat) + ' ' + o.start_time_time_tuple[8];
            var this_end = end_time.format(dateTimeFormat) + ' ' + o.end_time_time_tuple[8];
            var this_starttime = start_time.format(this.timeFormat) + ' ' + o.start_time_time_tuple[8];
            var this_endtime = end_time.format(this.timeFormat) + ' ' + o.end_time_time_tuple[8];
        }

        if (!o.date_assigned_time_tuple) {
            var this_date_assigned = "None";
        } else {
            var this_date_assigned = timeTupleToDate(o.date_assigned_time_tuple).format(this.dateFormat);
        }

        tpl.push('<table class="mc-maint">',
                '<tr><td class="mc-maint-heading">',
                'Maintenance Category',
                '</td><td class="mc-maint-data">',
                 o.maintenance_category,
                '</td></tr>',
                '<tr><td class="mc-maint-heading">',
                'Service Type',
                '</td><td class="mc-maint-data">',
                 o.service_type,
                '</td></tr>',
                '<tr><td class="mc-maint-heading">',
                'Start Time',
                '</td><td class="mc-maint-data">',
                 this_start ,
                '</td></tr>',
                 '<tr><td class="mc-maint-heading">',
                'End Time',
                '</td><td class="mc-maint-data">',
                 this_end ,
                '</td></tr></table>',
                '<table class="mc-maint"><tr><td class="mc-maint-heading">',
                'Server(s)<img src="/maintcal/shared/resources/images/plus.gif" class="mc-maint-heading-buttonUp" />',
                '<img src="/maintcal/shared/resources/images/minus.gif" class="mc-maint-heading-buttonDown" />',
                '</td><td class="mc-maint-data">',
                '<ul class="mc-maint-data-serverlist" style="list-style-type:none">');

        for (var d = 0; d < o.devices.length; d++) {
            tpl.push('<li><a href="javascript:loadParent(', "'" ,
            o.devices[d][1], "'",
            ',0,1)">', o.devices[d][0], '</a> ',
            o.devices[d][3], ' ', o.devices[0][4],
            '</li>');
        }

        tpl.push('</ul></td></tr></table>',
                '<table class="mc-maint"><tr><td class="mc-maint-heading">',
                'Description',
                '</td><td class="mc-maint-data">',
                'General Description:<br/>',
                newline2Break(o.general_description),
                '</td></tr></table>',
                '<table class="mc-maint"><tr><td class="mc-maint-heading">',
                'Expedite',
                '</td><td class="mc-maint-data">',
                (o.expedite) ? "Yes" : "No",
                '</td></tr>',
                '<tr><td class="mc-maint-heading">',
                'Additional Duration',
                '</td><td class="mc-maint-data">',
                o.additional_duration,
                ' minutes</td></tr>',
                '<tr><td class="mc-maint-heading">',
                'Scheduled By',
                '</td><td class="mc-maint-data">',
                 o.contact, ' (', this_date_assigned,
                ')</td></tr>',
                '<tr><td class="mc-maint-heading">',
                'Status',
                '</td><td class="mc-maint-data">',
                o.status,
                '</td></tr></table>');

        //  Add Customer Contact Info
        //  Also, save a copy of it for later

        this.notify_customer_before             = o.notify_customer_before;
        this.notify_customer_after              = o.notify_customer_after;
        this.notify_customer_department         = o.notify_customer_department;
        this.notify_customer_department_name    = o.notify_customer_department_name;
        this.notify_customer_name               = o.notify_customer_name;
        this.notify_customer_info               = o.notify_customer_info;

        if (o.notify_customer_before || o.notify_customer_after) {
            tpl.push(
                '<table class="mc-maint"><tr><td class="mc-maint-heading">',
                'Contact Customer Before Maintenance:',
                '</td><td class="mc-maint-data">',
                o.notify_customer_before ? 'True' : 'False',
                '</td></tr>',

                '<tr><td class="mc-maint-heading">',
                'Contact Customer After Maintenance:',
                '</td><td class="mc-maint-data">',
                o.notify_customer_after ? 'True' : 'False',
                '</td></tr>',

                '<tr><td class="mc-maint-heading">',
                'Department that should contact Customer:',
                '</td><td class="mc-maint-data">',
                o.notify_customer_department_name,
                '</td></tr>',

                '<tr><td class="mc-maint-heading">',
                'Customer Contact Name:',
                '</td><td class="mc-maint-data">',
                o.notify_customer_name,
                '</td></tr>',

                '<tr><td class="mc-maint-heading">',
                'Customer Contact Information:',
                '</td><td class="mc-maint-data">',
                o.notify_customer_info,
                '</td></tr>',

                '</table>'
            );
        }

        //  Check for a completed or canceled maintenance to show button or not.

        var buttonsArray = [ 
                {
                    text : 'Cancel Maintenance',
                    handler : this.cancelDialog.show,
                    scope : this.cancelDialog
                }
            ];

        if (o.status_id === 4 || o.status_id === 5) {
            buttonsArray = [];
        }

        this.ServicePanel = new Rack.app.maintcal.serviceView({
            maintenance_view: this,
            region : 'center',
            title : 'Services',
            layout : 'accordion',
            width: 400,
            collapsible: false,
            margins: '5 5 5 5',
            layoutConfig : {animate : true}
        });

        this.ServicePanel.composeAndAdd(o.services, activeItemIndex);

        this.maintenancePanel = new Ext.Panel({
            title : this_starttime + ' - ' + this_endtime + ' - ' + o.service_type,
            region : 'center',
            layout: 'border',
            items : [
                {
                    region : 'west',
                    frame: true,
                    autoScroll: true,
                    width: 350,
                    html : tpl.join(''),
                    buttons: buttonsArray
                },
                this.ServicePanel
            ]
        });

        this.composePage(o);

        //  Hide the expand and contract servers button on start.
        Ext.select('img.mc-maint-heading-buttonUp').each(function (el) {
                el.setVisibilityMode(Ext.Element.DISPLAY);
                el.hide();
            });

        Ext.addBehaviors({
            'img.mc-maint-heading-buttonDown@click': function (e, t) {
                e.stopEvent();
                var realt = Ext.get(t);
                realt.setVisibilityMode(Ext.Element.DISPLAY);
                realt.hide();
                Ext.select('img.mc-maint-heading-buttonUp').each(function (el) {
                    el.setVisibilityMode(Ext.Element.DISPLAY);
                    el.show();
                });
                Ext.select('ul.mc-maint-data-serverlist').each(function (i) {
                    i.setVisibilityMode(Ext.Element.DISPLAY);
                    i.hide();
                });
            },

            'img.mc-maint-heading-buttonUp@click': function (e, t) {
                e.stopEvent();
                var realt = Ext.get(t);
                realt.setVisibilityMode(Ext.Element.DISPLAY);
                realt.hide();
                Ext.select('img.mc-maint-heading-buttonDown').each(function (el) {
                    el.setVisibilityMode(Ext.Element.DISPLAY);
                    el.show();
                });
                Ext.select('ul.mc-maint-data-serverlist').each(function (i) {
                    i.show();
                });
            }
        });

        this.ServicePanel.items.get(0).collapse();
        this.ServicePanel.current_panel.expand();
        this.setPageTitle(o.master_ticket);
    }
});

