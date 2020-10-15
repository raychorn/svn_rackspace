/**
*  This is just the container for the buttons on the left of the admin screen.
*/

/*extern Ext, Rack, global_view, global_doc */

Ext.namespace('Rack.app.maintcal.consoleNaviator');

Rack.app.maintcal.consoleNavigator = function(runtime_config) {

    // setup custom events
    this.addEvents({dataerror:true});

    // get initial configs or none.
    var config = runtime_config || {};

    // built-in configs
    Ext.apply(this,config,{
        region : 'west',
        width : 220,
        margins : '0 5 0 5',
        border: false,
        bodyStyle : 'background-color: transparent',
        autoScroll : true,
        cls: 'mc-navigation'
    });

    // setup events
    //this.on('render', this.initTask.start, this);
    this.on('dataerror',this.handleDataError,this);

    Ext.Panel.call(this,config);
};

Ext.extend(Rack.app.maintcal.consoleNavigator,Ext.Panel,{

    initComponent : function() {
        Rack.app.maintcal.consoleNavigator.superclass.initComponent.call(this);

        this.addEvents({
            dataerror : true
        });

        this.on('dataerror',this.handleDataError,this);

    },

    handleDataError : function(r,o) {
        this.fireEvent('dataerror',r,o);
    },

    clearCurrent : function() {
        var thisEl = this.getEl();
        var currentEls = thisEl.select('.current');
        currentEls.each(function(bt) {
            bt.removeClass('current');
        });
    },

    makeSectionButtons : function() {
        var serviceTypeButton = new Rack.app.maintcal.SectionButton({
            section : 'st',
            text : 'Service Type Admin',
            cls : 'mc-navigation',
            iconCls : 'mc-stype-config'
        });
        serviceTypeButton.on('click',this.handleNavigationRequest,this);
        this.add(serviceTypeButton);

        // cycle through all calendars and put in buttons for them.
        var calendar_data = this.doc.calendarData;

        var cal_id;
        for (cal_id in calendar_data) {
            if (! calendar_data.hasOwnProperty(cal_id)) {
                continue;
            }
            var thisCal = calendar_data[cal_id];
            var thisCalButton = new Rack.app.maintcal.SectionButton({
                section : cal_id,
                text : thisCal.name,
                cls : 'mc-navigation'
            });
            thisCalButton.on('click',this.handleNavigationRequest,this);
            this.add(thisCalButton);
        }

        this.view.loadcalendarsTask.unmaskView(this.view.vport);
        this.doLayout();
    },

    /**
     *  Handle requests to save data in the center panel
     */
    promptedSaveHandler : function(btn) {
        var calendar_view_ref = global_view.center.layout.activeItem.getActiveTab();
        if (btn === 'yes') {
            calendar_view_ref.saveHandler();
        }
        if (btn === 'no') {
            calendar_view_ref.markClean();
            this.handleNavigationRequest(this.current_nav_section_button);
        }
    },
    /**
    *  This is called when a section button on the left is clicked.
    */
    handleNavigationRequest : function(section_button) {
        var tab_is_dirty = false;
        if (global_view.center.layout.activeItem && global_view.center.layout.activeItem.getActiveTab) {
            var calendar_ref = global_view.center.layout.activeItem.getActiveTab();
            if (calendar_ref) {
                tab_is_dirty = calendar_ref.checkIsDirty();
            }
        }
        var section_id = section_button.id.slice(12);
        // force a check to see if the active tab is dirty and ...
        // fail the navigation if there is a task in progress ... as determined by masking ... hmmm ... maybe not
        // a good idea ... oh well.
        if(global_view.center.el.isMasked() || tab_is_dirty) {
            if (tab_is_dirty) {
                this.current_nav_section_button = section_button;
                Ext.Msg.show({
                    title:'Save Changes?',
                    msg: 'Your calendar has unsaved changes. Would you like to save your changes?',
                    buttons: Ext.Msg.YESNO,
                    fn: this.promptedSaveHandler,
                    scope : this,
                    icon: Ext.MessageBox.QUESTION
                });
            }
            return 0;
        }
        this.clearCurrent();
        section_button.el.addClass('current');
        if (global_view.center.items.containsKey(section_id)) {
            global_view.center.layout.setActiveItem(section_id);
        }
        else {
            if (section_id === 'st') {
                var stp_doc = new Rack.app.maintcal.serviceTypeStore();
                var stp = new Rack.app.maintcal.serviceTypeAdminView({
                    ds : stp_doc,
                    doc : stp_doc,
                    id : section_id,
                    ct : global_view.center
                });
                stp.addButton('Save',stp.save,stp);
                stp.addButton('Reset',stp.reset,stp);
                var st_task = new Rack.app.maintcal.serviceTypeStore.loadAll(stp,stp_doc);
                // disable calendar navigation for iteration 1.
                st_task.start();
            }
            else {
                global_view.center.createContentManager(section_id,global_doc.calendarData[section_id]);
                global_view.center.layout.setActiveItem(section_id);
                //global_view.generalDataLoad(section_id);
                //var calendarGeneralTab = new Rack.app.maintcal.adminConsole.displayGeneralData(this,this.doc);
                //calendarGeneralTab.start(section_id);
            }
            // set last_action
            Rack.createCookie(this.doc.console_last_action_key,
                section_id.toString(),
                this.doc.cookie_expires,
                this.doc.cookie_path);
        }
    }

});

   
