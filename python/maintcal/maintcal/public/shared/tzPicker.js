/*extern Ext, Rack, tznames */

Ext.namespace('Rack.app.maintcal.tzPicker');

Rack.app.maintcal.tzPicker = function (config) {
    this.addEvents({
        picked : true,
        bodyupdate : true
    });

    this.tzaliases = new Rack.app.maintcal.tzalias();

    this.tzList = document.createElement("div");
    this.tzList.className = "mc-bigCal-tz";

    this.content = Ext.get(this.tzList);
    this.eventEl = Ext.get(this.content.firstChild);

    config = config || {};

    Ext.apply(config, {
        height : 420,
        width : 680,
        modal: true,
        draggable : false,
        resizable: false
    });

    this.on('bodyupdate',this.composeDisplay);

    Ext.Window.call(this,config);
};

Ext.extend(Rack.app.maintcal.tzPicker, Ext.Window, {

    initialLoad: false,

    okText : 'OK',

    cancelText : 'Cancel',

    noTZMessage: 'Please select a Timezone.',
    
    defaultContinent: 'Zone Aliases',

    encodeValue : true,

    createTZPicker : function () {
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
                    }
                    if(col2Value){
                        col2Value = col2Value.replace(/_/g,' ');
                    }
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
                    }
                    if(col2Value){
                        col2Value = col2Value.replace(/_/g,' ');
                    }
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
        var totalbuf = newbuf.concat(tzbuf,zonebuf,['</table></div></td><td style="width:50%;"><div style="height:400px;overflow-y:auto;">'],locbuf);
        this.body.update(totalbuf.join(''));        
        this.body.on('click', this.ontzPickerClick, this);
        //this.tzPicker.on('dblclick', this.ontzPickerDblClick, this);
    },
    composeDisplay : function () {
        if (this.initialLoad === true){
            this.setTitle("Please select a default timezone - This will be saved");
        }
        else {
            this.setTitle("Change your default Timezone");
        }
        this.el = this.getEl();
        this.createTZPicker();
        //Selects default Continent
        var pel = Ext.get('defaultContinent');
        pel.addClass('mc-bigCal-tz-sel');
        
        var size = this.el.getSize();
        size.width = size.width - 14;
        this.body.setSize(size);
        this.body.unselectable();
        this.body.child('table').setSize(size);
        this.tzSelContinent = this.defaultContinent;
    },
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
            this.close();
        }
        else if(el.is('button.mc-bigCal-tz-ok')){
            if(typeof this.tzSelection == 'undefined'){
                messageEl.dom.style.display = "block";
            }
            else{
                //this.fireEvent('picked', encodeURIComponent(thismc-bigCal-tz-sel.tzSelection));
                var value_to_pass = this.tzSelection.replace(/ /g,'_');
                if (this.encodeValue) {
                    value_to_pass = encodeURIComponent(value_to_pass);
                }
                this.fireEvent('picked', value_to_pass);
                this.close();
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
                //locElDOM.style.overflow = 'scroll';
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
                }
                else{
                    pel.addClass('mc-bigCal-tz-sel');
                    this.tzSelContinent.removeClass('mc-bigCal-tz-sel');
                    var oldLocElDOM = document.getElementById(this.tzSelContinent.dom.childNodes[0].childNodes[0].data);
                    oldLocElDOM.style.display = 'none';
                    this.tzSelContinent = pel;
                    var locElDOM = document.getElementById(pel.dom.childNodes[0].childNodes[0].data);
                    locElDOM.style.display = 'block';
                    //locElDOM.style.overflow = 'scroll';
                }
                
            }
            else{
                // dont do jack                            
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
                // dont do jack
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
                    if (selRegion === 'Zone Aliases') {
                        this.tzSelection = this.tzaliases.resolveAlias(
                            pel.dom.childNodes[0].childNodes[0].data);
                    }
                    else {
                        this.tzSelection = this.tzSelContinent.dom.childNodes[0].childNodes[0].data + '/' + pel.dom.childNodes[0].childNodes[0].data;
                    }
                }
                else{
                    this.tzSelRegion = pel;
                    if (selRegion === 'Zone Aliases') {
                        this.tzSelection = this.tzaliases.resolveAlias(
                            pel.dom.childNodes[0].childNodes[0].data);
                    }
                    else {
                        this.tzSelection = this.tzSelContinent.dom.childNodes[0].childNodes[0].data + '/' + pel.dom.childNodes[0].childNodes[0].data;
                    }
               }
            }
            // add back the underscores instead of spaces used for display.
            var value_to_pass = this.tzSelection.replace(/ /g,'_');
            if (this.encodeValue) {
                value_to_pass = encodeURIComponent(value_to_pass);
            }
            this.fireEvent('picked', value_to_pass);
            this.close();
        }
        /*else{
            this.ontzPickerClick(e,t);
        }*/
    },
    // override default close function to add support for hiding the window.
    close : function() {
        if (this.closeAction === 'close') {
            Rack.app.maintcal.tzPicker.superclass.close.call(this);
        }
        else if (this.closeAction === 'hide') {
            Rack.app.maintcal.tzPicker.superclass.hide.call(this);
        }
        // default to 'close'
        else {
            Rack.app.maintcal.tzPicker.superclass.close.call(this);
        }
    },
    // override the default Panel afterRender to be able to fire bodyupdate
    // event. 
    afterRender : function(){
        Rack.app.maintcal.tzPicker.superclass.afterRender.call(this);
        this.fireEvent('bodyupdate',this);
    }
});
