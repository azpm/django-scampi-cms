/**
 * Author: Joey Leingang
 * Date: 5/22/12
 *
 */

(function($) {
    "use strict";

    $.fn.scampiAdminToolbar = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.jModalbox');
        }
    };

    var settings = {

    };

    var methods = {
        init: function(opts) {
            if (opts)
            {
                jQuery.extend(settings, opts);
            }


            return this.each(function(){
                var $this = $(this);
                var data = $this.data('keys');

                //shouldn't be an data set (we haven't built anything yet)
                if (!data)
                {
                    $this.data('keys',[]);
                }
            });

        }
    };


})(admin.jQuery);