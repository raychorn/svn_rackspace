/*extern Rack, Ext */

/* contains and updates the day grids thingee */


Ext.namespace('Rack.app.maintcal.ViewBody');

Rack.app.maintcal.ViewBody = function(runtime_config) {
    var config = runtime_config || {};
    if (!config.startdate) {
        config.startdate = new Date();
    }
    this.leftTimeline = new Rack.app.maintcal.DayViewTimeline({
            navigationParent : config.navigationParent,
            navigationBck : config.navigation,
            width: 60
    });
    this.dayContainer = new Rack.app.maintcal.DayViewContainer({
            data : config.data,
            startdate : config.startdate,
            height: (Rack.app.maintcal.TOTAL_QUANTA * Rack.app.maintcal.PIXELS_PER_QUANTA) + Rack.app.maintcal.TITLE_HEIGHT,
            gridCount: 7,
            columnWidth: 1.0,
            disableGrid : config.disableView,
            calendarMode: config.calendarMode || 'default'
    });
    this.rightTimeline = new Rack.app.maintcal.DayViewTimeline({
            navigationParent : config.navigationParent,
            navigationFwd : config.navigation,
            width: 60
    });
    var default_config = {
        layout: "column",
        calendarMode : "default",
        autoScroll: true,
        items: [
            this.leftTimeline,
            this.dayContainer,
            this.rightTimeline
        ]
        /*
        items : [
            {xtype: "panel",
            bodyStyle: "background-color:#FFFF00;",
            height: 400,
            columnWidth: .2
            },
            {xtype: "panel",
            bodyStyle: "background-color:#00FF00;",
            height: 800,
            columnWidth: .3
            },
            {xtype: "panel",
            bodyStyle: "background-color:#00FFFF;",
            height: 800,
            columnWidth: .5
            }
        ]
        */
    };

    Ext.apply(this, config, default_config);
    Ext.Panel.call(this);
    this.addEvents({
        'forward' :true,
        'back' : true
    });

};

Ext.extend(Rack.app.maintcal.ViewBody, Ext.Panel, {

    getCalendarData: function() {
        return this.dayContainer.getCalendarData();
    },

    changeViews: function(start_date,count) {
        this.dayContainer.removeAllDays();
        this.dayContainer.gridCount = count;
        this.dayContainer.fitMultipleGrids(start_date);
        this.dayContainer.doLayout();
        console.log('this.dayContainer');
        console.log(this.dayContainer);
        //this.dayContainer.render(); // Why is this commented out?
        
    }
});

