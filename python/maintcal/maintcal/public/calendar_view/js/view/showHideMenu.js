Rack.app.maintcal.showHideMenu = function (config) {
    this.addEvents({
        statechange: true
    });
    this.cookie_name = 'MCAL_HIDE_STATUS';
    config = config || {};
    Ext.apply(config, {
        defaultAlign : 'br',
        items : [{
            text : 'Nothing to Hide'
        }]
    });
    // default hidden states are: Temporary(1),Tentative(2),Canceled(4),
    // and Completed(5), Completed with issues (7)
    this.default_selections = ["1","4","5","7","8"];
    this.readSelections();
    Ext.menu.Menu.call(this, config);
    this.loadMenu();
    // reload menu based upon the available states for that calendar.
    // as of 08-27-08 they are all the same.
    this.calendarRef.calendarSelector.on('select',this.loadMenu,this);
};

Ext.extend(Rack.app.maintcal.showHideMenu, Ext.menu.Menu, {
    loadMenu : function(c, r, i) {
         if (r) {
            this.removeAll();
            current_states = r.get('available_states');
            var is_checked;
            for (state in current_states) {
                if (this.current_selections.indexOf(state) !== -1) {
                    is_checked = true;
                }
                else {
                    is_checked = false;
                }
                thisItem = new Ext.menu.CheckItem({
                    text : "Hide " + current_states[state],
                    state_id : state,
                    checked : is_checked,
                    checkHandler: this.thisCheckHandler,
                    scope: this
                });
                this.addItem(thisItem);
            } 
        }
    },

    thisCheckHandler : function(menu_item,checked) {
        var index_of_state = this.current_selections.indexOf(
            menu_item.state_id);
        if (index_of_state === -1 && checked) {
            this.current_selections.push(menu_item.state_id);
        }
        else if (index_of_state !== -1 && !checked) {
            this.current_selections.splice(index_of_state,1);
        }
        this.fireEvent('statechange',this);
        this.persistSelections();
    },

    readSelections : function() {
        var from_cookie = Rack.readCookie(this.cookie_name,true);
        if (!from_cookie) {
            this.current_selections = this.default_selections;
        }
        else {
            this.current_selections = from_cookie.split(':');
        }
    },

    persistSelections : function() {
        var serialized_selections = this.current_selections.join(':');
        Rack.createCookie(this.cookie_name,
                        serialized_selections,
                        new Date(2147483648000),
                        '/maintcal/',
                        true);

    }
});


   
