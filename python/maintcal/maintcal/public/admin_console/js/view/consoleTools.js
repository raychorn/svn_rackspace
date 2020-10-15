/**
*  This is the top-level buttons on the bottom of the screen.
*/
/*extern Ext, Rack, notImplemented */

Ext.namespace('Rack.app.maintcal.consoleTools');

Rack.app.maintcal.consoleTools = function(config) {

    // get initial configs or none.
    config = config || {};

    // built-in configs
    Ext.apply(config,{
        region : 'south',
        height : 25,
        buttons : [{
            text : 'Add New Calendar',
            iconCls : 'mc-c-tool',
            handler : notImplemented,
            scope : this
        },{
            text : 'Add New Maintenance Category',
            iconCls : 'mc-c-tool',
            handler : notImplemented,
            scope : this
        }]
    });

    /*this.addCalendarWizard = new Rack.app.maintcal.configWizard({
        title : "Add Calendar Wizard"
    });
    var wizardTask = new Rack.app.maintcal.createAddWizard(
        this.addCalendarWizard,this.doc);
    wizardTask.start();

    this.addCategoryWizard = new Rack.app.maintcal.configWizard({
        title : 'Add Maintenance Category Wizard'
    });
    var catTask = new Rack.app.maintcal.createCategoryWizard(
        this.addCategoryWizard,this.doc);
    catTask.start();
    */
    Ext.Toolbar.call(this,config);
};

Ext.extend(Rack.app.maintcal.consoleTools,Ext.Toolbar,{

    showAddCalendar : function() {
        this.addCalendarWizard.show();
    },

    showAddCategory : function() {
        this.addCategoryWizard.show();
    }

});

