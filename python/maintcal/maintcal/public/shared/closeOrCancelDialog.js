Ext.namespace('Rack.app.maintcal.cancelOrCloseDialog');

Rack.app.maintcal.cancelOrCloseDialog = function () {

    this.addEvents({
        closingclicked : true
    });

    this.contextRE = /service|maintenance/i;
    
    this.dialogLabel = new Rack.app.maintcal.Label();

    this.completeServiceSelected = function(combo, value) {
        var oldCmb = Ext.getCmp('successFulWithIssues');
        if(oldCmb) {
            this.formPanel.remove(oldCmb);
        }
        var oldCmb = Ext.getCmp('cancelReason');
        if(oldCmb) {
            this.formPanel.remove(oldCmb);
        }
        var oldCmb = Ext.getCmp('unsuccessfulReasons');
        if(oldCmb) {
            this.formPanel.remove(oldCmb);
        }
        var oldCmb = Ext.getCmp('legend');
        if(oldCmb) {
            this.formPanel.remove(oldCmb);
        }
        var checkList = [
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Incorrect Time or Date',
                            name: 'incorrect_time_or_date'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Late Start',
                            name: 'late_start'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'No QC',
                            name : 'no_qc'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Poor Execution',
                            name: 'poor_execution'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Poor Prep',
                            name: 'poop_prep'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Substandard QC',
                            name: 'standard_qc'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Template Not Used',
                            name: 'template_not_used'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Time Exceeded',
                            name: 'time_exceeded'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Unexpected Results',
                            name: 'UnExpected Results'
                        },
                        {
                            fieldLabel: '',
                            labelSeparator: '',
                            boxLabel: 'Other',
                            name: 'others'
                        },
                        {
                            xtype: 'textarea',
                            fieldLabel: 'Feedback',
                            anchor: '100%',
                            name: 'feedback'
                        }
                        ];
        if(value.data['id'] == 2) {
            var checkboxes = {
                xtype: 'fieldset',
                title: 'Select All That Apply',
                id: 'unsuccessfulReasons',
                autoHeight: true,
                defaultType: 'checkbox',
                items:  checkList
            };            
            var legend = {
                xtype: '',
                id: 'legend',
                html: '<b><i>The maintenance objective(s) were not met</i></b>'
            };
            this.formPanel.add(legend);
            this.formPanel.add(checkboxes);
            this.formPanel.doLayout();
        }
        else if(value.data['id'] == 1) {
            var legend = {
                xtype: '',
                id: 'legend',
                html: '<b><i>The maintenanace objective(s) were met</i></b>'
            };
            this.formPanel.add(legend);
            this.formPanel.doLayout();
        }
        else if(value.data['id'] == 3) {
            var checkboxes = {
                xtype: 'fieldset',
                title: 'Select All That Apply',
                id: 'successFulWithIssues',
                autoHeight: true,
                defaultType: 'checkbox',
                items:  checkList
            };
            var legend = {
                xtype: '',
                id: 'legend',
                html: '<b><i>The maintenance objective(s) were met but issues were encountered</i></b>'
            };
            this.formPanel.add(legend);
            this.formPanel.add(checkboxes);
            //this.formPanel.getComponent('unsuccessful').on('select',this.unSuccessfulSelected,this);
            this.formPanel.doLayout();
        }
        else if(value.data['id'] == 4) {
            var cancelReason = {
                xtype: 'fieldset',
                title: 'Select All That Apply',
                id: 'cancelReason',
                autoHeight: true,
                defaultType: 'checkbox', // each item will be a checkbox
                items: [
                {
                    fieldLabel: '',
                    labelSeparator: '',
                    boxLabel: 'Customer Request',
                    name: 'customer_request'
                },
                {
                    fieldLabel: '',
                    labelSeparator: '',
                    boxLabel: 'Incorrect Date Or Time',
                    name: 'incorrect_date_or_time'
                },
                {
                    fieldLabel: '',
                    labelSeparator: '',
                    boxLabel: 'Other',
                    name: 'others'
                },
                {
                    xtype: 'textarea',
                    fieldLabel: 'Feedback',
                    anchor: '100%',
                    name: 'feedback'
                }
                ]
            };
            var legend = {
                xtype: '',
                id: 'legend',
                html: '<b><i>The maintenance will not be performed or will be rescheduled</i></b>'
            };
            this.formPanel.add(legend);
            this.formPanel.add(cancelReason);
            this.formPanel.doLayout();
        }
    }
    
    this.formPanel = new Ext.FormPanel({
        labelWidth: 125, // label settings here cascade unless overridden
        frame:true,
        title: '',
        bodyStyle:'padding:5px 5px 0',
        width: 450,
        items: [{
            xtype: 'combo',
            id: 'completeService',
            fieldLabel: 'Complete/Cancel Service',
            hiddenName: 'closingResult',
            emptyText: 'Select Result',
            store:
            new Ext.data.SimpleStore({
                fields: ['id','closingReason'],
                data: [
                [1,"Successful"], 
                [3,"Successful With Issues"],
                [2,"Failed"],
                [4,"Cancelled"],
                ]
            }), 
            displayField: 'closingReason',
            valueField: 'id',
            selectOnFocus: true,
            mode: 'local',
            typeAhead: true,
            editable: false,
            triggerAction: 'all',
        }] 
    });
    this.formPanel.getComponent('completeService').on('select',this.completeServiceSelected,this);

    var config = {
        width: 470,
        autoScroll: false,
        draggable: true,
        resizable: false,
        shadow: true,
        closeAction: 'close',
        title: 'closing',
        plain: true,
        x: 235,
        y:50,
        //frame: true,
        modal: true,
        defaultButton: 0,
        buttons: [{
            text: 'Save',
            handler: this.closing,
            scope: this
        }, {
            text: 'Exit',
            handler: this.cancel,
            scope: this
        }],
        items: [
            this.dialogLabel,
            this.formPanel
        ]
    };

    Ext.Window.call(this, config);

};

Ext.extend(Rack.app.maintcal.cancelOrCloseDialog, Ext.Window, {

    makeDialogText: function(val) {

        var val = val.toLowerCase();

        var msg =  "You are permanently completing/cancelling this " + val + "." + 
            " Please enter the reason for the close below:"; 

        this.dialogLabel.setText(msg);

    },

    show : function(b ,e) {
        this.getContext(b,e);
        this.makeDialogText(this.context);
        this.setTitle("Completing/Cancelling " + this.context);
        Rack.app.maintcal.cancelOrCloseDialog.superclass.show.call(this); 
    },

    getContext : function(b,e) {
        var result = "maintenance or service";
        if ( b instanceof Ext.Button ) {
            if ( typeof b.getText === "function" ) {
                var context_result = b.getText().match(this.contextRE);
                if (context_result) {
                    this.context = context_result[0];
                }
                else {
                    throw "Called from an invalid context";
                }   
            }
            else {
                throw "b has no function getText";
            } 
        }
        else {
            throw "b is not an instance of Ext.Button";
        }
    },

    getCancelOrClosingReason : function () {
        return this.formPanel;
    },

    closing : function () {
        this.fireEvent('closingclicked',this);
    },

    cancel : function () {
        this.hide();
        Rack.app.maintcal.cancelOrCloseDialog.superclass.close.call(this);    
    }

});

