/**
* This is the tabbed container for each calendar. It is contained
* by Center.js.
*/

/*extern Ext, Rack */

Ext.namespace("Rack.app.maintcal.adminConsole.ContentManager");

Rack.app.maintcal.adminConsole.ContentManager = function(runtime_config) {

    var config = runtime_config || {};
    Ext.apply(this, config, { 
        header: false,
        bodyStyle: "background-color: transparent"
        //activeItem: 2
    });

    Ext.TabPanel.call(this, config);
    var detail_data = config.generalData;

    /* disable general tab
    * adminv3 addition
    */
    this.general_tab = new Rack.app.maintcal.generalTab({
        title : 'General',
        id : 'general_tab_' + detail_data.id,
        name: detail_data.name + ' Calendar Configuration',
        data : detail_data
        //activeItem : 'general_tab_' + detail_data.id
    });
    this.general_tab.addButton({
        text : 'Save',
        disabled : !detail_data.is_admin,
        handler : this.general_tab.save,
        scope : this.general_tab
    });
    this.general_tab.addButton({
        text : 'Revert',
        disabled : !detail_data.is_admin,
        handler : this.general_tab.revert,
        scope : this.general_tab
    });
    this.add(this.general_tab);
    /*replace general tab with a disabled empty one
    * disable the disabled tab to re-enable adminv3
    this.general_tab = new Ext.Panel({
        title : 'General',
        disabled : true
    });
    */
    // disabled for iteration 1.
    // re-enable for adminv3
    this.selector_tab = new Ext.Panel({
        title: "Selector",
        disabled: true
    });
    this.add(this.selector_tab);
    this.available_defaults_tab = new Rack.app.maintcal.CalendarView({
        calendarId : this.id,
        title: "Default Schedule",
        calendarMode : 'default',
        disableCalendar : !detail_data.is_admin
    });

    this.add(this.available_defaults_tab);
    
    this.available_exceptions_tab = new Rack.app.maintcal.CalendarView({
        calendarId : this.id,
        title: "Schedule Exceptions",
        calendarMode : 'exceptions',
        disableCalendar : !detail_data.is_admin
    });
    this.add(this.available_exceptions_tab);
    this.on('beforetabchange',this.checkContentDirty,this);
    //this.on('show',this.showContent,this);
    //this.available_exceptions_tab.on("show", this.showContent, this);
    //this.available_exceptions_tab.on("resize", this.sizeContents, this);
};

Ext.extend(Rack.app.maintcal.adminConsole.ContentManager, Ext.TabPanel, {
    sizeContents: function () {
        var sz = this.getSize();
        this.available_defaults_tab.setSize(sz.width, sz.height);
    //    this.doLayout();
    },

    tabIsDirty : function() {
        if (this.available_execeptions_tab && this.available_execeptions_tab.checkIsDirty()) {
            return true;
        }
        if (this.available_defaults_tab && this.available_defaults_tab.checkIsDirty()) {
            return true;
        }
        return false;
    },

    promptedSaveHandler : function(btn) {
        if (btn === 'yes') {
            this.current_navigation.saveHandler();
        }
        if (btn === 'no') {
            this.current_navigation.markClean();
            this.setActiveTab(this.requested_navigation); 

        }
    },

    checkContentDirty : function(tabPanel,requested_panel,current_panel) {
        if (current_panel && current_panel.checkIsDirty && current_panel.checkIsDirty()) {
            this.requested_navigation = requested_panel;
            this.current_navigation = current_panel;
            Ext.Msg.show({
                title:'Save Changes?',
                msg: 'Your calendar has unsaved changes. Would you like to save your changes?',
                buttons: Ext.Msg.YESNO,
                fn: this.promptedSaveHandler,
                scope : this,
                icon: Ext.MessageBox.QUESTION
            });
            return false;
        }
    },

    showContent: function() {
        /*
        // hard-coding "general tab" for now.
        var content_id = "general_tab_" + this.id;
        this.layout.setActiveItem(content_id);
        */
        //this.doLayout();
        this.sizeContents();
    }

});

