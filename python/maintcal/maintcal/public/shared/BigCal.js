/**
*
*   copied liberally from:
*
*   Ext JS Library 2.0 Beta 1
*   Copyright(c) 2006-2007, Ext JS, LLC.
*   licensing@extjs.com
*
*   Nathen Hinson 10-30-07 
*/

Ext.bigcal = Ext.extend(Ext.BoxComponent, {

    /**
    *   &#160; to give the user extra clicking room
    */
    okText: "&#160;OK&#160;", 

    /**
    *   The text to display on the cancel button
    */
    cancelText: "Cancel",

    /**
    *   Minimum allowable date (JavaScript date object, defaults to null)
    */
    minDate: null,

    /**
    *   Maximum allowable date (JavaScript date object, defaults to null)
    */
    maxDate: null,

    /**
    *   The error text to display if the minDate validation fails (defaults to "This date is before the minimum date")
    */
    minText: "The date selected is before today",

    /**
    *   The error text to display if the maxDate validation fails (defaults to "This date is after the maximum date")
    */
    maxText: "This date is after the maximum date",

    /**
    *   The default date format string which can be overriden for localization support.  The format must be
    *   valid according to {@link Date#parseDate} (defaults to 'm/d/y').
    */
    format: "m/d/y",

    /**
    *   An array of days to disable, 0-based. For example, [0, 6] disables Sunday and Saturday (defaults to null).
    */
    disabledDays: null,

    /**
    *   The tooltip to display when the date falls on a disabled day (defaults to "")
    */
    disabledDaysText: "",

    /**
    *   JavaScript regular expression used to disable a pattern of dates (defaults to null)
    */
    disabledDatesRE: null,

    /**
    *   The tooltip text to display when the date falls on a disabled date (defaults to "")
    */
    disabledDatesText: "",

    /**
    *   True to constrain the date picker to the viewport (defaults to true)
    */
    constrainToViewport: true,

    /**
    *   An array of textual month names which can be overriden for localization support (defaults to Date.monthNames)
    */
    monthNames: Date.monthNames,

    /**
    *   An array of textual day names which can be overriden for localization support (defaults to Date.dayNames)
    */
    dayNames: Date.dayNames,

    /**
    *   The next month navigation button tooltip (defaults to 'Next Month (Control+Right)')
    */
    nextText: 'Next Month (Control+Right)',

    /**
    *   The previous month navigation button tooltip (defaults to 'Previous Month (Control+Left)')
    */
    prevText: 'Previous Month (Control+Left)',

    /**
    *   The header month selector tooltip (defaults to 'Choose a month (Control+Up/Down to move years)')
    */
    monthYearText: 'Choose a month (Control+Up/Down to move years)',

    /**
    *   Day index at which the week should begin, 0-based (defaults to 0, which is Sunday)
    */
    startDay : 0,

    /**
    *   The tooltip to use as the text on today. Defaults to nothing.
    */
    todayText: '',

    /**
    *   Determine use of highlight to show currently selected day. Defaults to false.
    */
    useActiveDecoration: false,

    /**
    *   Determine use of a Timezone picker in the top menu bar. Defaults to false.
    */
    useTZPicker:false,

    /**
    *   set the width of the calendar.
    */
    calWidth:600,

    /**
    *   The Change TZ button 
    */
    tzPickerText: 'Change the effective Timezone of the calendar',

    /**
    *   Message to display when a timezone has not been selected.
    */
    noTZMessage: 'Please select a Timezone.',

    /**
    *   format to use on times. Defaults to 24-hour format.
    */
    timeFormat: "G:i",

    /**
    *   Is scheduled turned on?
    */
    scheduling: false,

    /**
    *   Default TimeZone to display on TZPicker
    */
    defaultContinent: 'Zone Aliases',
    
    /**
    *
    */
    initComponent: function() {
        Ext.bigcal.superclass.initComponent.call(this);

        // set an timezone offset property. 
        // This will be reset on a effective timezone change.
        this.currentOffset = false;

        // sets default this.value to a date only time.
        if (this.value) {
            this.value = this.value.clearTime();
        } else {
            if (this.currentOffset) {
                this.value = new Date(getMillisecondsInUTC(this.currentOffset)).clearTime();
            } else {
                this.value = new Date().clearTime();
            }
        };

        this.dateNow = new Date();

        this.addEvents({
            /**
            *   @event select
            *   Fires when a date is selected
            *   @param {DatePicker} this
            *   @param {Date} date The selected date
            */
            select: true,
            availableselected:true,
            tzselect:true,
            monthchange:true
        });

        if (this.handler) {
            this.on("select", this.handler,  this.scope || this);
        }

        // initialize tzaliases if useTZPicker is true
        if (this.useTZPicker) {
            this.tzaliases = new Rack.app.maintcal.tzalias();
        }
        this.initDisabledDays();
        atwGroup = new Ext.WindowGroup();
    },

    /**
    *  We disable days that are in the grid but not in the month.
    */
    initDisabledDays: function() {
        if ( ! this.disabledDatesRE && this.disabledDates) {
            var dd = this.disabledDates;
            var re = "(?:";
            for(var i = 0; i < dd.length; i++) {
                re += dd[i];
                if(i != dd.length-1) re += "|";
            }
            this.disabledDatesRE = new RegExp(re + ")");
        }
    },

    setValue: function(value) {
        var old = this.value;
        this.value = value.clearTime(true);
        if (this.el) {
            this.update(this.value);
        }
    },

    /**
    *   Gets the current selected value of the date field
    *   @return {Date} The selected date
    */
    getValue: function() {
        return this.value;
    },

    /**
    *   private
    */
    focus: function() {
        if (this.el) {
            this.update(this.activeDate);
        }
    },

    /**
    *
    */
    onRender: function(container, position) {
        var m = [
             '<table cellspacing="0" style="width:'+this.calWidth.toString()+'px;">',
                '<tr><td class="mc-bigCal-left"><a href="#" title="', this.prevText ,'">&#160;</a></td><td class="mc-bigCal-middle" align="center"><button id="mc-bigCal-mPicker" class="mc-bigCal-hdbtn" title="',this.monthYearText,'"></button><button id="mc-bigCal-tzPicker" class="mc-bigCal-hdbtn" title="',this.tzPickerText,'">Change Timezone</button></td><td class="mc-bigCal-right"><a href="#" title="', this.nextText ,'">&#160;</a></td></tr>',
                '<tr><td colspan="3"><table class="mc-bigCal-inner" cellspacing="0"><thead><tr>'];
        var dn = this.dayNames;
        for(var i = 0; i < 7; i++){
            var d = this.startDay+i;
            if(d > 6){
                d = d-7;
            }
            m.push("<th><span>", dn[d].substr(0,3), ".</span></th>");
        }
        m[m.length] = "</tr></thead><tbody><tr>";
        for(var i = 0; i < 42; i++) {
            if(i % 7 == 0 && i != 0){
                m[m.length] = "</tr><tr>";
            }
            m[m.length] = '<td><a href="#" hidefocus="on" class="mc-bigCal-date" tabIndex="1"><em><span></span></em></a></td>';
        }
        m[m.length] = '</tr></tbody></table></td></tr><tr></table><div class="mc-bigCal-mp"></div><div class="mc-bigCal-tz"></div>';

        var el = document.createElement("div");
        el.className = "mc-bigCal";
        el.innerHTML = m.join("");

        container.dom.insertBefore(el, position);

        this.el = Ext.get(el);
        this.eventEl = Ext.get(el.firstChild);

        var prevEl = this.el.child("td.mc-bigCal-left a");
        var nextEl = this.el.child("td.mc-bigCal-right a");

        prevEl.on('click',this.showPrevMonth,this);
        nextEl.on('click',this.showNextMonth,this);
        
        this.monthPicker = this.el.down('div.mc-bigCal-mp');
        this.monthPicker.enableDisplayMode('block');

        // dont reference the same element for the Timezone picker.
        this.tzPicker = this.el.down('div.mc-bigCal-tz');
        this.tzPicker.enableDisplayMode('block');

        var kn = new Ext.KeyNav(this.eventEl, {
            "left" : function(e){
                e.ctrlKey ?
                    this.showPrevMonth() :
                    this.update(this.activeDate.add("d", -1));
            },

            "right" : function(e){
                e.ctrlKey ?
                    this.showNextMonth() :
                    this.update(this.activeDate.add("d", 1));
            },

            "up" : function(e){
                e.ctrlKey ?
                    this.showNextYear() :
                    this.update(this.activeDate.add("d", -7));
            },

            "down" : function(e){
                e.ctrlKey ?
                    this.showPrevYear() :
                    this.update(this.activeDate.add("d", 7));
            },

            "pageUp" : function(e){
                this.showNextMonth();
            },

            "pageDown" : function(e){
                this.showPrevMonth();
            },

            "enter" : function(e){
                e.stopPropagation();
                return true;
            },

            scope : this
        });

        this.eventEl.on("click", this.handleDateClick,  this, {delegate: "a.mc-bigCal-date"});

        this.eventEl.addKeyListener(Ext.EventObject.SPACE, this.selectToday,  this);

        this.el.unselectable();
        
        this.cells = this.el.select("table.mc-bigCal-inner tbody td");
        this.textNodes = this.el.query("table.mc-bigCal-inner tbody span");

        this.mbtn = Ext.get('mc-bigCal-mPicker');
        this.tzbtn = Ext.get('mc-bigCal-tzPicker');

        this.mbtn.on('click', this.showMonthPicker, this);

        if (! this.useTZPicker) {
            // removes the Timezone Picker button when not required.
            this.tzbtn.dom.style.display = "none";
            
        } else {
            this.tzbtn.on('click',this.showTZPicker,this);
        }

        if (Ext.isIE) {
            this.el.repaint();
        }
        this.update(this.value);
    },


    onMonthClick: function(e, t) {
        e.stopEvent();
        var el = new Ext.Element(t), pn;
        var messageEl = Ext.get("mc-bigCal-invalid-message");
        if(messageEl.dom.style.display == 'block'){
            messageEl.dom.style.display = 'none';
        }
        if(el.is('button.mc-bigCal-mp-cancel')){
            this.hideMonthPicker();
        }
        else if(el.is('button.mc-bigCal-mp-ok')){
            if(this.currentOffset){
                var dateNow = new Date(getMillisecondsInUTC(this.dateNow,this.currentOffset));
                var localDate = new Date(this.mpSelYear, this.mpSelMonth, (this.activeDate || this.value).getDate());
                var offsetDate = new Date(getMillisecondsInUTC(localDate,
                                            this.currentOffset));
                if (offsetDate < dateNow) {
                    messageEl.dom.style.display = "block";
                }
                else {
                    this.update(offsetDate);
                    this.hideMonthPicker();
                }
            }
            else{
                var selectedDate = new Date(this.mpSelYear, this.mpSelMonth, (this.activeDate || this.value).getDate());
                if (selectedDate < this.dateNow) {
                    messageEl.dom.style.display = "block";
                }
                else {
                    this.update(selectedDate);
                    this.hideMonthPicker();
                }
            }
        }
        else if(pn = el.up('td.mc-bigCal-mp-month', 2)){
            this.mpMonths.removeClass('mc-bigCal-mp-sel');
            pn.addClass('mc-bigCal-mp-sel');
            this.mpSelMonth = pn.dom.xmonth;
            
        }
        else if(pn = el.up('td.mc-bigCal-mp-year', 2)){
            this.mpYears.removeClass('mc-bigCal-mp-sel');
            pn.addClass('mc-bigCal-mp-sel');
            this.mpSelYear = pn.dom.xyear;
            
        }
        else if(el.is('a.mc-bigCal-mp-prev')){
            this.updateMPYear(this.mpyear-10);
        }
        else if(el.is('a.mc-bigCal-mp-next')){
            this.updateMPYear(this.mpyear+10);
        }
    },

    onMonthDblClick : function(e, t){
        e.stopEvent();
        var el = new Ext.Element(t), pn;
        var messageEl = Ext.get("mc-bigCal-invalid-message");
        if(messageEl.dom.style.display == 'block'){
            messageEl.dom.style.display = 'none';
        }
        if(pn = el.up('td.mc-bigCal-mp-month', 2)){
            if(this.currentOffset){
                var dateNow = new Date(getMillisecondsInUTC(this.dateNow,this.currentOffset));
                var localDate = new Date(this.mpSelYear, pn.dom.xmonth, (this.activeDate || this.value).getDate());
                var offsetDate = new Date(getMillisecondsInUTC(localDate,
                                        this.currentOffset));
                 if (offsetDate < dateNow) {
                    messageEl.dom.style.display = "block";
                }
                else {
                    this.update(offsetDate);
                    this.hideMonthPicker();
                }
            }
            else{
                var selectedDate = new Date(this.mpSelYear, pn.dom.xmonth, (this.activeDate || this.value).getDate());
                if (selectedDate < this.dateNow) {
                    messageEl.dom.style.display = "block";
                }
                else {
                    this.update(selectedDate);
                    this.hideMonthPicker();
                }
            }
        }
        else if(pn = el.up('td.mc-bigCal-mp-year', 2)){
            if(this.currentOffset){
                var dateNow = new Date(getMillisecondsInUTC(this.dateNow,this.currentOffset));
                var localDate = new Date(pn.dom.xyear, this.mpSelMonth, (this.activeDate || this.value).getDate());
                var offsetDate = new Date(getMillisecondsInUTC(localDate,
                                       this.currentOffset));
                if (offsetDate < dateNow) {
                    messageEl.dom.style.display = "block";
                }
                else {
                    this.update(offsetDate);
                    this.hideMonthPicker();
                }
            }
            else {
                var selectedDate = new Date(pn.dom.xyear, this.mpSelMonth, (this.activeDate || this.value).getDate())
                if (selectedDate < this.dateNow) {
                    messageEl.dom.style.display = "block";
                }
                else {
                    this.update(selectedDate);
                    this.hideMonthPicker();
                }
           }
        }
    },

    hideMonthPicker : function(disableAnim){
        if(this.monthPicker.dom.firstChild){
            if(disableAnim === true){
                this.monthPicker.hide();
            }else{
                this.monthPicker.slideOut('t', {duration:.2});
            }
        }
    },

    // private
    showPrevMonth : function(e){
        var monthNow = this.dateNow.format('n');
        var requestedDate = this.activeDate.add("mo", -1);
        var requestedMonth = requestedDate.format('n');
        if (this.scheduling && requestedMonth < monthNow) {
             var prevEl = this.el.child("td.mc-bigCal-left a");
             prevEl.dom.setAttribute('title','Cannot schedule in the past.');
        }
        else {
            this.update(this.activeDate.add("mo", -1));
        }
    },

    // private
    showNextMonth : function(e){
        var prevEl = this.el.child("td.mc-bigCal-left a");
        if (this.scheduling && prevEl.dom.getAttribute('title') === 'Cannot schedule in the past.') {
            prevEl.dom.setAttribute('title',this.prevText);
        }
        this.update(this.activeDate.add("mo", 1));
    },

    // private
    showPrevYear : function(){
        this.update(this.activeDate.add("y", -1));
    },

    // private
    showNextYear : function(){
        this.update(this.activeDate.add("y", 1));
    },

    // private
    handleDateClick : function(e, t){
        e.stopEvent();
        if(t.dateValue && !Ext.fly(t.parentNode).hasClass("mc-bigCal-disabled") && (t.scheduleTime || t._availableTime)) {
            this.setValue(new Date(t.dateValue));
            this.fireEvent("select", this, this.value);
            if (t._availableTime) {
                this.showAvailableTimeWindow(t);
            } else {
// This doesn't seem to be needed, but leaving it in here in case we
// start noticing odd events.
//                this.suspendEvents();
            }
        }
    },

    selectToday : function(){
        if (this.currentOffset) {
            this.setValue(new Date(getMillisecondsInUTC(new Date().clearTime(),
                            this.currentOffset)));
        } else {
            this.setValue(new Date().clearTime());
        }
        
        this.fireEvent("select", this, this.value);
    },

    handleTimeSelect: function(g,i){
        var clickedSM = g.getSelectionModel();
        var recordSelected = clickedSM.getSelected();
        this.fireEvent("availableselected", recordSelected);
    },
    

    /**
    *  This method is conceptually private
    */
    update : function(date) {
        var oldActiveDate = this.activeDate;
        this.activeDate = date;
        this.cells.removeClass("mc-bigCal-today");
        if(oldActiveDate && this.el){
            var time = date.getTime();
            if(oldActiveDate.getMonth() == date.getMonth() && oldActiveDate.getFullYear() == date.getFullYear()){
                this.cells.removeClass("mc-bigCal-selected");
                this.cells.each(function(c){
                   if(c.dom.firstChild.dateValue == time && this.useActiveDecoration){
                       c.addClass("mc-bigCal-selected");
                       setTimeout(function(){
                            try{c.dom.firstChild.focus();}catch(e){}
                       }, 50);
                       return false;
                   }
                });
                return;
            }
        }
        var prevMonth = new Date(this.start_month_secs * 1000);
        var days = date.getDaysInMonth();
        var firstOfMonth = date.getFirstDateOfMonth();
        // used to what to send to server to get available times.
        this.start_month_secs = getSecondsInUTC(firstOfMonth);
        this.end_month_secs = this.start_month_secs + (days * 86399);
        // see if we need to update.
        /*if(date.getMonth() != prevMonth.getMonth()){
            this.fireEvent('monthchange',this);
        }*/
        this.fireEvent('monthchange',this);
        var startingPos = firstOfMonth.getDay()-this.startDay;

        if(startingPos <= this.startDay){
            startingPos += 7;
        }

        var pm = date.add("mo", -1);
        var prevStart = pm.getDaysInMonth()-startingPos;
        var cells = this.cells.elements;
        var textEls = this.textNodes;
        days += startingPos;

        // convert everything to numbers so it's fast
        var day = 86400000;
        var d = (new Date(pm.getFullYear(), pm.getMonth(), prevStart)).clearTime();
        if(this.currentOffset){
            var localToday = new Date();
            var zoneToday = new Date(getMillisecondsInUTC(localToday,this.currentOffset));
            var today = zoneToday.clearTime().getTime();
        }
        else{
            var today = new Date().clearTime().getTime();
        }
        var sel = date.clearTime().getTime();
        var min = this.minDate ? this.minDate.clearTime() : Number.NEGATIVE_INFINITY;
        var max = this.maxDate ? this.maxDate.clearTime() : Number.POSITIVE_INFINITY;
        var ddMatch = this.disabledDatesRE;
        var ddText = this.disabledDatesText;
        var ddays = this.disabledDays ? this.disabledDays.join("") : false;
        var ddaysText = this.disabledDaysText;
        var format = this.format;

        var setCellClass = function(cal, cell){
            cell.title = "";
            var t = d.getTime();
            cell.firstChild.dateValue = t;
            if(t == today){
                cell.className += " mc-bigCal-today";
                cell.title = cal.todayText;
            }
            // don't set selection decoration.
            /*if(t == sel){
                cell.className += " mc-bigCal-selected";
                setTimeout(function(){
                    try{cell.firstChild.focus();}catch(e){}
                }, 50);
            }*/
            // disabling
            if(t < min) {
                cell.className = " mc-bigCal-disabled";
                cell.title = cal.minText;
                return;
            }
            if(t > max) {
                cell.className = " mc-bigCal-disabled";
                cell.title = cal.maxText;
                return;
            }
            if(ddays){
                if(ddays.indexOf(d.getDay()) != -1){
                    cell.title = ddaysText;
                    cell.className = " mc-bigCal-disabled";
                }
            }
            if(ddMatch && format){
                var fvalue = d.dateFormat(format);
                if(ddMatch.test(fvalue)){
                    cell.title = ddText.replace("%0", fvalue);
                    cell.className = " mc-bigCal-disabled";
                }
            }
        };

        var i = 0;
        for(; i < startingPos; i++) {
            textEls[i].innerHTML = (++prevStart);
            d.setDate(d.getDate()+1);
            cells[i].className = "mc-bigCal-prevday";
            setCellClass(this, cells[i]);
        }
        for(; i < days; i++){
            intDay = i - startingPos + 1;
            textEls[i].innerHTML = (intDay);
            textEls[i].className = ("dayValue_" + intDay);
            d.setDate(d.getDate()+1);
            cells[i].className = "mc-bigCal-active";
            setCellClass(this, cells[i]);
        }
        var extraDays = 0;
        for(; i < 42; i++) {
             textEls[i].innerHTML = (++extraDays);
             d.setDate(d.getDate()+1);
             cells[i].className = "mc-bigCal-nextday";
             setCellClass(this, cells[i]);
        }
        
        if(this.mbtn.dom.hasChildNodes()){
            var curText = this.mbtn.dom.childNodes[0];
            this.mbtn.dom.removeChild(curText);
        }
        var mbtnText = document.createTextNode(this.monthNames[date.getMonth()] + " " + date.getFullYear());
        this.mbtn.dom.appendChild(mbtnText);

        if(!this.internalRender){
            var main = this.el.dom.firstChild;
            var w = main.offsetWidth;
            this.el.setWidth(w + this.el.getBorderWidth("lr"));
            Ext.fly(main).setWidth(w);
            this.internalRender = true;
            // opera does not respect the auto grow header center column
            // then, after it gets a width opera refuses to recalculate
            // without a second pass
            if(Ext.isOpera && !this.secondPass){
                main.rows[0].cells[1].style.width = (w - (main.rows[0].cells[0].offsetWidth+main.rows[0].cells[2].offsetWidth)) + "px";
                this.secondPass = true;
                this.update.defer(10, this, [date]);
            }
        }
    },

    /////////////////////////////////////////////////////////////////////////////
    //
    //  Available Time methods
    //
    /////////////////////////////////////////////////////////////////////////////

    /**
    *  Remove old available time information and add new info.
    */
    setAvailableTime: function (available_time_info) {
        this._removeAvailableTime(); 
        this._addAvailableTime(available_time_info); 
    },

    /**
    *  Remove available time information from all of the cells.
    */
    _removeAvailableTime: function() {
        var count = this.cells.getCount();
        for ( j = 0 ; j < count; j++ ) {
            var cell = this.cells.item(j);
 
            var firstChild = cell.dom.firstChild;

            this._deleteAttributeIfExists(firstChild, '_availableTime');
            this._deleteAttributeIfExists(firstChild, 'calendars');
            this._deleteAttributeIfExists(firstChild, 'window');

            this._removeCellColorClasses(cell);
        }
    },    

    /**
    *  Try to delete an attribute if it exists.
    */
    _deleteAttributeIfExists: function(dom_object, attribute) {
        if (! dom_object[attribute]) {
            return;
        }

        try {
            delete dom_object[attribute];
        } catch (e) {
            dom_object.removeAttribute(attribute);
        }
    },

    /**
    *  Remove cell color classes.
    */
    _removeCellColorClasses: function(cell) {
        if (cell.hasClass('mc-bigCal-green')) {
            cell.removeClass('mc-bigCal-green');
        }
        else if (cell.hasClass('mc-bigCal-yellow')) {
            cell.removeClass('mc-bigCal-yellow');
        }
        else if (cell.hasClass('mc-bigCal-red')) {
            cell.removeClass('mc-bigCal-red');
        }
        else if (cell.hasClass('mc-bigCal-black')) {
            cell.removeClass('mc-bigCal-black');
        }
    },

    /**
    *
    */
    _addAvailableTime: function (available_time_info) {
        var thisEl = this.el;
        var calendars = available_time_info.calendars;

        // set an instance variable for other widgets to access it.
        this.selectedCalendars = calendars;

        //  Remove calendar information from available_time_info
        //  so that it will not show up in the keys
        delete available_time_info.calendars; 
       
        var j;
        var count = this.cells.getCount();
        for ( j = 0 ; j < count; j++ ) {
            var cell = this.cells.item(j);
            this._applyAvailableTimeToCell(cell, available_time_info, calendars);
            this._setCellColor1(cell);
        }
    },

    /**
    *
    */
    _applyAvailableTimeToCell: function(cell, this_range, calendars) {
        var thisNumber = cell.dom.getElementsByTagName('span')[0];

        if (! thisNumber) {
            return 1;
        }

        var thisDay = thisNumber.childNodes[0].data;

        if (calendars) {
            cell.dom.firstChild.calendars = calendars;
        }

        if ( this_range[thisDay] &&
                    (! cell.hasClass("mc-bigCal-prevday") && ! cell.hasClass("mc-bigCal-nextday"))) {

            var available_time_tuples = this_range[thisDay];

            var available_times_for_day = [];

            var requestedMonth = this.activeDate.format('n');

            for ( var i = 0 ; i < available_time_tuples.length ; i++ ) {
                var single_available_time = []

                var start_month = available_time_tuples[i][0][1];

                if (start_month !== requestedMonth) {
                    //delete cell.dom.firstChild._availableTime;
                    continue;
                }

                var start_tzname = available_time_tuples[i][0][7];
                var end_tzname = available_time_tuples[i][1][7];
                var start_tzabbr = available_time_tuples[i][0][8];
                var end_tzabbr = available_time_tuples[i][1][8];

                var start_date = timeTupleToDate(available_time_tuples[i][0]);
                var end_date = timeTupleToDate(available_time_tuples[i][1]);

                single_available_time.push(start_date);
                single_available_time.push(end_date);
                single_available_time.push(start_date.format(this.timeFormat) + " " + start_tzabbr 
                    + ' - ' + end_date.format(this.timeFormat) + ' ' + end_tzabbr);
                single_available_time.push(available_time_tuples[i][0]);
                single_available_time.push(available_time_tuples[i][1]);

                available_times_for_day.push(single_available_time);
            }
            if (available_times_for_day.length === 0) {
                this._deleteAttributeIfExists(cell.dom.firstChild,"_availableTime");
                return;
            }
            cell.dom.firstChild._availableTime = available_times_for_day;
        }
    },

    /**
    *  Set the cell color according to the available time.
    */
    _setCellColor1: function(c) {
        this._removeCellColorClasses(c);

        if (typeof c.dom.firstChild._availableTime == 'undefined') {
            return;
        }

        var avail_time = c.dom.firstChild._availableTime;

        var total_available_time = 0;
        var d;
        for ( d = 0 ; d < avail_time.length ; d++ ) {
            total_available_time += avail_time[d][1].getTime() - avail_time[d][0].getTime();
        }

        var total_length_of_day =  1000 * 60 * 60 * 24;
        var all_time = total_available_time / total_length_of_day;

        var new_class = '';

        if (all_time <= 0.009 ) {
            new_class = '';
        } else if (all_time > 0.009 && all_time <= 0.33) {
            new_class = 'mc-bigCal-red';
        } else if (all_time > 0.33 && all_time < 0.66) {
            new_class = 'mc-bigCal-yellow';
        } else if (all_time >= 0.66) {
            new_class = 'mc-bigCal-green';
        }

        c.addClass(new_class);
    },

    /**
    *
    */
    showAvailableTimeWindow: function(c) {
        if (typeof c._availableTime == 'undefined') {
            return;
        } 

        // generate calendar names from the calendars object.

        var gridTitle = [];
        var overflow_calendars = [];
        var cname;

        for ( cname = 0 ; cname < c.calendars.length ; cname++ ) {
            var inner_name = c.calendars[cname].name;

            overflow_calendars.push(inner_name);

            if (cname <= 3) {
                gridTitle.push(inner_name);
            } else if (cname === 4) {
                gridTitle.push(' ...');
            }
        }

        if (typeof c.window != 'undefined') {                
            if (c.window.hidden) {
                c.window.show();
            } else {
                c.window.focus();
            }
            return;
        }

        var thisGrid = new Ext.grid.GridPanel({
            title: gridTitle,
            frame:true,
            viewConfig: {
                    forceFit:true,
                    templates: {
                        cell: new Ext.Template(
                            '<td class="x-grid3-col x-grid3-cell x-grid3-td-{id} x-selectable {css}" style="{style}" tabIndex="0" {cellAttr}>',
                            '<div class="x-grid3-cell-inner x-grid3-col-{id}" {attr}>{value}</div>',
                            '</td>')
                    }
            },
            store: new Ext.data.SimpleStore({
                    data: c._availableTime,
                    fields: [
                        { name:'start_time', type:'date' },
                        { name:'end_time', type:'date' },
                        { name:'display_string', type:'string' },
                        { name:'start_tuple', type: 'auto'},
                        { name:'end_tuple', type: 'auto' }] }),
            columns: [{header:false, dataIndex:'display_string' }]
        });

        thisGrid.on('render', function () {
            overflow_calendars = overflow_calendars.join('<br />');
            Ext.QuickTips.register({
                target : thisGrid.header,
                text: overflow_calendars
            });
        });                    

        thisGrid.on('rowdblclick', this.handleTimeSelect, this);
      
        c.window = new Ext.Window({
                        title: new Date(c.dateValue).format(this.format),
                        width: 211,
                        height:300,
                        plain:true,
                        frame:true,
                        autoScroll:true,
                        closeAction:'hide',
                        //resizable:false,
                        // Ryan thinks this is a good idea
                        resizable:true,
                        layout:'fit',
                        cls: 'mc-avail-window',
                        items:[thisGrid],
                        manager: atwGroup
                    }); 

        c.window.show();
        cascade(atwGroup, c.window);
        atwGroup.each( function () {
            Ext.QuickTips.register({
                target: c.window.header,
                text: 'Double click to select Available Time'
            });
        });
    },

    /////////////////////////////////////////////////////////////////////////////
    //
    //  Scheduled Time methods
    //
    /////////////////////////////////////////////////////////////////////////////

    /**
    *   scheduled times appear as an array of arrays that show a section
    *   of scheduled time.
    */
    addScheduleTime: function(epoch_range){
        this._removeScheduleTime();
        var f;
        var j;


        for (f=0; f < epoch_range.length; f++) {
            for (j=0; j < this.cells.getCount(); j++) {
                this._applyScheduleTimeInfo(this.cells.item(j),epoch_range[f]);
            };
        }

        var cell_count = this.cells.getCount();

        for ( j = 0 ; j < cell_count ; j++ ) {
            var cell_item = this.cells.item(j);
            this._setCellColor(cell_item);
            this._composeScheduleTimeDisplay(cell_item);
        }
    },

    _removeScheduleTime: function() {
        var cell_count = this.cells.getCount();

        var j;
        for ( j = 0 ; j < cell_count ; j++ ) {
            var cell = this.cells.item(j);
            var first_child = cell.dom.firstChild;

            if (first_child.scheduleTime) {
                first_child.scheduleTime = null;
                first_child.firstChild.firstChild.tip.destroy();
            }

            if (first_child.calendars) {
                first_child.calendars = null;
            }

            if (first_child.calcTime) {
                first_child.calcTime = null;
            }
            
            this._removeCellColorClasses(cell);
        };
    },

    /**
    *
    */
    _applyScheduleTimeInfo: function(c, this_range) {
        var scheduled_item_start = timeTupleToDate(this_range[0]);
        var day_start = new Date(c.dom.firstChild.dateValue);

        var scheduled_item_end = timeTupleToDate(this_range[1]);
        var local_day_end = c.dom.firstChild.dateValue + (86400000 - 1);
        var day_end = new Date(local_day_end);

        // this scheduled item is between the day start and end.
        if (scheduled_item_start.between(day_start, day_end) || 
            scheduled_item_end.between(day_start, day_end)) {
            if ( scheduled_item_start < day_start ) {
                var start_calc = day_start;
            } else {
                var start_calc = scheduled_item_start;
            }

            if ( scheduled_item_end > day_end ) {
                var end_calc = day_end;
            } else {
                var end_calc = scheduled_item_end;
            }

            // apply the range to the calendar cell.
            if(typeof c.dom.firstChild.scheduleTime == 'undefined' ||
                c.dom.firstChild.scheduleTime === null){
                c.dom.firstChild.scheduleTime = [this_range];
            } else{
                c.dom.firstChild.scheduleTime.push(this_range);
            }

            if(typeof c.dom.firstChild.calcTime == 'undefined' ||
                c.dom.firstChild.calcTime === null){
                c.dom.firstChild.calcTime = (end_calc - start_calc);
            } else{
                c.dom.firstChild.calcTime+= (end_calc - start_calc);
            }
        }
    },

    /**
    *   to set a color property on a cellcells based on a date
    */
    _setCellColor: function(c) {
        if(typeof c.dom.firstChild.calcTime == 'undefined' ||
            c.dom.firstChild.calcTime === null){
            new_class = '';
        } else {
            // take total_time out of Date object.
            var all_time = c.dom.firstChild.calcTime/(86400000); // need to handle depth
            if(all_time <= 0.33 && all_time != 0){
                new_class = 'mc-bigCal-green';
            } else if(all_time > 0.33 && all_time < 0.66){
                new_class = 'mc-bigCal-yellow';
            } else if(all_time >= 0.66 && all_time < 0.99){
                new_class = 'mc-bigCal-red';
            } else if(all_time >= 0.99){
                new_class = 'mc-bigCal-black';
            } else {
                new_class = ''; // no special display
            }
        }

        this._removeCellColorClasses(c);

        c.addClass(new_class);
    },

    /**
    *
    */
    _composeScheduleTimeDisplay: function(c) {
        if(typeof c.dom.firstChild.scheduleTime === 'undefined' ||
            c.dom.firstChild.scheduleTime === null) {
            return;
        } 

        // create the html fragment and register the tooltip.
        outA = new Array();
        outA.push({tag:'li', id:'item0', html:'' }); 
        for(a=0; a< c.dom.firstChild.scheduleTime.length;a++){
            var scheduled_item_start = timeTupleToDate(c.dom.firstChild.scheduleTime[a][0]);
            var scheduled_item_end = timeTupleToDate(c.dom.firstChild.scheduleTime[a][1]);

            var day_start = new Date(c.dom.firstChild.dateValue);
            var local_day_end = (c.dom.firstChild.dateValue) + (86400000 - 1);
            var day_end = new Date(local_day_end);

            if( scheduled_item_start < day_start) {
                var start_format_string = this.timeFormat + "(n/j)";
            } else {
                var start_format_string = this.timeFormat;
            }

            if( scheduled_item_end > day_end) {
                var end_format_string = this.timeFormat + "(n/j)";
            } else {
                var end_format_string = this.timeFormat;
            }

            outA.push({tag: 'li',
            id: 'item' + (a + 1).toString(),
            html: scheduled_item_start.format(start_format_string) + 
                  ' ' + c.dom.firstChild.scheduleTime[a][0][8] + 
                  " - " + scheduled_item_end.format(end_format_string) +
                  ' ' + c.dom.firstChild.scheduleTime[a][1][8] + 
                  " : " + c.dom.firstChild.scheduleTime[a][2] 
            });
        };
        var thisID = Ext.id();
        c.dom.firstChild.firstChild.firstChild.setAttribute('id',thisID);
        var toolTipContent =  {
            tag: 'ul', cls: 'mc-bigCal-scheduleTime', children:outA
        };
        c.dom.firstChild.firstChild.firstChild.tip = new Ext.ToolTip({
            target:thisID,
            html:toolTipContent
        });
    },

    /////////////////////////////////////////////////////////////////////////////
    //
    //  Time Zone Picker methods
    //
    /////////////////////////////////////////////////////////////////////////////

    /**
    *
    */
    createTZPicker: function() {
        if(!this.tzPicker.dom.firstChild){
            // apply any zone aliases to the tznames object
            if (! tznames['Zone Aliases']){
                Ext.apply(tznames,this.tzaliases.createAliasDisplay());
                tznames.keys.push('Zone Aliases');
            }
            var tzbuf = ['<table border="0" cellspacing="0"><tr style="height:400px"><td style="width:50%;border-right:1px solid gray;"><div style="height:400px;">'];
            var zonebuf = ['<table id=tableTzContinents border="0" cellspacing="0" style="width:100%;height:100%">'];
            var locbuf = [];
            var a = 0;
            var b = 0;
            var c = 0;
            for(a = 1; a <= tznames.keys.length; a += 2){
                if (tznames.keys[a-1] == this.defaultContinent){
                    zonebuf.push('<tr><td id="defaultContinent" class="mc-bigCal-tz-month"><a href="#">',tznames.keys[a-1],'</a></td>');
                }
                else{
                    zonebuf.push('<tr><td class="mc-bigCal-tz-month"><a href="#">',tznames.keys[a-1],'</a></td>');
                }
                if (tznames.keys[a] == this.defaultContinent){
                    zonebuf.push('<td id="defaultContinent" class="mc-bigCal-tz-month mc-bigCal-tz-sep"><a href="#">',tznames.keys[a], '</a></td></tr>');
                }
                else{
                    zonebuf.push('<td class="mc-bigCal-tz-month mc-bigCal-tz-sep"><a href="#">',tznames.keys[a], '</a></td></tr>');
                }
                //zonebuf.push(
                //    '<tr><td class="mc-bigCal-tz-month"><a href="#">',tznames.keys[a-1],'</a></td><td class="mc-bigCal-tz-month mc-bigCal-tz-sep"><a href="#">',tznames.keys[a], '</a></td></tr>');
                if(typeof tznames[tznames.keys[a-1]] != 'undefined'){
                    if (tznames.keys[a-1] == this.defaultContinent){
                    locbuf.push('<table id="',
                        tznames.keys[a-1],
                        '" border="0" cellspacing="0" style="display:block;width:95%:zoom:1">'); 
                    }
                    else{
                        locbuf.push('<table id="',
                            tznames.keys[a-1],
                            '" border="0" cellspacing="0" style="display:none;width:95%:zoom:1">');
                    }
                    var thisList = tznames[tznames.keys[a-1]].sort();
                    for(b=1;b<=thisList.length;b +=2){
                        var col1Value = thisList[b-1];
                        var col2Value = thisList[b];
                        if(col1Value){
                            col1Value = col1Value.replace(/_/g,' ');
                        };
                        if(col2Value){
                            col2Value = col2Value.replace(/_/g,' ');
                        };
                        locbuf.push('<tr><td class="mc-bigCal-tz-year"><a href="#">',
                            col1Value,
                            '</a></td><td class="mc-bigCal-tz-year"><a href="#">',
                            col2Value,
                            '</a></td></tr>');
                    }
                    locbuf.push('</table>');
                }
                if(typeof tznames[tznames.keys[a]] != 'undefined'){
                    if (tznames.keys[a] == this.defaultContinent){
                    locbuf.push('<table id="',
                        tznames.keys[a],
                        '" border="0" cellspacing="0" style="display:block;width:95%:zoom:1">'); 
                    }
                    else{
                        locbuf.push('<table id="',
                            tznames.keys[a],
                            '" border="0" cellspacing="0" style="display:none;width:95%:zoom:1">');
                    }
                    var anotherList = tznames[tznames.keys[a]].sort();
                    for(c=1;c<=anotherList.length;c +=2){
                        var col1Value = anotherList[c-1];
                        var col2Value = anotherList[c];
                        if(col1Value){
                            col1Value = col1Value.replace(/_/g,' ');
                        };
                        if(col2Value){
                            col2Value = col2Value.replace(/_/g,' ');
                        };
                        locbuf.push('<tr><td class="mc-bigCal-tz-year"><a href="#">',
                            col1Value,
                            '</a></td><td class="mc-bigCal-tz-year"><a href="#">',
                            col2Value,
                            '</a></td></tr>');
                    }
                    locbuf.push('</table>');
                }
            }
            locbuf.push('</div></td></tr><tr class="mc-bigCal-tz-btns"><td colspan="2"><button type="button" class="mc-bigCal-tz-ok">',this.okText,'</button><button type="button" class="mc-bigCal-tz-cancel">',
            this.cancelText,'</button><div id="mc-bigCal-noTZ-message">',this.noTZMessage,'</div></td></tr></table>');
            var newbuf = [];
            var totalbuf = newbuf.concat(tzbuf,zonebuf,['</table></div></td><td style="width:50%;"><div style="height:400px;width:316px;overflow-y:auto;">'],locbuf);
            this.tzPicker.update(totalbuf.join(''));
        };
        this.tzPicker.on('click', this.ontzPickerClick, this);
        //this.tzPicker.on('dblclick', this.ontzPickerDblClick, this);
    },

    /**
    *
    */
    showTZPicker: function() {
        this.createTZPicker();
        //Selects default Continent
        var pel = Ext.get('defaultContinent');
        pel.addClass('mc-bigCal-tz-sel');
        
        var size = this.el.getSize();
        this.tzPicker.setSize(size);
        this.tzPicker.child('table').setSize(size);
        this.tzPicker.slideIn('t', {duration:.2});
        this.tzSelContinent = this.defaultContinent;
    },

    /**
    *
    */
    hideTZPicker: function(disableAnim) {
        if(this.tzPicker.dom.firstChild){
            var pel2 = Ext.get('defaultContinent');
            if(this.tzSelContinent == this.defaultContinent){    
                delete this.tzSelContinent;
                if(typeof this.tzSelRegion != 'undefined'){
                    this.tzSelRegion.removeClass('mc-bigCal-tz-sel');
                    delete this.tzSelRegion;
                }
                if(disableAnim === true){
                    this.tzPicker.hide();
                }
                else{
                    this.tzPicker.slideOut('t', {duration:.2});
                }
            }
            else if(typeof this.tzSelContinent != 'undefined'){
                this.tzSelContinent.removeClass('mc-bigCal-tz-sel');
                oldLocElDOM = document.getElementById(this.tzSelContinent.dom.childNodes[0].childNodes[0].data);
                oldLocElDOM.style.display = 'none';
                pel2.addClass('mc-bigCal-tz-sel');
                defaultLocElDOM = document.getElementById(pel2.dom.childNodes[0].childNodes[0].data);
                defaultLocElDOM.style.display = 'block';
                delete this.tzSelContinent;
                if(typeof this.tzSelRegion != 'undefined'){
                    this.tzSelRegion.removeClass('mc-bigCal-tz-sel');
                    delete this.tzSelRegion;
                }
                if (disableAnim === true) {
                    this.tzPicker.hide();
                } else {
                    this.tzPicker.slideOut('t', {duration:.2});
                }
                   
            } else {
                if (disableAnim === true) {
                    this.tzPicker.hide();
                } else {
                    this.tzPicker.slideOut('t', {duration:.2});
                }
            }
        }
    },

    /**
    *
    */
    ontzPickerClick : function(e, t){
        e.stopEvent();
        var el = Ext.get(t);
        // always get the message element, reset it to hidden if it is 
        // being shown.
        var messageEl = Ext.get("mc-bigCal-noTZ-message");
        if(messageEl.dom.style.display == 'block'){
            messageEl.dom.style.display = 'none';
        }
        if(el.is('button.mc-bigCal-tz-cancel')){
            this.hideTZPicker();
        }
        else if(el.is('button.mc-bigCal-tz-ok')){
            if(typeof this.tzSelection == 'undefined'){
                messageEl.dom.style.display = "block";
            }
            else{
                var value_to_pass = this.tzSelection.replace(/ /g,'_');
                this.fireEvent('tzselect', encodeURIComponent(value_to_pass));
                this.hideTZPicker();
            }
        }
        else if(pn = el.findParentNode('td.mc-bigCal-tz-month')){
            var pel = Ext.get(pn);
            var pel2 = Ext.get('defaultContinent');
            if(typeof this.tzSelContinent == 'undefined'){
                pel2.removeClass('mc-bigCal-tz-sel');
                pel.addClass('mc-bigCal-tz-sel');
                this.tzSelContinent = pel;
                var locElDOM = document.getElementById(pel.dom.childNodes[0].childNodes[0].data);
                locElDOM.style.display = 'block';
                locElDOM.style.overflow = 'auto';
            }
            else if(this.tzSelContinent != pel){
                if (this.tzSelContinent == 'Zone Aliases'){
                    pel2.removeClass('mc-bigCal-tz-sel');
                    pel.addClass('mc-bigCal-tz-sel');
                    var oldLocElDOM = document.getElementById(pel2.dom.childNodes[0].childNodes[0].data);
                    oldLocElDOM.style.display = 'none';
                    this.tzSelContinent = pel;
                    var locElDOM = document.getElementById(pel.dom.childNodes[0].childNodes[0].data);
                    locElDOM.style.display = 'block';
                    locElDOM.style.overflow = 'auto';
                }
                else{
                    pel.addClass('mc-bigCal-tz-sel');
                    this.tzSelContinent.removeClass('mc-bigCal-tz-sel');
                    var oldLocElDOM = document.getElementById(this.tzSelContinent.dom.childNodes[0].childNodes[0].data);
                    oldLocElDOM.style.display = 'none';
                    this.tzSelContinent = pel;
                    var locElDOM = document.getElementById(pel.dom.childNodes[0].childNodes[0].data);
                    locElDOM.style.display = 'block';
                    locElDOM.style.overflow = 'auto';
                    //locElDOM.style.overflow = 'scroll';
                }
                
            }
        }
        else if(pn = el.findParentNode('td.mc-bigCal-tz-year')){
            pel = Ext.get(pn);
            if(typeof this.tzSelContinent == 'undefined'){
                throw "Attempt to select TZ Region without a TZ Continent";
            }
            else{
                if(typeof this.tzSelRegion == 'undefined'){                    
                    pel.addClass('mc-bigCal-tz-sel');
                    this.tzSelRegion = pel;
                    // check to see if this selection is an alias.
                    if (typeof this.tzSelContinent.dom == 'undefined'){
                        var selRegion = 'Zone Aliases';
                    }
                    else {
                        var selRegion = this.tzSelContinent.dom.childNodes[0].childNodes[0].data;
                    }                    
                    if (selRegion === 'Zone Aliases') {
                        this.tzSelection = this.tzaliases.resolveAlias(
                            pel.dom.childNodes[0].childNodes[0].data);
                    }
                    else {
                        this.tzSelection = this.tzSelContinent.dom.childNodes[0].childNodes[0].data + '/' + pel.dom.childNodes[0].childNodes[0].data;
                    }
                }
                else if(this.tzSelRegion != pel){
                    pel.addClass('mc-bigCal-tz-sel');
                    this.tzSelRegion.removeClass('mc-bigCal-tz-sel');
                    this.tzSelRegion = pel;
                    if (typeof this.tzSelContinent.dom == 'undefined' || this.tzSelContinent.dom.childNodes[0].childNodes[0].data == 'Zone Aliases') {
                        var selRegion = 'Zone Aliases';
                    }
                    if (selRegion === 'Zone Aliases') {
                        this.tzSelection = this.tzaliases.resolveAlias(
                            pel.dom.childNodes[0].childNodes[0].data);
                    }
                    else {
                        this.tzSelection = this.tzSelContinent.dom.childNodes[0].childNodes[0].data + '/' + pel.dom.childNodes[0].childNodes[0].data;
                    }
                }
                else{
                // don't do jack
                }
            }
        }
    },

    ontzPickerDblClick : function(e,t){
        e.stopEvent();
        var el = Ext.get(t);
        if(pn = el.findParentNode('td.mc-bigCal-tz-year')){
            pel = Ext.get(pn);
            pel.addClass('mc-bigCal-tz-sel');
            if(typeof this.tzSelContinent == 'undefined'){
                throw "Attempt to select TZ Region without a TZ Continent";
            }
            else{
                if(typeof this.tzSelRegion == 'undefined'){
                    pel.addClass('mc-bigCal-tz-sel');
                    this.tzSelRegion = pel;
                    var thisSelContinent = this.tzSelContinent.dom.childNodes[0].childNodes[0].data;
                    if (thisSelContinent === 'Zone Aliases') {
                        this.tzSelection = this.tzaliases.resolveAlias(
                            pel.dom.childNodes[0].childNodes[0].data);
                    }
                    else {
                        this.tzSelection = this.tzSelContinent.dom.childNodes[0].childNodes[0].data + '/' + pel.dom.childNodes[0].childNodes[0].data;
                    }
                    var value_to_pass = this.tzSelection.replace(/ /g,'_');
                    this.fireEvent('tzselect', this, encodeURIComponent(value_to_pass));
                    this.hideTZPicker();
                }
                else if(this.tzSelRegion != pel){
                    pel.addClass('mc-bigCal-tz-sel');
                    this.tzSelRegion.removeClass('mc-bigCal-tz-sel');
                    this.tzSelRegion = pel;
                    var thisSelContinent = this.tzSelContinent.dom.childNodes[0].childNodes[0].data;
                    if (thisSelContinent === 'Zone Aliases') {
                        this.tzSelection = this.tzaliases.resolveAlias(
                            pel.dom.childNodes[0].childNodes[0].data);
                    }
                    else {
                        this.tzSelection = this.tzSelContinent.dom.childNodes[0].childNodes[0].data + '/' + pel.dom.childNodes[0].childNodes[0].data;
                    }
                    var value_to_pass = this.tzSelection.replace(/ /g,'_');
                    this.fireEvent('tzselect', this, encodeURIComponent(value_to_pass));
                    this.hideTZPicker();
                }
                else{
                    this.tzSelRegion = pel;
                    var thisSelContinent = this.tzSelContinent.dom.childNodes[0].childNodes[0].data;
                    if (thisSelContinent === 'Zone Aliases') {
                        this.tzSelection = this.tzaliases.resolveAlias(
                            pel.dom.childNodes[0].childNodes[0].data);
                    }
                    else {
                        this.tzSelection = this.tzSelContinent.dom.childNodes[0].childNodes[0].data + '/' + pel.dom.childNodes[0].childNodes[0].data;
                    }
                    var value_to_pass = this.tzSelection.replace(/ /g,'_');
                    this.fireEvent('tzselect', this, encodeURIComponent(value_to_pass));
                    this.hideTZPicker();
                }
            }
        }
    },

    /////////////////////////////////////////////////////////////////////////////
    //
    //  Month Picker methods
    //
    /////////////////////////////////////////////////////////////////////////////

    /**
    *
    */
    createMonthPicker: function() {
        if (this.monthPicker.dom.firstChild) {
            return;
        }

        var buf = ['<table border="0" cellspacing="0">'];
        for(var i = 0; i < 6; i++){
            buf.push(
                '<tr><td class="mc-bigCal-mp-month"><a href="#">', this.monthNames[i].substr(0, 3), '</a></td>',
                '<td class="mc-bigCal-mp-month mc-bigCal-mp-sep"><a href="#">', this.monthNames[i+6].substr(0, 3), '</a></td>'
            );
            if (i == 0) {
                buf.push(
                    '<td class="mc-bigCal-mp-ybtn" align="center">',
                    '<a class="mc-bigCal-mp-prev"></a></td><td class="mc-bigCal-mp-ybtn" align="center">',
                    '<a class="mc-bigCal-mp-next"></a></td></tr>');
            } else {
                buf.push(
                    '<td class="mc-bigCal-mp-year"><a href="#"></a></td>',
                    '<td class="mc-bigCal-mp-year"><a href="#"></a></td></tr>');
            }
        }
        buf.push(
            '<tr class="mc-bigCal-mp-btns"><td colspan="4"><button type="button" class="mc-bigCal-mp-ok">',
                this.okText,
                '</button><button type="button" class="mc-bigCal-mp-cancel">',
                this.cancelText,'</button>',
                '<div id="mc-bigCal-invalid-message">',this.minText,'</div>',
                '</td></tr></table>'
        );
        this.monthPicker.update(buf.join(''));
        this.monthPicker.on('click', this.onMonthClick, this);
        this.monthPicker.on('dblclick', this.onMonthDblClick, this);

        this.mpMonths = this.monthPicker.select('td.mc-bigCal-mp-month');
        this.mpYears = this.monthPicker.select('td.mc-bigCal-mp-year');

        this.mpMonths.each(function(m, a, i){
            i += 1;
            if((i%2) == 0){
                m.dom.xmonth = 5 + Math.round(i * .5);
            }else{
                m.dom.xmonth = Math.round((i-1) * .5);
            }
        });
    },

    showMonthPicker : function() {
        this.createMonthPicker();
        var size = this.el.getSize();
        this.monthPicker.setSize(size);
        this.monthPicker.child('table').setSize(size);

        this.mpSelMonth = (this.activeDate || this.value).getMonth();
        this.updateMPMonth(this.mpSelMonth);
        this.mpSelYear = (this.activeDate || this.value).getFullYear();
        this.updateMPYear(this.mpSelYear);

        this.monthPicker.slideIn('t', {duration:.2});
    },

    updateMPYear : function(y){
        this.mpyear = y;
        var ys = this.mpYears.elements;
        for(var i = 1; i <= 10; i++){
            var td = ys[i-1], y2;
            if((i%2) == 0){
                y2 = y + Math.round(i * .5);
                td.firstChild.innerHTML = y2;
                td.xyear = y2;
            }else{
                y2 = y - (5-Math.round(i * .5));
                td.firstChild.innerHTML = y2;
                td.xyear = y2;
            }
            this.mpYears.item(i-1)[y2 == this.mpSelYear ? 'addClass' : 'removeClass']('mc-bigCal-mp-sel');
        }
    },

    updateMPMonth : function(sm){
        this.mpMonths.each(function(m, a, i){
            m[m.dom.xmonth == sm ? 'addClass' : 'removeClass']('mc-bigCal-mp-sel');
        });
    }
});

Ext.reg('BigCal', Ext.bigcal);
                  
