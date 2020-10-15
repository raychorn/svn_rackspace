/*extern Ext, Rack */

// demo only method
/*
Rack.app.maintcal.serviceTypeStore.loadDemo = function(view,doc){
    
    this.start = function(){
        doc.handleDemoResponse(st_response_obj);
    }
};
*/

Rack.app.maintcal.serviceTypeStore.loadAll = function(view,doc){
    this.start = function(){
        view.maskThis('Loading ...');
        doc.connection.request({
                url: '/maintcal/servicetypes.json?admin=true',
                timeout: 300000,
                success: doc.handleLoadResponse,
                failure: doc.handleLoadError,
                scope:doc
            });
    };
};

Rack.app.maintcal.serviceTypeStore.update = function(view,doc){
     this.start = function(){
        view.maskThis('Saving Data ... Please wait');
        var modifieds = doc.getModifiedRecords();
        // update this doc variable to ensure that the view gets unmasked
        // when all updates are confirmed.
        doc.currentUpdateCount = modifieds.length;
        var m;
        for(m=0;m<modifieds.length;m++){
            var request_url;
            var view_params;
            var success_method;
            var failure_method;
            // assumes a new service type and create should be called instead.
            if (!modifieds[m].json) {
                request_url = '/maintcal/servicetypes/create';
                view_params = modifieds[m].data;
                view_params.uiid = modifieds[m].id;
            } else {
                request_url = '/maintcal/servicetypes/update/' + 
                    modifieds[m].json.id;
                view_params = modifieds[m].getChanges();
            }
            doc.connection.request({
                url: request_url,
                method:'POST',
                success: doc.handleUpdateSuccess,
                failure: doc.handleUpdateFailure,
                scope:doc,
                params:view_params
            });
        }
    };

    this.confirmCreate = function(rid,uiid){
        // replace the client side id with the server side one, before
        // doing the confirm
        var idx = doc.find('id',uiid);
        if(idx != -1) {
            var modifiedRecord = doc.getAt(idx);
            modifiedRecord.set('id',rid);
            doc.connection.request({
                url: '/maintcal/servicetypes/' + rid + '.json',
                success: doc.handleConfirmResponse,
                failure: doc.handleConfirmFailure,
                scope:doc
            });
        } else {
            doc.handleConfirmFailure();
        }
    };

    this.confirmUpdate = function(rid){
        doc.connection.request({
            url: '/maintcal/servicetypes/' + rid + '.json',
            success: doc.handleConfirmResponse,
            failure: doc.handleConfirmFailure,
            scope:doc
        });
    };
};

Rack.app.maintcal.serviceTypeStore.reset = function(view,doc){
    this.start = function(){
        doc.each(function(r) {
            if(r.json && r.dirty) {
                r.reject();
            }
            if(!r.json){
                doc.remove(r);
            }
        });
        var the_view = view.getView();
        the_view.refresh();
    };
};

