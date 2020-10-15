/*extern Ext, Rack, tznames */

Ext.namespace('Rack.app.maintcal.tzalias');

Rack.app.maintcal.tzalias = function () {
    this.alias_map = {'US/Eastern' : 'America/New_York',
                      'US/Central' : 'America/Chicago',
                      'Texas' : 'America/Chicago',
                      'US/Mountain' : 'America/Denver',
                      'US/Pacific' : 'America/Los_Angeles',
                      'London' : 'Europe/London',
                      'India' : 'Asia/Calcutta',
                      'Western-Europe' : 'Europe/Paris',
                      'Western Australia' : 'Australia/Perth',
                      'Northern Territory' : 'Australia/Darwin',
                      'South Australia' : 'Australia/Adelaide',
                      'Queensland' : 'Australia/Brisbane',
                      'New South Wales' : 'Australia/Sydney',
                      'Victora' : 'Australia/Melbourne',
                      'Tasmania' : 'Australia/Hobart',
                      'Broken Hill' : 'Australia/Broken_Hill',
                      'New Zealand' : 'Pacific/Auckland'
    };

};

Ext.override(Rack.app.maintcal.tzalias,{

    createAliasDisplay : function() {
        // ensure tznames exits.
        if (!tznames){
            return {};
        }
        var display_aliases = {'Zone Aliases' : ['UTC']};
        var alias;
        // ensure that values specificed in this.alias_map exist in tznames.
        for (alias in this.alias_map) {
            var this_alias = this.alias_map[alias].split('/');
            var a;
            for (a = 0; a <= tznames.keys.length; a +=1 ) {
                if (this_alias[0] === tznames.keys[a]) {
                    if (tznames[tznames.keys[a]].indexOf(this_alias[1]) !== -1){
                        // found the aliases value in the map ... add it.
                        display_aliases['Zone Aliases'].push(alias);
                    }
                }
            }
        }
        return display_aliases;
    },
    resolveAlias : function(alias_name) {
        var alias;
        if (alias_name === 'UTC'){
            return 'UTC';
        }
        for (alias in this.alias_map) {
            if (alias_name === alias) {
                return this.alias_map[alias];
            }
        }
        throw "Selected Alias doesn't map back to known aliases";
                
    }
});

