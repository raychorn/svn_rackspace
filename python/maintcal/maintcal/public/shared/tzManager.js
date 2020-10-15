/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.tzManager');

Rack.app.maintcal.tzManager = function (config) {

    this.addEvents({
        currenttz : true
    });

    this.cookie_path = '/maintcal/';
    this.cookie_expires = new Date(2147483648000);    
   
    this.tzPicker = new Rack.app.maintcal.tzPicker({
        initialLoad : config.initialLoad
    });
   
    Ext.util.Observable.call(this);

    this.tzPicker.on('picked',this.announceTZ,this);
};

Ext.extend(Rack.app.maintcal.tzManager, Ext.util.Observable, {

    key_name : 'DEFAULT_TZ',
   
    check : function () {
        this.current_default_tz = Rack.readCookie(this.key_name, true);
        if (!this.current_default_tz) {
            return false;
        }
        else {
            return this.current_default_tz;
        }
               
    },
    announceTZ : function(tz_val){
        this.current_default_tz = tz_val;
        try {
            Rack.createCookie(this.key_name,
                this.current_default_tz,
                this.cookie_expires,
                this.cookie_path,
                true
            );
        }
        catch (e) {
            throw "Error saving default timezone";
        }
        this.fireEvent('currenttz',this.current_default_tz,this.tzPicker.initialLoad);
    },
    reset : function () {
        this.tzPicker.initialLoad = false;
        this.tzPicker.show();
    },

    show : function () {
        this.tzPicker.show();
    },

    close : function () {
        this.tzPicker.close();
    }
   
});

