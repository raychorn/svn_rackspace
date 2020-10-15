/*extern Ext, Rack, mouseX, mouseY */

Ext.namespace('Rack.app.maintcal.PeriodSpan');

Rack.app.maintcal.PeriodSpan = function(config) {
    this.inResizeHandler = true;
    this.created = false;
    this.lastEvent = new Date();
    this.work_units = 0;
    this.comments = "";

    config = config || {};

    Ext.apply(this,config, {
        cls: "periodspan",
        hideCollapseTool: true,
        minButtonWidth: 10,
        plain: true,
        wrap:true,
        shadow: false,
        background: 'transparent',
        autoScroll: false,
        bodyStyle: "padding:4px;"
    });

    Ext.Panel.call(this);
};

Ext.extend(Rack.app.maintcal.PeriodSpan,Ext.Panel, {
    afterRender: function() {
        Rack.app.maintcal.PeriodSpan.superclass.afterRender.call(this);
        this.mgr.setPeriodSizeAndPosition(this);
        this.label = this.items.items[0];
        this.inResizeHandler = false;
        this.setLabel();
        this.created = true;
        if(!this.disablePeriod) {
            this.getEl().on("contextmenu", this.rightclickHandler, this);
        }

        this.resizer = new Ext.Resizable(this.getEl(), {
            handles: "n s",
            enabled : !this.disablePeriod,
            heightIncrement: this.mgr.pixelsPerQuanta
        });
        this.resizer.on("resize", this.resizeHandler, this);
    },

    setLabel: function(sz) {
        if (sz === undefined) {
            sz = this.end_minutes - this.start_minutes;
        }
        // Time is in minutes, so convert to hours
        var periodTime = ((sz / this.mgr.pixelsPerQuanta) * this.mgr.granularity) / 60;
        var workTime = this.work_units;
        var time_only_fmt = "g:i A"; // hours( no leading zeros) AM/PM
        // creating custom classes for disabled periods is because the CSS rules do not appear to work otherwise.
        // i.e. just adding a 'disabled' class to the item. 
        var cls = this.disablePeriod ? "period_normal_disabled" : "period_normal";
        var oldcls = this.disablePeriod ? "period_empty_disabled" : "period_empty";
        var lblcls = this.disablePeriod ? "period_label_disabled" : "period_label";
        var oldlblcls = this.disablePeriod ? "period_label_zero_disabled" : "period_label_zero";
        if (workTime === 0) {
            cls = this.disablePeriod ? "period_empty_disabled" : "period_empty";
            oldcls = this.disablePeriod ? "period_normal_disabled" : "period_normal";
            lblcls = this.disablePeriod ? "period_label_zero_disabled" : "period_label_zero";
            oldlblcls = this.disablePeriod ? "period_label_disabled" : "period_label";
        }
        this.label.removeClass(oldlblcls);
        this.label.addClass(lblcls);
        this.removeClass(oldcls);
        this.addClass(cls);
        var punits = " hrs.";
        var wunits = " hrs.";
        if (Math.abs(periodTime - 1) < 0.1) {
            punits = " hr.";
        }
        if (Math.abs(workTime - 1) < 0.1) {
            wunits = " hr.";
        }        
        var tm_start_minutes = this.mgr.pxToDate(this.start_minutes, time_only_fmt);
        var tm_end_minutes = this.mgr.pxToDate(this.end_minutes, time_only_fmt);
//        var labelText = "Start: " + this.mgr.pxToTmString(this.start_minutes) + "<br/>End: " + this.mgr.pxToTmString(this.end_minutes) + "<br/>Work: " + workTime + wunits;
        var labelText = tm_start_minutes + "-" + tm_end_minutes + "<br/>Work: " + workTime + wunits;
        if (this.comments) {
            labelText = labelText + '<br/>&nbsp;<br/><span class="period_comment">' + this.comments + "</span>";
        }
        this.label.setText(labelText);
    },
    
    rightclickHandler: function (evt, div) {
        evt.stopEvent();
        // Context menu
        var itms = [
            {
                scope: this,
                text: "Set Available Work",
                handler: this.workHandler
                
            },
            {
                scope: this,
                text: "Set Comment",
                handler: this.commentHandler
                
            },
            {
                scope: this,
                text: "Split",
                handler: this.splitHandler
            }
        ];
        if (this.mgr.periods.length > 1) {
            itms.push({
                scope: this,
                text: "Delete",
                handler: this.deleteHandler
            });
        }
        var menu = new Ext.menu.Menu({
            id: "period_menu",
            items: itms
        });
        menu.showAt([mouseX, mouseY]);
    },
    
    splitHandler: function(itm, evt) {
        this.mgr.split(this);
    },

    deleteHandler: function(itm, evt) {
        this.mgr.deletePeriod(this, true);
    },

    workHandler: function(itm, evt) {
        var wunits = this.work_units.toString();
        Ext.Msg.prompt("Available Work Hours", "Number of work hours for this period?",
            function(btn, txt) {
                if (btn === "ok") {
                    if (!txt) {
                        // They clicked OK, but didn't enter anything
                        return;
                    }
                    var intval = parseFloat(txt, 10);
                    if (isNaN(intval) || (intval % 0.5 !== 0)) {
                        Ext.Msg.alert("Warning","'" + txt + "' is not a valid number or is not in half-hour increments");
                    } else {
                        this.work_units = intval;
                        // this particular day has changed.
                        this.mgr.parentContainer.markDirty(this.mgr);
                        // Using 'defer' because sometimes the CSS doesn't update otherwise.
                        this.setLabel.defer(100, this);
                    }
                }
            }, this, false, wunits);
    },

    commentHandler: function(itm, evt) {
        Ext.Msg.prompt("Comment", "Enter an optional comment for this period",
            function(btn, txt) {
                if (btn === "ok") {
                    this.comments = txt;
                    this.setLabel();
                    // this particular day has changed.
                    this.mgr.parentContainer.markDirty(this.mgr);
                }
            }, this, true, this.comments
        );
    },

    resizeHandler: function(obj, width, ht) {
        // NOTE: 'obj' is the Resizable object that wraps the period panel
        // not the period Panel itself.

        // Since many things in the resize handler can generate resize events,
        // use the following flag to prevent recursive calls.
        if (this.inResizeHandler) {
            return;
        }
        // Object hasn't been fully defined yet, so skip resize events.
        if (!this.created) {
            return;
        }

        var thisPos = this.getPosition(true);
        var thisTop = thisPos[1] + this.start_minutes;
        var maxEnd = this.mgr.totalPixels;

        this.inResizeHandler = true;
        if (thisTop < 0) {
            ht = ht + thisTop;
            thisTop = 0;
        }
        
        var newStart = thisTop;
        var newSize = ht;
        var newEnd = newStart + newSize;
        var oversize = Math.max(0, (newEnd - maxEnd));
        newEnd = newEnd - oversize;
        this.start_minutes = newStart;
        this.end_minutes = newEnd;
        this.setLabel(newSize, this);
        // Adjust periods to match
        this.mgr.adjustPeriods(this);
        // this particular day has changed.
        this.mgr.parentContainer.markDirty(this.mgr);
        this.inResizeHandler = false;
    }
    
});
Ext.reg("period_span", Rack.app.maintcal.PeriodSpan);

