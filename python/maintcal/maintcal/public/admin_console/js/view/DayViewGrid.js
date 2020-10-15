/*extern Ext, Rack, mouseX, mouseY */

/* DayViewTimeGrid thingee */

Ext.namespace("Rack.app.maintcal.DayViewGrid");

Rack.app.maintcal.DayViewGrid = function(config) {
    config = config || {};
    Ext.apply(this, config);
    Ext.Panel.call(this);
};

var totalQuanta = Rack.app.maintcal.DAY_MINUTES / Rack.app.maintcal.GRANULARITY;
var initial_height = (totalQuanta * Rack.app.maintcal.PIXELS_PER_QUANTA) + Rack.app.maintcal.TITLE_HEIGHT;

Ext.extend(Rack.app.maintcal.DayViewGrid, Ext.Panel, {
    data: undefined,
    granularity: Rack.app.maintcal.GRANULARITY,
    pixelsPerQuanta: Rack.app.maintcal.PIXELS_PER_QUANTA,
    height: initial_height,
    periodPadding: 24,
    gridDate: new Date(),
    initComponent: function() {
        this.dateFormat = {"default": "l", "exception": "D n/j"}[this.calendarMode];
        this.title = this.gridDate.format(this.dateFormat);
        Rack.app.maintcal.DayViewGrid.superclass.initComponent.call(this);
    },

    renderHandler: function() {
        this.table_grid = this.getEl("day-grid");
        this.initializePeriods();
        if (!this.disableGrid) {
            this.header.on("contextmenu", this.titleContextHandler, this);
        }
        this.on("resize", this.resizeHandler);
    },

    resizeHandler: function(obj, width, ht) {
        this.setAllPeriodsSizeAndPosition();
    },

    titleContextHandler: function (evt, div) {
        evt.stopEvent();
        var copyItem = {
            scope: this,
            text: "Copy Schedule",
            handler: this.copyHandler
        };
        var pasteItem = {
            scope: this,
            text: "Paste Schedule",
            handler: this.pasteHandler
        };
        var itms = [copyItem];
        if (Rack.app.maintcal.Clipboard) {
            itms.push(pasteItem);
        }
        // Context menu
        var menu = new Ext.menu.Menu({
            id: "title_menu",
            items: itms
        });
        menu.showAt([mouseX, mouseY]);
    },

    copyHandler: function() {
        Rack.app.maintcal.Clipboard = this.reportData();
    },

    pasteHandler: function() {
        var data = Rack.app.maintcal.Clipboard;
        data.day_info = this.dayInfo;
        this.clearInfo();
        this.recreatePeriods(data);
        this.reRender();
    },

    setAllPeriodsSizeAndPosition: function() {
        this.doLayout();
        this.sortPeriods();
        for (var i=0; i < this.periods.length; i++) {
            this.setPeriodSizeAndPosition(this.periods[i]);
        }
    },
    
    setPeriodSizeAndPosition: function(pd) {
        // Calculate buffer zone between container and the period
        var xPosition = this.periodPadding/2;

        // The period's new width should be the same as it currently is
        // minus the buffer zone (?)
        var width = this.getSize().width - this.periodPadding;

        // The period's new height should stay the same
        var height = pd.end_minutes - pd.start_minutes;

        // Size object to make setting period size easier below
        var new_size = {};
        new_size.height = height;
        new_size.width = width;

        // Assign positional values calculated above to the period
        pd.inResizeHandler = true;
        pd.width = width;
        pd.setSize(new_size);
        pd.setPosition(xPosition, 0);
        pd.inResizeHandler = false;
    },

    initializePeriods: function() {
        this.totalPixels = 24 * (60 / this.granularity) * this.pixelsPerQuanta;
        //this.setHeight(this.totalPixels);
        this.periods = [];
        var dt = this.gridDate;
        var fmt = this.dateFormat;
        if (this.calendarMode === "default") {
            this.dayInfo = dt.format(fmt);
        } else {
            this.dayInfo = this.gridDate;
        }
        if (this.data === undefined) {
            // Create a single empty period
            var pd = this.createPeriod();
            this.add(pd);
            // Period should be rendered as part of the initialization process.
            // No need to call doLayout() here.
        } else {
            this.recreatePeriods(this.data);
        }
    },

    recreatePeriods: function(data) {
        // Use the passed data to create the saved periods
        this.dayInfo = data.day_info;
        var datalen = data.periods.length;
        ////// Periods have to be created in reverse order!! Please don't ask me why!
        ////// (ok, it's because ExtJS does an 'insertBefore' for subsequent 'add's.)
        var i;
        for (i=datalen-1; i>=0; i--) {
            var pd = data.periods[i];
            var newpd = this.createPeriod(this.minutesToPix(pd.start_minutes), this.minutesToPix(pd.end_minutes));
            this.add(newpd);
            newpd.work_units = pd.work_units;
            newpd.comments = pd.comments;
            newpd.setLabel();
        }
    },

    createPeriod: function(periodStart, periodEnd) {
        if (periodStart === undefined) {
            periodStart = 0;
        }
        if (periodEnd === undefined) {
            periodEnd = this.totalPixels;
        }
        var period = new Rack.app.maintcal.PeriodSpan({
            disablePeriod : this.disableGrid,
            container : this
        });
        period.label = new Rack.app.maintcal.Label();
        period.start_minutes = periodStart;
        period.end_minutes = periodEnd;
        period.add(period.label);
        period.mgr = this;
        this.periods.push(period);
        return period;
    },

    tmToPx: function(val) {
        /* Takes a time string in the format "HH:MM" and returns
        the corresponding pixel location. This is the inverse of pxToTmString.
        */
        var hrMin = val.split(":");
        var hrs = parseInt(hrMin[0], 10);
        var mins = parseInt(hrMin[1], 10);
        var minutes = (hrs * 60) + mins;
        return (minutes / this.granularity) * this.pixelsPerQuanta;
    },

    pxToTmString: function(val) {
        /* Takes the pixel values reported by the periods, and returns
        a formatted string like "HH:MM". This is the inverse of tmToPx.
        */
        var minutes = (val / this.pixelsPerQuanta) * this.granularity;
        var hrs = parseInt(minutes/60, 10);
        var mins = minutes % 60;
        if (mins === 0) {
            mins = "00";
        }
        return hrs + ":" + mins;
    },
    
    pxToDate: function(val, fmt) {
        /* Takes a pixel location and optional format string. Returns
        a date value with the equivalent time. If 'fmt' is provided,
        returns the string that results from formatting with the 
        'fmt' value.
        */
        var minutes = (val / this.pixelsPerQuanta) * this.granularity;
		var ret = new Date().clearTime();
		ret = ret.add(Date.MINUTE, minutes);
		if (fmt) {
			ret = ret.format(fmt);
		}
		return ret;
    },

    pxToMinutes: function(val) {
        /* Takes a pixel location and returns the number of minutes
        that corresponds to that location. This is the inverse of minutesToPix.
        */
		return (val / this.pixelsPerQuanta) * this.granularity;
    },

    minutesToPix: function(val) {
        /* Takes a value in minutes, and returns the corresponding pixel
        location. This is the inverse of pxToMinutes.
        */
        return (val / this.granularity) * this.pixelsPerQuanta;
    },

    clearInfo: function() {
        var itemlen = this.items.items.length;
        var i;
        for (i=itemlen; i>=0; i--) {
            this.remove(this.items.items[i], true);
        }
        this.periods = [];
    },
    
    reRender: function() {
        var data = this.reportData();
        this.clearInfo();
        this.recreatePeriods(data);
        this.doLayout();
    },

    reportData: function() {
        /*
        This will be called to get a summary of what the user has configured.
        The report will be in an object with the following structure:
            DayInfo: either the Date this is managing (for exceptions), or the DOW for defaults
            Periods: one or more objects with the following format:
                start_minutes: beginning time of block
                end_minutes: ending time of block
                work_units: number of hours of available work
                comments: optional comments associated with this block
        */
        var periodData = [];
        this.sortPeriods();
        var i;
        for (i=0; i < this.periods.length; i++) {
            var pd = this.periods[i];
            var info = {"start_minutes": this.pxToMinutes(pd.start_minutes), 
                "end_minutes": this.pxToMinutes(pd.end_minutes),
                "work_units": pd.work_units,
                "comments": pd.comments};
            periodData.push(info);
        }
        return {"day_info": this.dayInfo, "periods": periodData};
    },

    sortPeriods: function() {
        var pdSort = function(x, y) {
            if (x.start_minutes < y.start_minutes) {
                return -1;
            } else if (x.start_minutes > y.start_minutes) {
                return 1;
            } else if (x.end_minutes < y.end_minutes) {
                return -1;
            } else if (x.end_minutes > y.end_minutes) {
                return 1;
            } else {
                return 0;
            }
        };
        this.periods.sort(pdSort);
    },

    adjustPeriods: function(obj) {
        this.sortPeriods();
        var numPeriods = this.periods.length;
        // Check for openings at the beginning and end of the day.
        var pd;
        var p0 = this.periods[0];
        var pLast = this.periods[numPeriods-1];
        // Check for open at the beginning
        if (p0.start_minutes > 0) {
            pd = this.createPeriod(0, p0.start_minutes);
        }
        if (pLast.end_minutes < this.totalPixels) {
            pd = this.createPeriod(pLast.end_minutes, this.totalPixels);
        }
        if (numPeriods !== this.periods.length) {
            this.reRender();
            return;
        }
        // Check for overlaps; cycle through until no changes
        // Resort in case any periods were added or removed
        this.adjustBorders(obj);
    },

    adjustBorders: function(obj) {
        this.sortPeriods();
        var changed = false;
        for (var i=0; i < this.periods.length-1; i++) {
            var thispd = this.periods[i];
            var nextpd = this.periods[i+1];
            var thisIsChangedObj = (thispd === obj);
            var nextIsChangedObj = (nextpd === obj);
            if (thispd.end_minutes !== nextpd.start_minutes) {
                changed = true;
                if (thisIsChangedObj) {
                    // thispd was extended over the next period; shorted
                    // the nextpd to compensate
                    this.alterSize(nextpd, thispd.end_minutes, nextpd.end_minutes);
                } else if (nextIsChangedObj) {
                    // nextpd is the changed object, so adjust thispd.
                    this.alterSize(thispd, thispd.start_minutes, nextpd.start_minutes);
                }
            }
        }
        if (changed) {
            this.adjustBorders.defer(0, this, [obj]);
        } else {
            this.reRender();
        }
    },

    alterSize: function(period, periodStart, periodEnd) {
        // Called when a change to a neighboring period overlaps the passed in period
        if (periodStart >= periodEnd) {
            // This period was completely overlapped, so remove it.
            this.removePeriod(period, false);
            return;
        }
        period.start_minutes = periodStart;
        period.end_minutes = periodEnd;
    },

    split: function(origPeriod) {
        // Split the origPeriod into two parts.
        var currQuanta = (origPeriod.end_minutes - origPeriod.start_minutes) / this.pixelsPerQuanta;
        var topPeriodQuanta = currQuanta /2;
        var bottomPeriodQuanta = topPeriodQuanta;
        if (currQuanta % 2) {
            // Not an even split; make the first bigger
            topPeriodQuanta = (currQuanta+1) / 2;
            bottomPeriodQuanta = currQuanta - topPeriodQuanta;
        }
        
        var topPeriodStart = origPeriod.start_minutes;
        var topPeriodLength = topPeriodQuanta * this.pixelsPerQuanta;
        var topPeriodEnd = topPeriodStart + topPeriodLength;

        var bottomPeriodStart = topPeriodEnd;
        var bottomPeriodLength = bottomPeriodQuanta * this.pixelsPerQuanta;
        var bottomPeriodEnd = bottomPeriodStart + bottomPeriodLength;

        var bottomPeriod = this.createPeriod(bottomPeriodStart, bottomPeriodEnd);
        bottomPeriod.start_minutes = bottomPeriodStart;
        bottomPeriod.end_minutes = bottomPeriodEnd;
        // The original period will be left at the top, so 'topPeriod' is 
        // a more descriptive name at this point.
        var topPeriod = origPeriod;
        topPeriod.start_minutes = topPeriodStart;
        topPeriod.end_minutes = topPeriodEnd;
        // this particular day has changed.
        this.parentContainer.markDirty(this);
        this.reRender();
    },

    deletePeriod: function(pd) {
        // Called when the user deletes the period. We need to
        // adjust the following period to fill the time. If there
        // is no following period, adjust the prior one down.
        this.sortPeriods();
        var idxPd = this.periods.indexOf(pd);
        var nextPd = this.periods[idxPd+1];
        var prevPd = this.periods[idxPd-1];
        if (nextPd) {
            nextPd.start_minutes = pd.start_minutes;
        } else {
            prevPd.end_minutes = pd.end_minutes;
        }
        this.removePeriod(pd, true);
        // this particular day has changed.
        this.parentContainer.markDirty(this);
    },

    removePeriod: function(pd, forceRender) {
        var idxPd = this.periods.indexOf(pd);
        this.periods.splice(idxPd, 1);
        if (forceRender) {
            this.reRender();
        }
    }

});

