/**
*   This class represents a dialog to display customer contact information.
*/
Ext.namespace('Rack.app.maintcal.contactCustomerDialog');

Rack.app.maintcal.contactCustomerDialog = function (parent_view, before_or_after_text, connection, maintenance_id, reasons, unsuccessful, feedback) {

    this.parent_view            = parent_view;
    this.before_or_after_text   = before_or_after_text;
    this.connection             = connection;
    this.maintenance_id         = maintenance_id;
    this.reasons                = reasons;
    this.unsuccessful           = unsuccessful;
    this.feedback               = feedback;

    this.addEvents({
        cancelclicked : true
    });

    this.contactInfo = {};

    this.dialogLabel = new Rack.app.maintcal.Label();

    this.closeButton = new Ext.Button({
            id: 'notify_close',
            text: 'I have contacted the Customer',
            handler: this.close,
            scope: this
        });

    this.cancelButton = new Ext.Button({
            id: 'notify_cancel',
            text: 'I have NOT contacted the Customer',
            handler: this.cancel,
            scope: this
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
        buttons: [
            this.closeButton,
            this.cancelButton 
        ],
        items: [
            this.dialogLabel
        ]
    };
    
    Ext.Window.call(this, config);
};

Ext.extend(Rack.app.maintcal.contactCustomerDialog, Ext.Window, {

    setContactInfo: function(info) {
        this.contactInfo = info;
    },

    makeDialogText: function() {
        var msg =  "Please contact the Customer using the following information:<br /><br />" +
            "<table cellpadding=\"15px\" cellspacing=\"0\" width=\"99%\" " +
            " style=\"padding: 15px !important;\" " +
            "><tr><th>Name: </th><td>" +
            this.contactInfo['customer_name'] + 
            "</td></tr><tr><th>Contact Information: </th><td>" + 
            this.contactInfo['customer_info'] + "</td></tr>" +
            "<tr><th colspan=\"2\">How was customer contacted? </th></tr>" +
            "<tr><th colspan=\"2\">Please indicate who you contacted and how you contacted them.</th></tr>" +
            "<tr><td colspan=\"2\">" +
            "<input id=\"after_log_text\" name=\"after_log_text\" size=\"40\" maxlength=\"200\" value=\"\" /></td></tr>" +
            "</table><br/><br/>";

        this.dialogLabel.setText(msg);
    },

    show: function(b ,e) {
        this.makeDialogText();
        this.setTitle("Contact Customer " + this.before_or_after_text + " Maintenance");
        Rack.app.maintcal.contactCustomerDialog.superclass.show.call(this); 
    },

    cancel: function () {
        this.hide();
        this.destroy();
    },

    close: function () {
        var textBox = document.getElementById('after_log_text');
        if (textBox.value == "") {
            alert("You must record how you have contacted the customer in order to proceed.");
            textBox.focus();
            return;
        }

        textBox.disabled = true;
        this.closeButton.disable();
        this.cancelButton.disable();

        var requestConfig = {
            url: '/maintcal/maintenances/set_notify_customer_after_log/' + this.maintenance_id,
            method: 'POST',
            success: this.closeResponseHandler,
            failure: this.closeResponseHandler,
            scope: this
        };

        requestConfig.params = {notify_customer_after_log: textBox.value};

        this.connection.request(requestConfig);
    },

    closeResponseHandler: function () {
        this.parent_view.runCompleteServiceTask(this.reasons, this.unsuccessful, this.feedback);
        this.hide();
        this.destroy();
    }
});

