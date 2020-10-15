/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.selectorRules');
Ext.namespace('Rack.app.maintcal.rule');
Ext.namespace('Rack.app.maintcal.tlRule');
Ext.namespace('Rack.app.maintcal.ruleAttribute');
Ext.namespace('Rack.app.maintcal.ruleModifier');

Rack.app.maintcal.tlRule = Ext.form.ComboBox({

    store: new Ext.data.Store({
        reader : new Ext.data.JsonReader({
            idProperty: 'id',
            fields : [
                {name : 'name', type :'string'},
                {name : 'id', type : 'int'}
            ]
        }),
        data : demo_tlRule_ds
    }),

    mode: 'local',

    displayField: 'name',

    valueField: 'id',

    triggerAction: 'all',

    forceSelection: true,

    editable: false

});

Rack.app.maintcal.ruleAttribute = Ext.extend(Ext.form.ComboBox, {

    store: new Ext.data.Store({
            reader : new Ext.data.JsonReader({
                idProperty: 'id',
                fields : [
                    {name : 'name', type :'string'},
                    {name : 'id', type : 'int'}
                ]
            }),
        }),

    mode: 'local',

    displayField: 'name',

    valueField: 'id',

    triggerAction: 'all',

    forceSelection: true,

    editable: false,

    initComponent : function() {
        Rack.app.maintcal.ruleAttribute.superclass.initComponent.call(this);
        if (this.tlRule) {
            this.store.loadData(demo_ruleAttribute_ds[this.tlRule]);
        }

        this.addEvents({'loadattributes' : true});
    },

    onLoadAttributes : function(tlRuleName) {
        // for real this is where an async call would be made.
        this.store.loadData(demo_ruleAttribute_ds[tlRuleName]);
    }


});

Rack.app.maintcal.ruleModifier = Ext.extend(Ext.form.ComboBox, {

    store: new Ext.data.Store({
        reader : new Ext.data.JsonReader({
            idProperty: 'id',
            fields : [
                {name : 'name', type :'string'},
                {name : 'id', type : 'int'}
            ]
        }),
        data : demo_ruleModifiers
    }),

    mode: 'local',

    displayField: 'name',

    valueField: 'id',

    triggerAction: 'all',

    forceSelection: true,

    editable: false

});

Rack.app.maintcal.selectorRules = Ext.extend(Ext.Panel, {

    layout : 'fit',

    scrollable : true,

    initComponent : function() {
        Rack.app.maintcal.selectorRules.superclass.initComponent.call(this);
        this.addButton({text : 'AND'}, this.handleAND, this);
        this.addButton({text : 'OR'}, this.handleOR, this);
        this.addButton({text : 'NOT'}, this.handleNOT, this);
        this.rules = [];

    },

    handleAND : function() {

        var ANDRule = new Rack.app.maintcal.rule({ title : 'AND'});
        this.rules.push(ANDRule);
        this.add(ANDRule);
        ANDRule.doLayout();
    },

    handleOR : function() {

        var ORRule = new Rack.app.maintcal.rule({ title : 'OR'});
        this.rules.push(ORRule);
        this.add(ORRule);
    },

    handleNOT : function() {
        var NOTRule = new Rack.app.maintcal.rule({ title : 'NOT'});
        this.rules.push(NOTRule);
        this.add(NOTRule);
    }

});

Rack.app.maintcal.rule = Ext.extend(Ext.Panel, {

    layout : 'table',

    autoShow : true,

    layoutConfig : { columns : 4 },

    height : 100,

    bodyStyle : 'margin-top:5;margin-bottom:5',

    initComponent : function() {
        Rack.app.maintcal.rule.superclass.initComponent.call(this);
        var tlLabel = new Rack.app.maintcal.Label({ text : 'Rule Type:'});
        var attrLabel = new Rack.app.maintcal.Label({ text : 'Type Attributes:' });
        var modLabel = new Rack.app.maintcal.Label({ text : 'Modifier:' });
        var valueLabel = new Rack.app.maintcal.Label({ text : 'Value' });
        this.rType = new Rack.app.maintcal.tlRule();

        this.rType.on('select',this.handleTlChange,this);
        this.typeAttrs = new Rack.app.maintcal.ruleAttribute();
        this.modifier = new Rack.app.maintcal.ruleModifier();
        this.value = new Ext.form.TextField();
        this.add(tlLabel);
        this.add(attrLabel);
        this.add(modLabel);
        this.add(valueLabel);
        this.add(this.rType);
        this.add(this.typeAttrs);
        this.add(this.modifier);
        this.add(this.value);
        this.addButton({text : 'AND'}, this.handleAND, this);
        this.addButton({text : 'OR'}, this.handleOR, this);
        this.addButton({text : 'NOT'}, this.handleNOT, this);
    },

    handleTlChange : function(t,r,i) {
        this.typeAttrs.fireEvent('loadattributes',r.get('name'));

    },

    handleAND : function() {

    },

    handleOR : function () {

    },

    handleNOT : function () {

    }

});




