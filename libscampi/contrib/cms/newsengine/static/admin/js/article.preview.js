(function($) {
    // apply methods
    $.fn.ArticlePreview = function (preview_url) {
        //handle preview button
        var original_action = $("form#article_form").attr('action');
        var preview_button = "<input type='submit' value='Preview' class='preview' name='_preview' />";

        $(".submit-row").find("input:last").before(preview_button);

        $("input[name='_preview']").click(function(e){
            e.preventDefault();
            $("form#article_form").attr({"action": preview_url, "target": "_blank"});
            $("form#article_form").submit();
        });
        $("input[type='submit'][name!='_preview']").click(function(){
            $("form#article_form").attr({"action": original_action, "target": "_self"});
        });
    };

})(jQuery);
