(function($) {
    "use strict";
    // apply methods
    $.fn.imageRollover = function (method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.RelatedImagePreview');
        }
    };

    var settings = {
        xOffset: 10,
        yOffset: 10
    };

    var methods = {
       init : function(){
           return this.each(function(){
                var this_ = $(this);
                this_.hover(methods.hover_in, methods.hover_out);
                this_.mousemove(methods.mouse_move);
           });
       },
       hover_in : function(event) {
           "use strict";
            var elem = $(this);
            var text = elem.attr("title");
            $("body").append("<p id='img_preview_popover'><img src='"+ elem.attr('rel') +"' alt='url preview' /><br/>&nbsp;&nbsp;"+ text +"</p>");
            $("#img_preview_popover")
                   //.css("top",(elem.offset().top - settings.xOffset) + "px")
                   //.css("right",(elem.offset().left + settings.yOffset) + "px")
                   .css("top",(event.pageY - settings.yOffset) + "px")
                   .css("right",(event.pageX + settings.xOffset) + "px")
                   .fadeIn("fast");
       },
       hover_out : function(event) {
           "use strict";
           $("#img_preview_popover").remove();
       },
       mouse_move : function(event) {
           "use strict";
           var elem = $(this);
           console.log("y: "+event.pageY + " x: " + event.pageX);
           $("#img_preview_popover")
               //.css("top",(elem.offset().top - settings.xOffset) + "px")
               //.css("right",(elem.offset().left + settings.yOffset) + "px");
               .css("top",(event.pageY - settings.yOffset) + "px")
               .css("right",(event.pageX + settings.xOffset) + "px");
       }
    };
})(jQuery);
