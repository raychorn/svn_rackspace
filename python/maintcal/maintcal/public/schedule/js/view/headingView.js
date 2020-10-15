/*extern Ext, Rack */

Ext.namespace('Rack.app.maintcal');

Rack.app.maintcal.headingView = function (config) {
    
    this.pageTitle = new Rack.app.maintcal.Label({
        cls: 'mcSV-title-flush-left'
    });
    this.clock = new Rack.app.maintcal.clock({
        cls: 'mcSV-title-flush-left'
    });
    this.updateAvailableButton = new Ext.Button({
        text: 'Update Available Times',
        tooltip: 'Click to calculate Available Maintenance Times'
    });
    this.tzChangeButton = new Rack.app.maintcal.Label({
        tag: 'button',
        html : 'Change TZ',
        cls: 'mc-tz-change-button-schedule'
    });
    this.ticketNumber = new Rack.app.maintcal.Label({
        cls: 'mcSV-ticket-title'
    });
    this.accountInfo = new Rack.app.maintcal.Label({
        cls: 'mcSV-account-title'
    });

    config = config || {};
    Ext.apply(config, {
        items: [
            this.pageTitle,
            this.clock,
            this.tzChangeButton,
            this.updateAvailableButton,
            this.ticketNumber,
            this.accountInfo
        ]
    });

    Ext.Panel.call(this, config);
};

Ext.extend(Rack.app.maintcal.headingView, Ext.Panel);

