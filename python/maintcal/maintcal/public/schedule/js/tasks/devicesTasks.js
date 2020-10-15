/**
*   Three load tasks.
*/

Rack.app.maintcal.devices.load = function (model) {
    
    // Takes an optional second argument stating if we should bring
    // in the managed_storage devices
    this.start = function (device_numbers) {
        // create the device url.
        var base_string = '/maintcal/devices/shows.json';
        var these_params = {numbers: device_numbers}; 
        var success_handler = model.handleLoadResponse;
        if (arguments.length > 1 ) {
            these_params['has_managed_storage'] = arguments[1];
        }
        model.connection.request({
                url: base_string,
                success: success_handler,
                failure: model.handleLoadError,
                scope: model,
                params: these_params 
            });
    };
};

Rack.app.maintcal.devices.loadAll = function(model) {

    this.start = function(acct) {
        model.connection.request({
            url: '/maintcal/devices.json?account=' + acct,
            success: model.handleLoadResponse,
            failure: model.handleLoadError,
            scope: model
        });
    };
};

Rack.app.maintcal.devices.pagedLoad = function(model) {


    this.start = function (acct,page,limit) {

        model.connection.request({
            url: '/maintcal/devices.json?account=' + acct + 
                '&page=' + page + '&limit=' + limit, 
            success: model.handlePagedResponse,
            failure: model.handleLoadError,
            scope: model
        });

    };
};

