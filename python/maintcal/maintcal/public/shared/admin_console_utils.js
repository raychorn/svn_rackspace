/*extern Ext, Rack */

/* admin console only shared utils */

// make Ext.form.Fields in admin console mark themselves as dirty.

Ext.override(Ext.form.Field,{
    // private
    initEvents : function(){
        this.el.on(Ext.isIE ? "keydown" : "keypress", this.fireKey,  this);
        this.el.on("focus", this.onFocus,  this);
        this.el.on("blur", this.onBlur,  this);
        this.on("change",this.markDirty,this);

        // reference to original value for reset
        this.originalValue = this.getValue();
    },

    markDirty : function() {
        if(this.el.hasClass('mc-mark-dirty') && this.isDirty()) {
            this.el.addClass('mc-text-dirty');
        }
        if(this.el.hasClass('mc-mark-dirty') && 
            this.el.hasClass('mc-text-dirty') && 
            !this.isDirty()) {
            this.el.removeClass('mc-text-dirty');
        }
    },

    // new method to cause fields to reload themselves.
    setOriginalValue : function(val) {
        this.originalValue = val;
        this.setValue(val);
        this.markDirty();
    },

    // adds markDirty call to built-in reset call.
    reset : function() {
        this.setValue(this.originalValue);
        this.clearInvalid();
        this.markDirty();
    }

});

