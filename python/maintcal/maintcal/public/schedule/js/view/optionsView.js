/*extern Ext, Rack */

Rack.app.maintcal.optionsView = function (model) {

    this.addEvents({
        optionschange : true
    });

    this.doc = model;

    this.expediteWarning = "You must have prior approval to select " +
        "the Expedite option and include the approvers name in " +
        "the Specific Notes for each calendar. Please make sure you " +
        "have contacted the associated groups for approval and to " +
        "confirm available resources. Failure to include the approver " +
        "will result in the maintenance being cancelled. By selecting " +
        "the Expedite option all lead times will be disregarded.";
    this.expediteHasFired = false;
    this.expediteCheckBox = new Ext.form.Checkbox({
        id: 'expediteCheckBox_id',
        labelSeparator: '',
        itemCls: 'mc-SVSO-chkbox'
    });
    this.expedite = new Ext.form.FieldSet({
        title: 'Expedite',
        collapsible: false,
        height: 35,
        items: this.expediteCheckBox
    });
    this.extendTimesCombo = new Ext.form.ComboBox({
        id: 'extendTimesComboBox_id',
        store: this.doc,
        mode: 'local',
        width: 100,
        hideLabel: true,
        listWidth: 100,
        displayField: 'name',
        valueField: 'value',
        triggerAction: 'all',
        forceSelection: true,
        editable: false
    });
    this.extendTimes = new Ext.form.FieldSet({
        title: 'Extend Length of Maintenance',
        collapsible: false,
        height: 45,
        items: this.extendTimesCombo
    });

    var config = {
        title: 'Scheduling Options',
        animCollapse: false,
        frame: true,
        listeners:{
            afterlayout: function(c) {
                c.tools.toggle.dom.qtip= 'Click to Expand/Collapse Scheduling Options'
            }
        },
        items: [
            this.expedite,
            this.extendTimes
        ]
    };

    Ext.form.FormPanel.call(this, config);

    this.addEvents({
        expedite: true,
        extend: true
    });
    this.expediteCheckBox.on('check', this.expediteNagMessage, this);
    this.expediteCheckBox.on('change', this.handleOptionsChange, this);
    this.extendTimesCombo.on('change', this.handleOptionsChange, this);
};

Ext.extend(Rack.app.maintcal.optionsView, Ext.form.FormPanel, {
    
    expediteNagMessage : function () {
        if (!this.expediteHasFired) {
            Ext.MessageBox.alert('ALERT', this.expediteWarning);
            this.expediteHasFired = true;
        }
    },

    handleOptionsChange : function () {
        this.fireEvent('optionschange');
    }      
    
});
  



