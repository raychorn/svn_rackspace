/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.adminConsole.Content');

Rack.app.maintcal.adminConsole.Content = function(runtime_config) {

    var config = Ext.apply(runtime_config, {
        region : 'center',
        header : false,
        layout : 'card',
        bodyStyle : 'background-color: transparent'
    });

    Ext.Panel.call(this, config);
    //this.on('render', this.makeGeneralTab, this);
    this.makeGeneralTab(config.generalData);

};

Ext.extend(Rack.app.maintcal.adminConsole.Content, Ext.Panel, {

    /*initComponent : function() {
        Ext.Panel.initComponent.call(this);
        this.makeGeneralTab(this.generalData);
    }, */

    makeGeneralTab : function() {
        var detail_data = this.generalData;
        var task_section = new Rack.app.maintcal.generalTab({
            id : 'general_tab_' + detail_data.id,
            name: detail_data.name + ' Calendar Configuration',
            data : detail_data
            //activeItem : 'general_tab_' + detail_data.id
        });
        task_section.addButton({
            text : 'Save',
            disabled : !detail_data.is_admin,
            handler : task_section.save,
            scope : task_section
        });
        task_section.addButton({
            text : 'Revert',
            disabled : !detail_data.is_admin,
            handler : task_section.revert,
            scope : task_section
        });
        this.add(task_section);
        //this.doLayout();
   }

});
