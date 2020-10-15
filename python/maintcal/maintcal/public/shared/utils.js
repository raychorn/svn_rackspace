/**
*  Time tuples need to be used in two different ways:
*
*  1) For display purposes
*  2) For conversions to/from UTC
*
*
*  For 1) we can simple shove a maintcal time value into a local js date object 
*  and display it.
*
*  For 2) we need to load the maintcal time value as a UTC value, and then apply
*  the UTC offset and produce a REAL utc value.
*/

/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal');
Ext.namespace('Rack.msg');

// Constants used by various components for sizing and layout
Rack.app.maintcal.DAY_MINUTES = 24 * 60;
Rack.app.maintcal.GRANULARITY = 30;
Rack.app.maintcal.TOTAL_QUANTA = Rack.app.maintcal.DAY_MINUTES / Rack.app.maintcal.GRANULARITY;

Ext.BLANK_IMAGE_URL = '/maintcal/ext/resources/images/default/s.gif';

// add custom validators
Ext.apply(Ext.form.VTypes, {
    'delta': function (v) { return /^(\.5|\d+\.0|\d+|0\.5|\d+\.5)$/.test(v);},
    'deltaMask': /[\d\.]/i,
    'deltaText': 'Only accepts half hour increments.',
    'numeric' : function (v) { return /^\d+$/.test(v);},
    'numericMask' : /[\d]/i,
    'numericText' : 'Only whole numbers are allowed.'
});

Rack.app.maintcal.eventManager = function () {

    this.queueDataLoaded = false;
    this.categoryDataLoaded = false;
    this.statusDataLoaded = false;

    this.addEvents({
        'queuedataready' : true
    });

    this.on('queuedataready',this.markLoaded,this);
};

Ext.extend(Rack.app.maintcal.eventManager,Ext.util.Observable,{

    /*markLoaded : function(e,args) {
        switch(e) {
            case "queuedataready":
                this.queueDataLoaded = true;
        }
        
    }*/
});

/**
*  A possibly clickable label.
*/
Rack.app.maintcal.Label = Ext.extend(Ext.BoxComponent, {

        /* what is this built out of */
        tag : 'span',

        cls : '',

        /* The initial disabled status */
        disabled : false,

        /* Is this widget currently disabled? */
        is_currently_disabled : false,

        /* The current label text, this is visible */
        html : '',
        title : '',

        /* The enabled and disabled label texts */
        enabledText : false,
        disabledText : false,

        clickHandler: function (e) {this.fireEvent('click', this, e);},

        setText : function(val) {
            this.html = val

            if (this.rendered) {
                this.el.update(this.html);
            }
        },

        disable : function() {
            if (this.is_currently_disabled) {
                return;
            }

            if(this.rendered) {
                if (!this.el.hasClass('disabled')){
                    this.el.addClass('disabled');
                }
            }

            if(this.disabledText) {
                if(this.rendered) {
                    this.el.update(this.disabledText);
                } 
                this.enabledText = this.html;
                this.html = this.disabledText;
            }

            if (this.rendered && this.enableClick) {
                this.el.un('click', this.clickHandler, this);
            }

            this.is_currently_disabled = true;
        },

        enable : function() {
            if (! this.is_currently_disabled) {
                return;
            }

            if(this.rendered && this.el.hasClass('disabled')) {
                this.el.removeClass('disabled');
            }

            if(this.disabledText) {
                if(this.rendered && this.enabledText) {
                    this.el.update(this.enabledText);
                }
                this.html = this.enabledText;
            }

            if (this.rendered && this.enableClick) {
                this.el.on('click', this.clickHandler, this);
            }

            this.is_currently_disabled = false;
        },

        setTitle : function(val) {
            this.title = val;
            if (this.rendered) {
                this.el.dom.setAttribute('title', this.title);
            }
        }, 

        onRender: function (ct, position) {
            var domArgs = {}
            if (!this.el) {
                domArgs.tag = this.tag;
                domArgs.cls = this.cls;
                if (this.title) {
                    domArgs.title = this.title;
                }
                this.el = ct.createChild(domArgs, position);
                if (this.enableClick) {
                    this.el.on('click', this.clickHandler, this);
                }
                if (this.disabled) {
                    this.disable();
                }
            }
            this.el.update(this.html);
        }
});

