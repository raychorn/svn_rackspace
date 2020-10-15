/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.DayViewContainer');

Rack.app.maintcal.DayViewContainer = function(config) {
    var default_config = {
        calendarMode: "default"
    };
    Ext.apply(this, config, default_config);
    Ext.Panel.call(this);
};

Ext.extend(Rack.app.maintcal.DayViewContainer, Ext.Panel, {
    gridCount: 1,
    layout: 'column',
    startdate: new Date(),
    initComponent: function() {
        this.data = this.massageCalendarData(this.data);
        // Need to move the start date to fall on the designated
        // starting day of the week.
        var dow = this.startdate.format("w"); //returns DOW
        var offset = -1 * (dow - Rack.app.maintcal.STARTING_DAY_OF_WEEK);
        this.startdate = this.startdate.add(Date.DAY, offset);
        if (this.gridCount === 1) {
            this.items = [
                new Rack.app.maintcal.DayViewGrid({
                    columnWidth: "100%",
                    parentContainer : this,
                    calendarMode: this.calendarMode,
                    gridDate: this.startdate,
                    height: this.height + Rack.app.maintcal.TITLE_HEIGHT
                })
            ];
        } else {
            this.fitMultipleGrids();
        }               
        Rack.app.maintcal.DayViewContainer.superclass.initComponent.call(this);
    },

    massageCalendarData : function(data) {
        var js_dow;
        var packaged_data;
        packaged_data = {};
        for( js_dow in data ) {
            if (! data.hasOwnProperty(js_dow) ) {
                continue;
            }
            packaged_data[js_dow] = {};
            packaged_data[js_dow].day_info = js_dow;
            packaged_data[js_dow].periods = [];
            for( var i = 0 ; i < data[js_dow].length ; i++ ) {
                if (data[js_dow][i].disabled) {
                    packaged_data[js_dow].disabled = true;
                }
                else {
                    packaged_data[js_dow].disabled = false;
                }
                if (data[js_dow][i].last_modified && !this.last_modified) {
                    this.last_modified = data[js_dow][i].last_modified;
                }
                packaged_data[js_dow].periods.push(data[js_dow][i]);
            }
       }
       return packaged_data;
    },

    getCalendarData: function() {
        var data = {};
        for (var i=0; i<this.items.items.length; i++) {
            var grd = this.items.items[i];
            var dtInfo = grd.reportData();
            data[dtInfo.day_info] = dtInfo.periods;
        }
        data.last_modified = this.last_modified;
        return data;
    },

    /**
    *
    */
    fitMultipleGrids: function() {
        this.items = this.items || [];
        var gridDate = this.startdate;
        var dvg;
        var wd;

        for (var i=1; i<=this.gridCount; i++) {
            var data_key;
            // use a different day key for defaults and exceptions.
            // an day of week 'int' for defaults and a date for exceptions.
            if (this.calendarMode === "exception") {
                //data_key = [gridDate.getFullYear(),gridDate.getMonth() + 1,gridDate.getDate()];
                data_key = gridDate.format("Y,n,j");
            } else {
                data_key = parseInt(gridDate.format('w'),10);
            }

            // make a new daygrid for each one requested. 
            wd = this.determineDayWidths(i);

            // check to see if we need to disable the DayViewGrid
            var disableGrids = (((this.calendarMode === "exception") && 
                                    (this.data[data_key].disabled)) || this.disableGrid);

            dvg = new Rack.app.maintcal.DayViewGrid({
                // check to see if this grid date is before today
                disableGrid : disableGrids,
                parentContainer : this,
                data : this.data[data_key],
                columnWidth: wd,
                calendarMode: this.calendarMode,
                gridDate: gridDate,
                height: this.height + Rack.app.maintcal.TITLE_HEIGHT
            
            });

            dvg.on("render", dvg.renderHandler, dvg);
            this.items.push(dvg);
            gridDate = gridDate.add(Date.DAY, 1);
        }
    },

    reload : function(data) {
        this.data = this.massageCalendarData(data);
        this.removeAllDays();
        this.fitMultipleGrids();
        //this.doLayout();
    },

    determineDayWidths: function(current_count) {
        return 1/this.gridCount;
    },

    /* deprecated in favor of reloading the entire calendar view.
    forward: function() {
       // remove the first item and add a new DayViewGrid to the back.
       this.remove(this.items.first());
       var day_to_add =  new Rack.app.maintcal.DayViewGrid({
                    columnWidth: this.determineDayWidths(i),
                    height: 560,
                    gridDate: this.items.last().gridDate.add(Date.DAY,1)
                });
       var added_day = this.add(day_to_add);
       //added_day.container = this;
       //added_day.render();
       //day_to_add.render();
       this.doLayout();
    },
    */

    markDirty : function(gridRef) {
        this.dirty = true;
    },

    removeAllDays: function() {
        if (this.items) {
            var f;
            while(f === this.items.first()){
                this.remove(f);
            }
        }
        this.items = [];
        ///delete this.items;

    }
});
