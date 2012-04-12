// renaissance inline media tag generator

(function($) {
    // apply methods
    $.fn.RenaissanceTagGenerator = function (method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.jModalbox');
        }
    };

    var methods = {
        init : function( options ) {
            var tag_cp_area = '\
                    <div class="form-row media-inlines">\
                    <div><label>Media Inlines</label>\
                        <section id="image_inlines"></section>\
                        <section id="video_inlines"></section>\
                        <section id="audio_inlines"></section>\
                        <section id="document_inlines"></section>\
                        <section id="object_inlines"></section>\
                        <section id="external_inlines"></section>\
                    </div></div>';
            jQuery("div.form-row.field-body:first").before(tag_cp_area);

            return this.each(function(){
                var $this = $(this);
                var data = $this.data('keys');

                if (!data)
                {
                    $this.data('keys',[]);
                }

                $this.on('change.rtg keyup.rtg', methods.update_tags);
            });
        },
        update_tags : function(e) {
            var input = $(this);

            var inline_type = input.attr("name");
            var inline_name = inline_type.split("_")[0];
            var existing_keys = input.data("keys");
            var entered_keys = input.val().split(",");

            jQuery.each(entered_keys, function(key, value){
                if (jQuery.inArray(value, existing_keys) == -1 && value != "")
                {
                    existing_keys.push(value);
                    jQuery("section#"+inline_type).append('{% inline '+inline_name+' '+value+' %}');
                }
            });
            console.log(existing_keys,entered_keys);
        }
    };

})(jQuery);