Rack.app.maintcal.clock = Ext.extend(Rack.app.maintcal.Label, {
    // default time.
    dateObj : new Date(),

    initComponent : function(){
        Rack.app.maintcal.clock.superclass.initComponent.call(this);
        this.setDisplayFormat(this.dateObj);
        this.html = this.dateObj.format(this.displayFormat);
        this.currentInterval = setInterval(this.update.createDelegate(this,[]),10000);
    },

     setDisplayFormat : function(dobj){
        var localOffset = dobj.getTimezoneOffset()/60;
        if(localOffset <= 8 || localOffset >= 4){
            this.displayFormat = "g:i A";
        }
        else{
            this.displayFormat = "G:i";
        }
    },

    update : function(offset){
    

       if(typeof offset === 'undefined'){
            this.dateObj = new Date();
            this.html = this.dateObj.format(this.displayFormat);
            this.el.update(this.html);
        }
        else {
            clearInterval(this.currentInterval);
            var today = new Date();
            this.dateObj = new Date(getMillisecondsInUTC(today,offset));
            this.html = this.dateObj.format(this.displayFormat);
            this.el.update(this.html);
            this.currentInterval = setInterval(this.update.createDelegate(this,[offset]),10000);  
        }

    }

});

Ext.grid.CheckColumn = function(config){
    Ext.apply(this, config);
    if(!this.id){
        this.id = Ext.id();
    }
    this.renderer = this.renderer.createDelegate(this);
};

Ext.grid.CheckColumn.prototype ={
    init : function(grid){
        this.grid = grid;
        this.grid.on('render', function(){
            var view = this.grid.getView();
            view.mainBody.on('mousedown', this.onMouseDown, this);
        }, this);
    },

    onMouseDown : function(e, t){
        if(t.className && t.className.indexOf('x-grid3-cc-'+this.id) != -1){
            e.stopEvent();
            var index = this.grid.getView().findRowIndex(t);
            var record = this.grid.store.getAt(index);
            record.set(this.dataIndex, !record.data[this.dataIndex]);
        }
    },

    renderer : function(v, p, record){
        p.css += ' x-grid3-check-col-td'; 
        return '<div class="x-grid3-check-col'+(v?'-on':'')+' x-grid3-cc-'+this.id+'">&#160;</div>';
    }
};

Rack.app.maintcal.SectionButton = function(config) {
    
    config = config || {};
    Ext.apply(config,{
        id : this.makeButtonId(config.section)
    });
    this.addEvents('click');
    Ext.BoxComponent.call(this,config);

};

Ext.extend(Rack.app.maintcal.SectionButton, Ext.BoxComponent,{

    onRender: function (ct, position) {
        this.el = ct.createChild({
            tag: 'a',
            href: this.href || 'javascript:(function(){return})();',
            target: this.target || '',
            id: this.id,
            cls: this.current ? 'current' : ''
        }, position);
        
        this.el.on('click', function (e) {
            this.fireEvent('click', this, e);
        }, this);

        if (this.text.length > 29) {
            this.textEl = this.el.createChild({
                tag: 'span',
                cls: 'icn-before',
                title: this.text,
                html: Ext.util.Format.ellipsis(this.text,22)
            });
        }
        else {
            this.textEl = this.el.createChild({
                tag: 'span',
                cls: 'icn-before',
                html: this.text
            });
        }
        
        if (this.iconCls) {
            this.textEl.addClass(this.iconCls);
        }
        
        Ext.BoxComponent.superclass.onRender.call(this, ct, position);
    },

    setText: function (t) {
        this.text = t;
        if (this.rendered) {
            this.textEl.dom.innerHTML = t;
        }
        return this;
    },
    
    setIcon: function (i) {
        if (this.rendered) {
            if (this.iconCls) {
                this.textEl.removeClass(this.iconCls);
            }
            this.textEl.addClass(i);
        }
        this.iconCls = i;
    },

    makeButtonId : function(a) {
        return 'mc-admin-bt-' + a.toString();
    },
    
    setHref: function (l) {
        if (this.rendered) {
            this.el.set({href: l});
        }
    }
    
});

