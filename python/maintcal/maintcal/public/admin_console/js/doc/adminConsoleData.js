/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.adminConsole');

Rack.app.maintcal.adminConsole = function(config) {

    this.connection = new Ext.data.Connection({timeout: 60000});
    Ext.util.Observable.call(this);
    this.addEvents({
        'calendarloaded' : true,
        'queuesloaded' : true
    });

    // this should always be populated on the initial app load.
    this.calendarData = {};
    this.queueData = {};
    this.subCatData = {};
    this.statusData = {};

    // core auth cookie info.
    this.core_cookie_path = '/';
    this.core_auth_cookie_key = 'redacted_admin_session';

    // maintcal cookie info.
    this.cookie_path = '/maintcal/';
    this.cookie_expires = new Date(2147483648000);
    this.console_last_action_key = 'LAST_ACT';

    // object to loaded categories 
    this.catLoadTask = new Rack.app.maintcal.adminConsole.categoriesAsNeeded(this);
    this.statLoadTask = new Rack.app.maintcal.adminConsole.statusesAsNeeded(this);
};

Ext.extend(Rack.app.maintcal.adminConsole,Ext.util.Observable,{
});
