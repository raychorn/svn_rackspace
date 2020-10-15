/* Ext patches to bugs */
/* We believe that this patches a problem with the original Ext.layout.ColumnLayout
    that put this.renderAll call outside the check for this.innerCt.
*/

Ext.override(Ext.layout.ColumnLayout, {

    onLayout : function(ct, target){
        Ext.layout.ColumnLayout.superclass.onLayout.call(this, ct, target);

        var cs = ct.items.items, len = cs.length, c, i;

        if(!this.innerCt){
            target.addClass('x-column-layout-ct');

            
            
            this.innerCt = target.createChild({cls:'x-column-inner'});

            this.renderAll(ct, this.innerCt);

            this.innerCt.createChild({cls:'x-clear'});

        }

        var size = target.getViewSize();

        if(size.width < 1 && size.height < 1){ 
            return;
        }

        var w = size.width - target.getPadding('lr') - this.scrollOffset,
            h = size.height - target.getPadding('tb'),
            pw = w;

        this.innerCt.setWidth(w);
        
        
        

        for(i = 0; i < len; i++){
            c = cs[i];
            if(!c.columnWidth){
                pw -= (c.getSize().width + c.getEl().getMargins('lr'));
            }
        }

        pw = pw < 0 ? 0 : pw;

        for(i = 0; i < len; i++){
            c = cs[i];
            if(c.columnWidth){
                c.setSize(Math.floor(c.columnWidth*pw) - c.getEl().getMargins('lr'));
            }
        }
    }
    
    
});

// override default Ext masking behavior to give masks correct z-indexes.
Ext.override(Ext.Element,{
    mask : function(msg, msgCls, zLayer){
        if(this.getStyle("position") == "static"){
            this.setStyle("position", "relative");
        }
        if (this.getStyle("z-index") == "auto" || this.getStyle("z-index") === 0){
            this.setStyle("z-index",1);
        }
        if(this._maskMsg){
            this._maskMsg.remove();
        }
        if(this._mask){
            this._mask.remove();
        }

        this._mask = Ext.DomHelper.append(this.dom, {cls:"ext-el-mask"}, true);
        // pop mask just above the layer of this element unless zLayer is set.
        if (zLayer) {
            var mask_layer = zLayer;
        }
        else {
            var mask_layer = parseInt(this.getStyle("z-index"),10) + 1;
        }
        this._mask.setStyle("z-index",mask_layer.toString());

        this.addClass("x-masked");
        this._mask.setDisplayed(true);
        if(typeof msg == 'string'){
            this._maskMsg = Ext.DomHelper.append(this.dom, {cls:"ext-el-mask-msg", cn:{tag:'div'}}, true);
            var mm = this._maskMsg;
            // pop the mask message just above the mask
            var mask_msg_layer = parseInt(this._mask.getStyle("z-index"),10) + 1;
            mm.setStyle("z-index",mask_msg_layer.toString());
            mm.dom.className = msgCls ? "ext-el-mask-msg " + msgCls : "ext-el-mask-msg";
            mm.dom.firstChild.innerHTML = msg;
            mm.setDisplayed(true);
            mm.center(this);
        }
        if(Ext.isIE && !(Ext.isIE7 && Ext.isStrict) && this.getStyle('height') == 'auto'){ // ie will not expand full height automatically
            this._mask.setSize(this.dom.clientWidth, this.getHeight());
        }
        return this._mask;
    }
});



// add a convienience method of getSelectedRecord to an Ext.form.ComboBox
Ext.override(Ext.form.ComboBox,{
    getSelectedRecord : function() {
        var index = this.view.getSelectedIndexes()[0];
        return this.store.getAt(index);
    }
});