function getURLParam(strParamName){
    var strReturn = "";
    var strHref = window.location.href;
    if ( strHref.indexOf("?") > -1 ){
        var strQueryString = strHref.substr(strHref.indexOf("?")).toLowerCase();
        var aQueryString = strQueryString.split("&");
        for ( var iParam = 0; iParam < aQueryString.length; iParam++ ){
            if (aQueryString[iParam].indexOf(strParamName + "=") > -1 ){
                var aParam = aQueryString[iParam].split("=");
                strReturn = aParam[1];
                break;
            }
        }
    return strReturn;
    }
}

function objCompare(a,b){
    for(var name in a){
        if(name in b){
            if(a[name] != b[name]){
                return false;
            }
        }
        else{
            return false;
        }
    }
    return true;
}

function getSecondsInUTC(d){
 return Date.UTC(d.getFullYear(),
            d.getMonth(),
            d.getDate(),
            d.getHours(),
            d.getMinutes(),
            d.getSeconds()) / 1000;
    
}

function getMillisecondsInUTC(d,offset){
    if(typeof offset != 'undefined'){
        return ((d.format('U') * 1000) - (d.format('Z') * 1000)) +
            (offset * 3600000);
    }
    else{
        return (d.format('U') * 1000) + (d.format('Z') * 1000);
    } 
}

function makeMaintcalEpochSeconds(time_tuple) {
    var offset = time_tuple[6];
    var maintcal_time = timeTupleToDate(time_tuple);
    var millis = getMillisecondsInUTC(maintcal_time,offset / 3600);
    return millis / 1000
}

function getMaintcalDate(d,offset) {
    return new Date(getMillisecondsInUTC(d,offset));
}

function newline2Break(s) {
    if (!s) {
        return '';
    }
    else {
        return s.replace(/\n/g, '<br/>');
    }
}

/**
*   This takes a time tuple from the server and converts it to
*   a usable javascript Date.
*
*   The time tuple is in "maintcal time", which is the timezone
*   that has been chosen by the user of maintcal.
*/
function timeTupleToDate(time_tuple) {
    var year = time_tuple[0];
    var month = time_tuple[1] - 1; 
    var day = time_tuple[2];
    var hours = time_tuple[3]; 
    var minutes = time_tuple[4]; 
    var seconds = time_tuple[5];
   
    var new_date = new Date(year, month, day, hours, minutes, seconds, 0);
    return new_date; 
}


function parseWSGIError(wsgi_error){
    var findBreak = /<br\/>/g;
    if(findBreak.test(wsgi_error)){
        var error_response = wsgi_error.split("<br/>");
        error_response = error_response[1].split("<");
        findBreak.lastIndex = 0;
        return error_response[0];
    }
    else{
        return wsgi_error;
    }
}

function loadParent(url, close, do_top) {
    if (url === "") {
        try {
            opener.post_form_reloader();
        } 
        catch(e) {
            try {
                url = opener.location.href;
            } 
            catch(e) {
                url = "/";
            }
        }
    }
    if (url !== "") {
        try {
            if (do_top) {
                opener.top.location.href = url;
            }
            else {
                opener.location.href = url;
            }
        } 
        catch (e) {
            if (do_top) {
                opener.location.href = url;
            }
        }
    }
    if (close) {
        window.close();
    }
}

function isArray(o){
    return o && typeof o === "object" && typeof o.length === "number" && 
        !(o.propertyIsEnumerable('length'));
}

function globalCloseWindow() {
    window.close();
}

