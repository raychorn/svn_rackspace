/**
*   This class represents the "month view" of the calendar_view application.
*/

Ext.namespace("Rack.app.maintcal.MonthView");

Rack.app.maintcal.MonthView = function(cal_obj, config) {
    this.ticketView = new Rack.app.maintcal.ticketView(cal_obj.doc.tickets, cal_obj, 
        {
            timeFormat: config.timeFormat,
            region: "west",
            width: 300,
            collapsible: false,
            margins: "5 5 5 5",
            border: false,
            bodyStyle: "background-color:transparent;"
        }
    );

    this.calendar = new Ext.bigcal({
        timeFormat: config.timeFormat,
        region: "center"
    });

    //  Listen for items shown/hidden on the showHideStateMenu and refresh
    //  both ticket view and calendar view.
    this.ticketView.showHideMenu.on("statechange", this.refreshViews, cal_obj);

    this.addEvents({
        activate: true
    });

    var default_config = {
        layout: "border",
        autoScroll: true,
        buttonAlign: "right",
        items: [this.ticketView, this.calendar]
    };

    Ext.apply(this, config, default_config);
    Ext.Panel.call(this);
};

Ext.extend(Rack.app.maintcal.MonthView, Ext.Panel, {
    addScheduleTime: function(o) {
        this.calendar.addScheduleTime(o);
    },

    onActivate: function() {
        this.ticketView.onActivate();
    }
});
