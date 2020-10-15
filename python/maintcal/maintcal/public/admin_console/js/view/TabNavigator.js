/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.adminConsole.TabNavigtor');

/**
*  This is the top row of the content.
*/
Rack.app.maintcal.adminConsole.TabNavigator = function(parent_container) {
    
    // default constructor 
    Ext.Panel.call(this);

    this.parent_container = parent_container;
    this.disabledNav = true;
    // this sets up the psuedo tabs for navigation.
    this.detailNav = new Rack.app.maintcal.Label(
        {
            name : 'detailNav',
            html : 'Calendar Details',
            cls : 'mc-cal-nav',
            enableClick : true,
            disabled : this.disabledNav
        });
    this.detailNav.on('click',this.parent_container.center.handleTabNavigation,this.parent_container.center);
    this.add(this.detailNav);

    this.availableDefaultNav = new Rack.app.maintcal.Label(
        {
            name : 'availableDefaultNav',
            html : 'Available Time Defaults',
            cls  : 'mc-cal-nav',
            enableClick : true,
            disabled : this.disabledNav
        });
    this.availableDefaultNav.on('click',this.parent_container.center.handleTabNavigation,this.parent_container.center);
    this.add(this.availableDefaultNav);
    
    /* disabled for this iteration of the adminConsole
    this.selectorNav = new Rack.app.maintcal.Label(
        {
            name : 'selectorNav',
            html : 'Calendar Selector Rules',
            cls : 'mc-cal-nav',
            enableClick : true
        });
    this.selectorNav.on('click',this.handleCalendarNavigation,this);
    */
};

Ext.extend(Rack.app.maintcal.adminConsole.TabNavigator,Ext.Panel, {

    region: 'north',

    bodyStyle : 'background-color: transparent',

    border: false,

    height: 25,

    disableNavigation : function() {
        this.items.each(function(btRef) {
            if (!btRef.disabled) {
                btRef.disable();
            }
        });
    },

    enableNavigation : function() {
        this.items.each(function(btRef) {
            if (btRef.disabled) {
                btRef.enable();
            }
        });
    }

});