/* cascade - function to cascade windows
    parameters:
        WinGroup - name of windowGroup
        cascadeWindow - window to cascade (object)
*/
function cascade(winGroup, cascadeWindow){    
    var windowPosition = [];
    var defaultPos = cascadeWindow.getPosition();
    var atX = defaultPos[0];
    var atY = defaultPos[1];
    var atPos = false;

    var windowList = winGroup.getBy(function(win){
        return true;
    });
    
    winGroup.each(function(win){
        windowPosition = win.getPosition();
        if (windowPosition[0] == atX  && windowPosition[1] == atY){
           atPos = true;
        }   
    });
    
    if (atPos === true && windowList.length > 1){
        atX += 10;
        atY += 25;
        atPos = false;                    
        var x;
        for (x in windowList){
            winGroup.each(function(win){
                windowPosition = win.getPosition();
                if (windowPosition[0] == atX  && windowPosition[1] == atY){
                    atPos = true;
                }   
            });
            
            if (atPos === true){
                atX += 10;
                atY += 25;
                atPos = false;
            }
            else{
                cascadeWindow.setPosition(atX, atY);
                break;
            }
        }
        
    }
    else{
        //don't cascade window
    }
}

Rack.msg = function (title, body) {
    var msgCt = Rack.msg.msgCt;
    var msgTpl = Rack.msg.msgTpl;
    
    if (!msgCt) {
        msgCt = Ext.DomHelper.insertFirst(document.body, {id: 'msg-div', style: 'z-index:20000; position:absolute;'}, true);
        Rack.msg.msgCt = msgCt;
    }
    var m = Ext.DomHelper.append(msgCt, {html: msgTpl.apply({'t': title, 'b': body})}, true);
    msgCt.alignTo(document,'t');
    //msgCt.alignTo(document, 't-t');
    m.slideIn('t', {duration: 0.5}).fadeIn({duration: 0.5, endOpacity: 0.80, useDisplay:true, concurrent: true}).pause(2).ghost('t', {remove: true});
};

Rack.msg.msgCt = null;
Rack.msg.msgTpl = new Ext.XTemplate('<div style="background-color:#eee;',
    'padding:15px; border:1px solid #ccc; font-size:110%; margin-bottom:5px;">',
    '<tpl if="t"><b>{t}</b><br></tpl>{b}',
    '</div>');
Rack.msg.msgTpl.compile();

function notImplemented() {
    Rack.msg('','Not Implemented');

}


function ReloadWindow() {
    var currentURL = window.location.href;
    window.location.href = currentURL;

}

function UASCheck() {

    var findFox2 = /(Firefox|Shiretoko|Chrome|IceCat|Iceweasel)/g;
    if (Ext.isIE || findFox2.test(navigator.userAgent)) {
        return true;
    }
    else {
        Ext.MessageBox.show({
            title: 'Alert',
            msg: 'This is not a supported browser.',
            fn: globalCloseWindow,
            buttons: Ext.MessageBox.OK,
            width: 250
        });
        return false;
    }
};

/*
function Set(a) {
    this.data = {};
    this.type = "set";
    if (typeof a !== Array) {
        throw "ValueError: takes array as contructor argument"
    }
    else {
        var i;
        for (i in a) {
            this.data[a[i]] = true;
        }
    }
    return this;
};

Set.prototype = {
    extend : function(a) {
        if (typeof a === Array) {
            var j;
            for (j in a) {
                this.data[a[j]] = true;
            }
        }
        else {
            this.data[a] = true;
        }
    },

    in : function(a) {
        if (this.data.hasOwnProperty(a)) {
            return true;
        }
        else {
            return false;
        }
    },

    union : function(a) {
        if (a.type && a.type === "set") {
            var rset = new Set();
            var k;
            for (k in a.data) {
                rset.data[a.data[k]] = true;
            }
            return  rset;
        }
        else {
            throw "TypeError: argument must be a Set instance."
        }
    },

    intersection : function(a) {
        if (a.type && a.type === "set") {
            var l;
            for (l in a.data) {
                if (this.data.hasOwnProperty(a.data[l])) {}
            }

        }
        else {
            throw "TypeError: argument must be a Set instance."
        }
    }
};
*/
