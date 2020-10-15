Ext.namespace('Rack.app.maintcal.configWizard');
Ext.namespace('Rack.app.maintcal.wizardStep');

Rack.app.maintcal.wizardStep = Ext.extend(Ext.Panel , {

    step : '',

    header : false,

    bodyStyle : 'background-color: transparent',

    initComponent : function() {
        Rack.app.maintcal.wizardStep.superclass.initComponent.call(this);
        this.addEvents({
            bodyupdate: true,
            wizardback: true,
            wizardfwd: true
        });
        this.id = this.makeId();
        this.html = this.draw();
        this.on('bodyupdate',this.loadEditables,this);
        //this.on('beforerender',this.draw,this);
    },

    makeId : function() {
        return 'mc-wiz-step-' + this.step;
    },

    draw : function() {

        if (this.isTerminal) {
            var outs = [
            '<div class="mc-wiz-heading">',
                '<div class="mc-wiz-step-label">',
                this.step,'</div><h1>', this.title,
                '</h1>','<div class="mc-wiz-desc">',
                this.description,'</div></div>',
                '<div id="mc-wiz-main-id-' + this.step 
                + '" class="mc-wiz-main"> </div>'];
        }
        else {

            var outs = [
            '<div class="mc-wiz-heading">',
                '<div class="mc-wiz-step-label">',
                this.step,'</div><h1>', this.title,
                '</h1>','<div class="mc-wiz-desc">',
                this.description,'</div></div>',
                '<div id="mc-wiz-main-id-' + this.step 
                + '" class="mc-wiz-main"> </div>',
                '<div class="mc-wiz-footer">',
                /*'<div class="mc-wiz-fwd-icn"> </div>',*/
                '<a title="Next" href="javascript:(function(){return})();"' + 
                ' class="mc-wiz-fwd-icn"> </a>',
                /*'<div class="mc-wiz-back-icn"> </div>',*/
                '<a title="Back" href="javascript:(function(){return})();"' + 
                ' class="mc-wiz-back-icn"> </a></div>'];
        }

        return outs.join('');
        
    },

    loadEditables : function() {
        var mainEl = Ext.get("mc-wiz-main-id-" + this.step);
        // need to create these myself instead of relying on "lazy render",
        // because they need to be available for the 'bodyupdate' event.
        if (this.isTerminal) {
            // short-circut normal step creation and display a 'Done' button.
            var done_button = new Ext.Button({
                text : 'Done',
                handler : this.closeWizard,
                scope : this,
                renderTo : mainEl
            });
            // center the button
            var theButton = mainEl.first();
            theButton.center(mainEl);
            return
        }
        switch(this.editor) {
            case "textfield" :
                this.editorWidget = new Ext.form.TextField({
                    allowBlank : !this.required,
                    cls : 'edit-container',
                    blankText : "This option is required.",
                    value : this.defaultValue ? this.defaultValue : '',
                    editable: false,
                    vtype : this.validator ? this.validator : null,
                    renderTo : mainEl
                });
                this.value = this.editorWidget.getValue;
                break;

            case "boolean" :
                this.editorWidget = new Ext.form.ComboBox({
                    store: new Ext.data.Store({
                        reader : new Ext.data.JsonReader({
                        idProperty: 'id',
                        fields : [
                            {name : 'name', type :'string'},
                            {name : 'id', type : 'int'}
                        ]
                        }),
                    data : [{name:'Yes',id:'1'},{name:'No',id:'0'}] 
                    }),
                    mode: 'local',
                    allowBlank : !this.required,
                    cls : 'edit-container',
                    displayField: 'name',
                    valueField: 'id',
                    //listWidth: 200,
                    triggerAction: 'all',
                    forceSelection: true,
                    editable: false,
                    renderTo : mainEl 
                });
                break;

            case "tzpicker" :
                this.editorWidget = new Rack.app.maintcal.pickerWidget({
                    editorType: 'tz',
                    cls : 'edit-container',
                    required : this.required,
                    renderTo : mainEl,
                    dataStruct : tznames
                });
                this.value = this.editorWidget.value
                break;

            case "queuepicker" :
                this.editorWidget = new Rack.app.maintcal.pickerWidget({
                    editorType: 'queue',
                    cls : 'edit-container',
                    required : this.required,
                    renderTo : mainEl,
                    dataStruct : queue_ds
                });
                this.value = this.editorWidget.value
                break;

            case "categorypicker" :
                this.editorWidget = new Rack.app.maintcal.pickerWidget({
                    editorType: 'category',
                    cls : 'edit-container',
                    required : this.required,
                    renderTo : mainEl,
                    dataStruct : categories_demo_ds
                });
                this.value = this.editorWidget.value
                break;

            case "statuspicker" :
                this.editorWidget = new Ext.form.ComboBox({
                    store: new Ext.data.Store({
                        reader : new Ext.data.JsonReader({
                        idProperty: 'id',
                        fields : [
                            {name : 'name', type :'string'},
                            {name : 'id', type : 'int'}
                        ]
                        }),
                    data : demo_status_ds
                    }),
                    mode: 'local',
                    allowBlank : !this.required,
                    cls : 'edit-container',
                    displayField: 'name',
                    valueField: 'id',
                    //listWidth: 200,
                    triggerAction: 'all',
                    forceSelection: true,
                    editable: false,
                    value : 214,
                    renderTo : mainEl 
                });
                break;

            case "ruletype" :
                this.editorWidget = new Ext.form.ComboBox({
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
                    allowBlank : !this.required,
                    cls : 'edit-container',
                    displayField: 'name',
                    valueField: 'id',
                    //listWidth: 200,
                    triggerAction: 'all',
                    forceSelection: true,
                    editable: false,
                    renderTo : mainEl 
                });
                break;

            case "ruleattribute" :
                this.editorWidget = new Ext.form.ComboBox({
                    store: new Ext.data.Store({
                        reader : new Ext.data.JsonReader({
                        idProperty: 'id',
                        fields : [
                            {name : 'name', type :'string'},
                            {name : 'id', type : 'int'}
                        ]
                        }),
                        data : []
                    }),
                    mode: 'local',
                    allowBlank : !this.required,
                    cls : 'edit-container',
                    displayField: 'name',
                    valueField: 'id',
                    //listWidth: 200,
                    triggerAction: 'all',
                    forceSelection: true,
                    editable: false,
                    renderTo : mainEl 
                });
                break;

            case "ruleoperator" :
                this.editorWidget = new Ext.form.ComboBox({
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
                    allowBlank : !this.required,
                    cls : 'edit-container',
                    displayField: 'name',
                    valueField: 'id',
                    //listWidth: 200,
                    triggerAction: 'all',
                    forceSelection: true,
                    editable: false,
                    renderTo : mainEl 
                });
                break;

            case "servicecategory" :
                this.editorWidget = new Ext.form.ComboBox({
                    store: new Ext.data.Store({
                        reader : new Ext.data.JsonReader({
                        idProperty: 'id',
                        fields : [
                            {name : 'name', type :'string'},
                            {name : 'id', type : 'int'}
                        ]
                        }),
                        data : service_cats_only
                    }),
                    mode: 'local',
                    allowBlank : !this.required,
                    cls : 'edit-container',
                    displayField: 'name',
                    valueField: 'id',
                    //listWidth: 200,
                    triggerAction: 'all',
                    forceSelection: true,
                    editable: false,
                    renderTo : mainEl 
                });
                break;
                
                
        }
        // active forward/back buttons
        this.forward_button = this.body.select('a.mc-wiz-fwd-icn',true).first();
        this.forward_button.on('click',this.handleNext,this);
        this.back_button = this.body.select('a.mc-wiz-back-icn',true).first();
        this.back_button.on('click',this.handleBack,this);

        // add validation listeners to enable and disable buttons
        if (this.step === '1') {
            // disable back button\
            this.back_button.setStyle('background-image',
                'url(shared/resources/images/wz_back_bt_disable.gif)');
            this.back_button.un('click',this.handleBack,this);

            //this.back_button.addClass('btn-disabled');
        }
        this.editorWidget.on('valid', this.enableNext,this);
        this.editorWidget.on('invalid', this.disableNext,this);

        // verify and handle any dependent steps
        if ( this.dependency ) {
            this.on('show',this.handleDependentLoad,this);
        }

        // center the editor
        var editContainer = mainEl.first();
        editContainer.center(mainEl);
        
        // run validation
        this.editorWidget.validate();
        this.doLayout();

    },

    handleNext : function() {
        if(this.editorWidget.validate()) {
            this.fireEvent('wizardfwd');
        }
    },

    handleBack : function() {
        // restore the step we are leaving
        if (this.defaultValue) {
            this.editorWidget.setValue(this.defaultValue);
        }
        else {
            this.editorWidget.setValue('');
        }
        this.fireEvent('wizardback');
    },

    enableNext : function() {
        if (this.forward_button.hasClass('btn-disabled')) {
            this.forward_button.removeClass('btn-disabled');
            this.forward_button.setStyle('background-image',
                'url(shared/resources/images/wz_fwd_bt.gif)');
            
        }
    },

    disableNext : function() {
        if (!this.forward_button.hasClass('btn-disabled')) {
            this.forward_button.addClass('btn-disabled');
            this.forward_button.setStyle('background-image',
                'url(shared/resources/images/wz_fwd_bt_disable.gif)');
        }
    },

    getStepDisplayValue : function(step) {
        var ct = this.ownerCt;
        var editRef = ct.items.get(parseInt(step) - 1).editorWidget;
        var type = editRef.constructor.xtype;

        if (type === 'combo') {
            var r = editRef.getSelectedRecord();
            return r.get('name'); 
        }
        else {
            // only other thing is a textfield at this point
            return editRef.getValue();
        }

    },

    handleDependentLoad : function() {
        // implement diffrent loads for each supported wizard option.
        var dependency = this.getStepDisplayValue(this.dependency);
        this.editorWidget.store.loadData(demo_ruleAttribute_ds[dependency]);

    },

    closeWizard : function(sender) {
        this.ownerCt.close(sender);
    },

    // override the default Panel afterRender to be able to fire bodyupdate
    // event. 
    afterRender : function(){
        Rack.app.maintcal.generalTab.superclass.afterRender.call(this);
        this.fireEvent('bodyupdate',this);
    }
});


