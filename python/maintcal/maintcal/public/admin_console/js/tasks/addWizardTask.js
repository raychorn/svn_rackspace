/*extern Ext, Rack */


Ext.namespace('Rack.app.maintcal.createAddWizard');

Rack.app.maintcal.createAddWizard = function (view,doc) {
    this.start = function () {
        // comment out real code for demo
        /*var base_string = '/maintcal/devices/shows.json';
        var these_params = {numbers: device_numbers}; 
        doc.connection.request({
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleLoadError,
            scope: this,
            params: these_params 
        });
        */
        this.demoLoad();
    };

    this.maskView = function (this_view) {
        if (this_view.isVisible && this_view.mask) {
            this_view.mask('Loading ... ');
        }
    };

    this.unmaskView = function (this_view) {
        if ( this_view.mask && this_view.isMasked() ){
            this_view.unmask();
        }
    };

    this.demoLoad = function () {
        // fake a load from the server
        //window.setTimeout(function(){return},2000);
        this.handleLoadResponse();
    };

    this.handleLoadResponse = function () {
        // demo only.
        /*var i;
        for (i=0;i<calendar_steps.length;i++) {
            view.addStep(calendar_steps[i]);
        }
        */
        return 0;
    };

    this.handleDataError = function (r, o) {
        view.fireEvent('dataerror', r, o);
    };
};

Rack.app.maintcal.createCategoryWizard = function (view,doc) {
    
    this.start = function () {
        // comment out real code for demo
        /*var base_string = '/maintcal/devices/shows.json';
        var these_params = {numbers: device_numbers}; 
        doc.connection.request({
            url: base_string,
            success: this.handleLoadResponse,
            failure: this.handleLoadError,
            scope: this,
            params: these_params 
        });
        */
        this.demoLoad();
    };

    this.maskView = function (this_view) {
        if (this_view.isVisible && this_view.mask) {
            this_view.mask('Loading ... ');
        }

    };

    this.unmaskView = function (this_view) {
        if ( this_view.mask && this_view.isMasked() ){
            this_view.unmask();
        }
    };

    this.demoLoad = function () {
        // fake a load from the server
        //window.setTimeout(function(){return},2000);
        this.handleLoadResponse();
    };

    this.handleLoadResponse = function () {
        // demo only.
        /*
        var i;
        for (i=0;i<category_steps.length;i++) {
            view.addStep(category_steps[i]);
        }
        */
        return 0;
    };

    this.handleDataError = function (r, o) {
        view.fireEvent('dataerror', r, o);
    };
};
