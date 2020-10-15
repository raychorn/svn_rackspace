/*extern Ext, Rack */

/* DayViewTimeline thingee */

// hard-code time values for now.


Ext.namespace("Rack.app.maintcal.DayViewTimeline");

Rack.app.maintcal.DayViewTimeline = function(config) {
    config = config || {};
    Ext.apply(this,config);
    Ext.Panel.call(this);
    
};
Ext.extend(Rack.app.maintcal.DayViewTimeline, Ext.Panel, {
    initComponent : function() {
        var current_time = new Date().clearTime(); // midnight
        var next_day = current_time.add(Date.HOUR, 24);
        var time_only_fmt = "g:i A"; // hours( no leading zeros) AM/PM
        /*
        var numTimes = Rack.app.maintcal.DAY_MINUTES / Rack.app.maintcal.GRANULARITY;
        var pnl;
        for (i=0; i<numTimes; i++) {
            pnl = new Ext.Panel({
                height: Rack.app.maintcal.PIXELS_PER_QUANTA,
                bodyStyle: "background-color: blue;",
//                items: [
//                    {
//                        xtype: "cool_label",
//                    }
//                ]
            });
//            pnl.items.items[0].setText("cool");
            this.add(pnl);
        }
        */

        var ppq = Rack.app.maintcal.PIXELS_PER_QUANTA;
        var title_height = Rack.app.maintcal.TITLE_HEIGHT;
        var currtm;
        var txt;
        if (this.navigationFwd || this.navigationBck) {
            this.html = ["<table class='timeline' align='center' border='0' >"];
        }
        else {
            this.html = ["<table class='timeline' align='center' border='0' style='margin-top: " + (title_height*0.75) + "px'>"];
        }
        while (current_time < next_day) {
            // in the future this should be a config value of granularity not hard-code
            // hours.
            currtm = current_time.format(time_only_fmt);
            if (currtm.indexOf(":30") > -1) {
                txt = "&mdash;&mdash;&mdash;";
            } else {
                txt = currtm;
            }
            this.html.push(
                "<tr><td><div style='height: " + ppq  + "px; font-size: 11px; text-align: center;'>" + txt + "</div></td></tr>");
            current_time = current_time.add(Date.MINUTE, 30);

        }
        // Add the ending midnight value
        currtm = current_time.format(time_only_fmt);
        txt = currtm;
        this.html.push(
            "<tr><td><div style='height: " + ppq + "px; font-size: 11px; text-align: center;'>" + txt + "</div></td></tr>");
        this.html.push("</table>");
        this.html = this.html.join("");

        // add in navigation support for the exceptions context of the calendar view.
        if(this.navigationBck) {
            this.tbar = [{
                text : '<<',
                tooltip : 'Move back one week',
                handler : this.moveBack,
                scope : this
            }];
            //this.title = '<<<'
        }
        else if (this.navigationFwd) {
            this.tbar = [{
                text : '>>',
                tooltip : 'Move forward one week',
                handler : this.moveForward,
                scope : this
            }];        
        }
        Rack.app.maintcal.DayViewTimeline.superclass.initComponent.call(this);
    },

    moveBack : function() {
        // event arguments are swallowed at this point. As they are unecessary
        this.navigationParent.navigate('back'); 
    },

    moveForward : function() {
        // event arguments are swallowed here too.
        this.navigationParent.navigate('forward');
    }

});