Rack.app.maintcal.configWizard = Ext.extend(Ext.Window, {

    modal: true,

    draggable : false,

    layout : 'card',

    closable : true,

    resizable: false,

    height: 400,

    width : 600,

    initComponent : function() {
        Rack.app.maintcal.configWizard.superclass.initComponent.call(this);
        this.layout = this.getLayout();
        this.addButton('Cancel',this.close,this);
        this.on('show',this.handleShow,this);
    },

    addStep : function(config) {
        var thisStep = new Rack.app.maintcal.wizardStep(config);
        thisStep.on('wizardfwd',this.showNext,this);
        thisStep.on('wizardback',this.showPrevious,this);
        this.add(thisStep);
    },

    showNext : function() {
        this.layout.setActiveItem(parseInt(this.layout.activeItem.step))
    },

    showPrevious : function(id) {
        this.layout.setActiveItem(parseInt(this.layout.activeItem.step) - 2)
    },

    handleShow : function() {
        // always show the first step
        this.layout.setActiveItem(this.items.get(0).id);
    },

    close : function(sender) {
        if (sender.text && sender.text === 'Done') {
            Rack.app.maintcal.configWizard.superclass.close.call(this);
        }
        else {
            Ext.MessageBox.confirm('Alert !',
            "You are canceling the calendar creation process. Are you sure ?",
            this.closeConfirm,this);
        }
    },

    closeConfirm : function(arg) {
        if(arg === "yes") {
            Rack.app.maintcal.configWizard.superclass.close.call(this);
        }
    },

    insertStep : function(idxBefore,config) {

    }
});
