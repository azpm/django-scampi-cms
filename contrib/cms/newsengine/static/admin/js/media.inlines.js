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

    var settings = {
        helper_url: "",
        uiMethod: "fadeIn"
    };

    var methods = {
        init : function( options ) {
            if (options)
            {
                jQuery.extend(settings, options);
            }

            var tag_cp_area = '\
                    <fieldset class="module aligned">\
                    <h2>Generated Inline Helpers</h2>\
                        <table style="border: 1px solid #eee; width: 100%">\
                            <thead><tr>\
                                <th>Images</th>\
                                <th>Videos</th>\
                                <th>Audio</th>\
                                <th>Documents</th>\
                                <th>Objects</th>\
                                <th>Widgets</th>\
                            </tr></thead>\
                            <tr>\
                                <td id="image_inlines"></td>\
                                <td id="video_inlines"></td>\
                                <td id="audio_inlines"></td>\
                                <td id="document_inlines"></td>\
                                <td id="object_inlines"></td>\
                                <td id="external_inlines"></td>\
                            </tr>\
                        </table>\
                    </fieldset>';
            jQuery("div#translations-group").before(tag_cp_area);

            return this.each(function(){
                var $this = $(this);
                var data = $this.data('keys');

                if (!data)
                {
                    $this.data('keys',[]);
                }

                $this.on('change.rtg', methods.update_tags);
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
                    jQuery.getJSON(settings.helper_url, {'media_id': value, 'media_ctype': inline_name}, function(data) { methods.build_inline(data); });
                    existing_keys.push(value);
                }
            });

        },

        build_inline : function(media) {
            var html = $("<span>{% inline "+media.form_of+" "+media.slug+" %}</span>").attr("id", media.form_of+'_'+media.pk);

            $(html)
                .hide()
                .appendTo("td#"+media.form_of+"_inlines")
                .fadeIn()
                .after("<br/>");
        }
    };

})(jQuery);