/**
*   This class is used on the left-hand side of the screen.
*   It looks like each item that is displayed is an instance of ticketbox.
*
*   It looks as though this class is only instanced one time,
*   and the class that instances this class is MonthView.
*/

Ext.namespace('Rack.app.maintcal.ticketView');

Rack.app.maintcal.ticketView = function (doc, cal_obj, config) {

    this.doc = doc;
    this.parentCalendarView = cal_obj;

    this.addEvents({
        dataerror: true,
        loadtickets: true,
        ticketsloaded: true,
        ticketstatechange: true
    });

    this.showHideMenu = new Rack.app.maintcal.showHideMenu({
        calendarRef : this.parentCalendarView
    });

    this.currentStartTime = new Date().clearTime();

    // add a listener to tell the widget to start loading tickets.
    this.on('loadtickets', this.loadTickets, this);

    // add listener to listen for data error events from ticket view thingies.
    this.on('dataerror', cal_obj.showDataError, cal_obj);

    config = config || {};
    Ext.apply(config, {
        frame: true,
        height: 360,
        autoScroll: true,
        collapsible: true,
        title: 'Maintenance Tickets',
        tools : [{
            'id' : 'down',
            'handler' : this.showHideOptions,
            'scope' : this,
            'qtip' : 'Show/Hide Options'
        }]
    });
    Ext.Panel.call(this, config);
};

Ext.extend(Rack.app.maintcal.ticketView, Ext.Panel, {
    dateFormat : "M. d, Y",
    timeFormat : "G:i", // 24 hour display
    dateAbbrevFormat: "n/j",

    loadTickets: function (start_year, start_month, start_day, calendar_id, currentTZ, admin) {
        var start_date;
        if (!start_year || !start_month || !start_day) {
            start_date = this.currentStartTime;
        } else {
            start_date = new Date(start_year, start_month-1, start_day);
            this.currentStartTime = start_date;
        }
        var end_date = start_date.add(Date.DAY, 1);

        this.doc.on("load", this.addTickets, this);
        this.doc.on('ticketsloaded', this.addTickets, this);

        this.currentEndTime = this.currentStartTime.add(Date.DAY, 1);
        this.currentStartTimeLabel = this.currentStartTime.format(this.dateFormat);
        this.isAdmin = admin;
        this.doc.getTicketsByDateRange(start_date, end_date, calendar_id, currentTZ, 
            this.showHideMenu.current_selections);
    },

    showNoTicketsLabel: function() {
        var ticket_found_label = new Rack.app.maintcal.Label({html: 'No Maintenance Tickets found', cls: 'mc-no-ticket-label'});
        this.add(ticket_found_label);
    },

    onActivate: function() {
        this.addTickets();
    },

    addTickets : function () {
        this.doc.un("load", this.addTickets);
        this.doc.un("ticketsloaded", this.addTickets);

        if (this.items && this.items.getCount() !== 0) {
            this.items.each(function (c) {
                this.remove(c, true);
            }, this);
        }

        if (this.doc.getCount() === 0) {
            this.showNoTicketsLabel();
        } else {
            var number_added = 0;
            this.doc.each(function (r) {
                var item_start = timeTupleToDate(r.get('start_time_time_tuple'));
                var item_end = timeTupleToDate(r.get('end_time_time_tuple'));


                // Check for items outside of the selected date
                if ((item_start > this.currentEndTime) || (item_end < this.currentStartTime)) {
                    return;
                }
				var start_format_string;
                if(item_start < this.currentStartTime) {
                    start_format_string = this.timeFormat + "(n/j)";
                } else {
                    start_format_string = this.timeFormat;
                }
				var end_format_string;
                if(item_end > this.currentEndTime) {
                    end_format_string = this.timeFormat + "(n/j)";
                } else {
                    end_format_string = this.timeFormat;
                }

                var thisTicketLabel = item_start.format(start_format_string) + 
                     " - " + item_end.format(end_format_string) + ' ' + 
                     r.get('end_time_time_tuple')[8] + ' (' + r.get('service_type') +
                      ') ';

                if(thisTicketLabel.length > 46) {
                    thisTicketLabel = '<span title="' + thisTicketLabel + '">' +
                    Ext.util.Format.ellipsis(thisTicketLabel,46) + '</span>';
                }

                var aTicket = new Rack.app.maintcal.TicketBox(
                    {
                        currentTZ: this.parentCalendarView.currentTZ,
                        label: thisTicketLabel,
                        ticket: r,
                        isAdmin: this.isAdmin,
                        doc: this.doc,
                        stateful: false,
                        autoHeight: false,
                        height: 30
                    }
                );

                aTicket.on('statechange', this.handleStateChange, this);
                this.add(aTicket);
                number_added++;
            }, this);
            if (number_added === 0) {
                this.showNoTicketsLabel();
            }
        }

        this.setTitle('Maintenance Tickets ' + this.currentStartTimeLabel);
        if (this.rendered) {
            this.doLayout();
        }
    },

    handleStateChange : function (ticketBoxObj) {
        this.fireEvent('ticketstatechange', ticketBoxObj);
    },

    showHideOptions : function (e,el,p) {
        this.showHideMenu.show(el);
    }
});


