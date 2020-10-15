/**
*  This is the top-level cardlayout for the right of the screen.
*  This is to allow each button on the left to maintain its own instance
*  of ContentManager in seperate cards.
*/
/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.adminConsole.Center');

Rack.app.maintcal.adminConsole.Center = function() {
    var config = {
        region: 'center',
        header: false,
        layout: 'card',
        bodyStyle: 'background-color: transparent'
    };

    Ext.Panel.call(this,config);
};

Ext.extend(Rack.app.maintcal.adminConsole.Center,Ext.Panel,{

    createContentManager: function(cal_id,calendarData) {
        var acontentManager = new Rack.app.maintcal.adminConsole.ContentManager({
            activeItem : 0,
            id: cal_id,
            generalData: calendarData
        });
        this.add(acontentManager);
        //this.doLayout();
    }
});

