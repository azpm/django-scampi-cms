// renaissance inline media tag generator

(function($) {
    // apply methods
    $.fn.RenassainceTagGenerator = function (method) {
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
            return this.each(function(){
                var $this = $(this);

                $this.live('change textInput', methods.update_tags);
            });
        },
        update_tags : function(e) {
            console.log(this);
        }
    }

})(jQuery);