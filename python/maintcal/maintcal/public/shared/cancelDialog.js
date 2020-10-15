Ext.namespace('Rack.app.maintcal.cancelDialog');

Rack.app.maintcal.cancelDialog = function () {

    this.addEvents({
        cancelclicked : true
    });

    this.contextRE = /service|maintenance/i;
    
    this.dialogLabel = new Rack.app.maintcal.Label();
        
    this.cancelReason = new Ext.form.TextArea({
        allowBlank: false,
        tabIndex: 1,
        width: 400,
        height: 80,
        hideLabel: true
    });

    var config = {
        width: 420,
        autoScroll: false,
        draggable: false,
        resizable: false,
        shadow: true,
        closeAction: 'close',
        title: 'Cancel',
        plain: true,
        frame: true,
        modal: true,
        defaultButton: 0,
        buttons: [{
            text: 'Yes',
            handler: this.cancel,
            scope: this
        }, {
            text: 'No',
            handler: this.close,
            scope: this
        }],
        items: [
            this.dialogLabel,
            this.cancelReason
        ]
    };

    Ext.Window.call(this, config);

};

Ext.extend(Rack.app.maintcal.cancelDialog, Ext.Window, {

    makeDialogText: function(val) {

        var val = val.toLowerCase();

        var msg =  "You are permanently canceling this " + val + "." + 
            " Please enter the reason for the cancellation below:"; 

        this.dialogLabel.setText(msg);

    },

    show : function(b ,e) {
        this.getContext(b,e);
        this.makeDialogText(this.context);
        this.setTitle("Cancel " + this.context + " - Enter a Reason");
        Rack.app.maintcal.cancelDialog.superclass.show.call(this); 
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

    getCancelReason : function () {
        return this.cancelReason.getRawValue();
    },

    cancel : function () {
        if (this.cancelReason.isValid()) {
            this.fireEvent('cancelclicked',this);
        }
    },

    close : function () {
        this.cancelReason.reset();
        this.hide();
        //Rack.app.maintcal.cancelDialog.superclass.close.call(this);    
    }

});

