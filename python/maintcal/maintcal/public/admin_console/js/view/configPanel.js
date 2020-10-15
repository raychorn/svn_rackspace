/**
*  This is nothing anymore, we hope ...
*/

/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.adminConsole.ContentManager');

Rack.app.maintcal.adminConsole.ContentManager = function() {
    
    Ext.Panel.call(this);
    this.north = new Rack.app.maintcal.adminConsole.TabNavigator();
    this.center = new Rack.app.maintcal.adminConsole.Content();
};

Ext.extend(Rack.app.maintcal.adminConsole.ContentManager,Ext.Panel,{

    header : false,

    layout : 'border',

    bodyStyle : 'background-color: transparent',

    handleTabNavigation : function(btRef, event_object) {
    alert(btRef.name);
        if (this.layout.activeItem && this.layout.activeItem.id === 'st') {
            return;
        }
        if (btRef.name === 'selectorNav') {
            this.showSelectorTab();    
        } else if (btRef.name === 'detailNav') {
            this.showDetailTab();
        } else if (btRef.name === 'availableDefaultNav') {
            this.showAvailableDefaultTab();
        }
    },

    showDetailTab : function() {
        var current_calendar_id = this.layout.activeItem.id.slice(10);
        this.layout.setActiveItem(current_calendar_id);
    },

    showSelectorTab : function() {
        var cal_rules_id = 'cal_rules_' + this.layout.activeItem.id.toString();
        if (this.items.containsKey(cal_rules_id)) {
            this.layout.setActiveItem(cal_rules_id);
        }
        else {
            var these_rules = new Rack.app.maintcal.selectorRules({
                id : cal_rules_id
            });
            this.add(these_rules);
            this.layout.setActiveItem(cal_rules_id);
        }
    },

    showAvailableDefaultTab : function() {
        var available_defaults_id = 'cal_defaults_' + this.layout.activeItem.id.toString();
        if (this.items.containsKey(available_defaults_id)) {
            this.layout.setActiveItem(available_defaults_id);
        }
        else {
            var these_defaults = new Rack.app.maintcal.CalendarView({
                id : available_defaults_id,
                autoScroll: true
            });
            this.add(these_defaults);
            this.layout.setActiveItem(available_defaults_id);
        }

    }

});

