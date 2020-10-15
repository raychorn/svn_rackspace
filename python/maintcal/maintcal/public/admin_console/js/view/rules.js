/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal.selectorRules');
Ext.namespace('Rack.app.maintcal.rule');
Ext.namespace('Rack.app.maintcal.tlRule');
Ext.namespace('Rack.app.maintcal.ruleAttribute');
Ext.namespace('Rack.app.maintcal.ruleModifier');

Rack.app.maintcal.tlRule = Ext.extend(Ext.form.ComboBox,{

    store: new Ext.data.Store({
        reader : new Ext.data.JsonReader({
            idProperty: 'id',
            fields : [
                {name : 'name', type :'string'},
                {name : 'id', type : 'int'}
            ]
        }),
        //data : demo_tlRule_ds
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

    emptyText : 'Select a Rule Type',

    initComponent : function() {
        Rack.app.maintcal.ruleAttribute.superclass.initComponent.call(this);
        if (this.tlRule) {
            this.store.loadData(demo_ruleAttribute_ds[this.tlRule]);
        }

        this.addEvents({'loadattributes' : true});
        this.on('loadattributes',this.onLoadAttributes,this);
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
        //data : demo_ruleModifiers
    }),

    mode: 'local',

    displayField: 'name',

    valueField: 'id',

    triggerAction: 'all',

    forceSelection: true,

    editable: false,

    width : 50

});

Rack.app.maintcal.selectorRules = Ext.extend(Ext.Panel, {

    autoScroll : true,

    bodyStyle : 'background-color: transparent',

    initComponent : function() {
        Rack.app.maintcal.selectorRules.superclass.initComponent.call(this);
        this.addButton({text : 'AND'}, this.handleAddRule, this);
        this.addButton({text : 'OR'}, this.handleAddRule, this);
        this.addButton({text : 'NOT'}, this.handleAddRule, this);
    },

    handleAddRule: function(btRef) {
        var thisRule = new Rack.app.maintcal.rule({ 
            title : btRef.text + ' Rule',
            ruleType : 'tlRule',
            height: 100 });

        thisRule.on('removeme',this.removeRule,this);
        thisRule.on('addsub', this.handleAddCondition,this);
        this.add(thisRule);
        this.doLayout();
    },

    handleAddCondition : function(conditionName,panelRef) {
        var thisRule = new Rack.app.maintcal.rule({ 
            title : conditionName + ' Condition',
            ruleType : 'condition',
            parentRule : panelRef,
            height: 100 });
        // add the condition to its parent rule conditions collection, so
        // removing a rule will remove its conditions. Also create conditions
        // below other conditions.
        if(panelRef.conditions.getCount() !== 0) {
            var siblingRuleIdx = this.items.indexOf(panelRef.conditions.last());
        }
        else {
            var siblingRuleIdx = this.items.indexOf(panelRef);
        }
        thisRule.on('removeme',this.removeRule,this);
        panelRef.conditions.add(thisRule);
        this.insert(siblingRuleIdx + 1,thisRule);
        this.doLayout();
    },

    removeRule : function(ruleRef) {
        // remove all conditions if a rule is removed.
        if (ruleRef.conditions && ruleRef.conditions.getCount() !== 0) {
            ruleRef.conditions.each(function(i) {
                this.remove(i,true);
            },this);
        }
        // remove the condition from the parent rule if it is present.
        if (ruleRef.parentRule) {
            ruleRef.parentRule.conditions.remove(ruleRef);
        }
        this.remove(ruleRef,true);
    }

});

Rack.app.maintcal.rule = function (config) {

    var tlLabel = new Rack.app.maintcal.Label({ html : 'Rule Type:',
                                                cls : 'mc-rule-label'});
    var attrLabel = new Rack.app.maintcal.Label({ html : 'Type Attributes:',
                                                cls : 'mc-rule-label'});
    var modLabel = new Rack.app.maintcal.Label({ html : 'Modifier:',
                                                cls : 'mc-rule-label'});
    var valueLabel = new Rack.app.maintcal.Label({ html : 'Value',
                                                cls : 'mc-rule-label'});
    this.rType = new Rack.app.maintcal.tlRule();
    this.typeAttrs = new Rack.app.maintcal.ruleAttribute();
    this.modifier = new Rack.app.maintcal.ruleModifier();
    this.value = new Ext.form.TextField();

    if (config.ruleType === 'condition') {
        
        var ruleWidth = 570;
        var buttonBar =  ['->',{text : 'Remove this rule',
                                handler : this.handleRemove,
                                scope : this
                                }];

    }
    else {
        var ruleWidth = 625;

        var buttonBar = ['->',
            {
                text : 'Add "AND" Condition',
                handler : this.handleSub,
                scope : this
            },'-',{
                text : 'Add "OR" Condition',
                handler : this.handleSub,
                scope : this
            },'-',{
                text : 'Add "NOT" Condition',
                handler : this.handleSub,
                scope : this
            },'-',{
                text : 'Remove this rule',
                handler : this.handleRemove,
                scope : this
            }];
        this.conditions = new Ext.util.MixedCollection(false); 
    }

    config = config || {};

    Ext.apply(config, {
        layout : 'table',
        layoutConfig : { columns : 4 },
        bodyStyle : 'background-color: transparent',
        cls : 'mc-tl-rule',
        width : ruleWidth,
        bbar : buttonBar,
        items : [
            tlLabel,
            attrLabel,
            modLabel,
            valueLabel,
            this.rType,
            this.typeAttrs,
            this.modifier,
            this.value
        ]});
    this.rType.on('select',this.handleTlChange,this);
    this.addEvents({'removeme' : true,
                    'addsub' : true
                    });
    Ext.Panel.call(this,config);

};

Ext.extend(Rack.app.maintcal.rule,Ext.Panel, {

    handleTlChange : function(t,r,i) {
        this.typeAttrs.fireEvent('loadattributes',r.get('name'));

    },

    handleSub : function(btRef) {
        var conditionName = /AND|OR|NOT/.exec(btRef.text);
        this.fireEvent('addsub',conditionName,this);
    },

    handleRemove : function() {
        this.fireEvent('removeme',this);
    }

});




