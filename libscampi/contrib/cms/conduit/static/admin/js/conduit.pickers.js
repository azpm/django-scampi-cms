/**
 Picking Form Builder
 */

function Pickers() {
    "use strict";
    this.incl = {
        prefix:"incl",
        label:"Inclusion",
        total_forms:0,
        initial_forms:0,
        max_forms:0,
        bar_color:"#9ac4a7"
    };
    this.excl = {
        prefix:"excl",
        label:"Exclusion",
        total_forms:0,
        initial_forms:0,
        max_forms:0,
        bar_color:"#c49b98"
    };
    this.available_pickers = [];
}

Pickers.prototype.update_element_index = function (elem, prefix, replace, ndx, formrow) {
    "use strict";
    var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
            replacement = replace + '-' + ndx + '-';

    //loop over the elem for compound form elements
    jQuery.each(elem, function (index, value) {
        //get the jQuery friendly value
        var ptr = jQuery(value);
        //update the prefix-# values for each element
        if (ptr.attr("for")) {
            ptr.attr("for", ptr.attr("for").replace(idRegex, replacement));
        }
        if (ptr.attr('name')) {
            ptr.attr('name', ptr.attr('name').replace(idRegex, replacement));
            //ptr.attr('name', label);
        }
        if (ptr.attr('id')) {
            var curr_id = ptr.attr('id');
            ptr.attr('id', ptr.attr('id').replace(idRegex, replacement));
            if (curr_id !== ptr.attr('id')) {
                jQuery.event.trigger('filter_id_update', [ptr.attr('id'), formrow]);
            }
        }

    });
};

Pickers.prototype.bundle_filters = function () {
    "use strict";
    var self = this;

    jQuery.each([self.incl, self.excl], function (index, filter_type) {
        var type = filter_type.prefix;
        var fieldsets = jQuery("fieldset." + type + "_group");
        //order the form count correctly
        var total_forms = jQuery("#id_" + type + "-TOTAL_FORMS");
        filter_type.total_forms = 0; //always set the base counter to zero

        jQuery.each(fieldsets, function (k, v) {
            //reset counters in the available filters, this is done for each group
            /* jQuery.each(self.available_pickers, function (picker_index, picker_value) {
                picker_value.incl_count = 0;
                picker_value.excl_count = 0;
            }); */
            var count = k + 1;

            var fieldset = jQuery(v);
            var form_rows = jQuery(fieldset).find("div.form-row:not([name=filter_adder])");

            jQuery.each(form_rows, function (num, form_row) {
                var div = jQuery(form_row); //if you're trying to follow along this is a jquery friendly object of a form row
                //var picker_ptr = div.attr("data-filter-ptr");
                //var picking_filter = self.available_pickers[picker_ptr];

                //order the item correctly
                self.update_element_index(jQuery(div).find("label ~ input,select"), "form", type, k, div);
            });

            //increase form count for each group
            if (form_rows.length > 0)
            { //only if we had a group
                filter_type.total_forms += 1;
                //total_forms.val(count);
            }
        });

        total_forms.val(filter_type.total_forms);
    });

    return true;
};

Pickers.prototype.add_filter = function (type, group_suffix, initial) {
    "use strict";
    var self = this;
    var id_pointer = type + group_suffix;

    var index = null;
    var picking_filter = null;

    if (initial === null) {
        index = jQuery("#" + id_pointer + "_picking_element").val();
        if (index in self.available_pickers) {
            picking_filter = self.available_pickers[index];
        }
        else {
            if (window.console && window.console.log) {
                window.console.log('cannot add filter', type, group_suffix, index, id_pointer);
            }
            return;
        }
    }
    else {
        index = jQuery("#" + id_pointer + "_picking_element option:contains('" + initial[1] + "')").val();
        picking_filter = {
            name:initial[1],
            html:initial[2]
        };
    }

    //remove ability to add this filter element to the group again
    jQuery("#" + id_pointer + "_picking_element option[value='" + index + "']").remove();
    //add the filter box
    jQuery("#" + id_pointer + "_filters > div.form-row").filter(":last").after('<div class="form-row" data-filter-ptr="' + index + '"><div><label>' + picking_filter.name + '</label>' + picking_filter.html + '&nbsp;<a class="inline-deletelink">Delete</a></div></div>');
    //add "remove filter" action to little grey x button
    jQuery("#" + id_pointer + "_filters > div.form-row").filter(":last").find("a").bind("click", function () {
        self.remove_filter(this, id_pointer, index);
    });

    self.bundle_filters();
};

Pickers.prototype.remove_filter = function (elem, id_pointer, picker_id) {
    "use strict";
    var self = this;

    if (picker_id in self.available_pickers) {
        var picking_filter = self.available_pickers[picker_id];

        //add back to list of available filters
        jQuery("#" + id_pointer + "_filters select[name*='picking_elements']").append('<option value="' + picker_id + '">' + picking_filter.name + '</option>');
    }
    else {
        window.alert("Fatal error, filter id is no longer available. Please contact the web team");
    }

    //remove the form row no matter what
    jQuery(elem).parent().parent().remove();
    self.bundle_filters();
};

Pickers.prototype.create_fieldsets = function () {
    "use strict";
    var self = this;
    var img = jQuery("img[alt*='Add Another']").filter(":last");

    var temp_types = [self.incl, self.excl];

    //loop over the types in make fieldsets
    jQuery.each(temp_types, function (index, value) {
        //create the base fieldsets
        jQuery('input[name*="csrfmiddlewaretoken"]').after('<input type="hidden" name="' + value.prefix + '-TOTAL_FORMS" id="id_' + value.prefix + '-TOTAL_FORMS" value="0"/><input type="hidden" name="' + value.prefix + '-INITIAL_FORMS" id="id_' + value.prefix + '-INITIAL_FORMS" value="0"/><input type="hidden" name="' + value.prefix + '-MAX_NUM_FORMS" id="id_' + value.prefix + '-MAX_NUM_FORMS" value=""/><input type="hidden" name="includes-pickers" value="1"/>');
        self.create_fieldset(value, 0);
    });
};

Pickers.prototype.create_fieldset = function (type, num) {
    "use strict";
    var self = this;
    var img = jQuery("img[alt*='Add Another']").filter(":last");
    var group_suffix = '_group_' + num;
    var id_pointer = type.prefix + group_suffix;

    var html = jQuery('<fieldset class="module aligned ' + type.prefix + '_group" id="' + id_pointer + '_filters"><h2 id="' + id_pointer + '" style="background:' + type.bar_color + ' !important;">' + type.label + ' Picking Group</h2><div class="description"></div><div class="form-row" id="' + id_pointer + '_filter_adder" name="filter_adder"><div><label for="' + id_pointer + 'picking_element">Filter Using:</label><select name="picking_elements" id="' + id_pointer + '_picking_element"><option>---------</option></select><a class="add-another" id="' + id_pointer + '_add_filter"></a></div></div></fieldset>');

    html.hide();

    if (num === 0) {
        //create the base fieldsets
        jQuery("fieldset").filter(":last").after(html);
        jQuery("fieldset." + type.prefix + "_group > div.description").append('<a class="addlink" id="' + id_pointer + '_add_group">Add Group</a>');

        //bind click to adding a new group
        jQuery("#" + id_pointer + "_add_group").bind("click", function () {
            self.create_fieldset(type, num += 1);
        });
    }
    else {
        //create the base fieldsets
        jQuery("fieldset." + type.prefix + "_group").filter(":last").after(html);
        jQuery("fieldset#" + id_pointer + "_filters > div.description").append("<a class='deletelink' id='" + id_pointer + "_delete_group'>Delete Group</a>");

        //bind click to adding a new group
        jQuery("#" + id_pointer + "_delete_group").bind("click", function () {
            self.delete_fieldset(this);
        });
    }

    //add available picking fields to the select boxes
    jQuery.each(self.available_pickers, function (index, value) {
        jQuery("#" + id_pointer + "_filters select[name*='picking_elements']").append('<option value="' + index + '">' + value.name + '</option>');
    });

    //First we add the little green plus sign image, then we bind clicking it to ourself "add_filter"
    jQuery("#" + id_pointer + "_add_filter").append(img.clone());
    jQuery("#" + id_pointer + "_add_filter").bind("click", function () {
        self.add_filter(type.prefix, group_suffix, null);
    });

    html.slideDown("fast");
};


Pickers.prototype.delete_fieldset = function (elem) {
    "use strict";
    //remove the form row no matter what
    jQuery(elem).parent().parent().remove();
};

Pickers.prototype.process_available = function (data) {
    "use strict";
    var self = this;
    var picker_ids = [];

    var html = jQuery('<fieldset class="module aligned" id="picked-objects"><h2>Preview Picker <a class="refresh-icon web-symbol" id="refresh-picked" href="#refresh-picked">V</a></h2><div class="form-row" id="picked-objects"></div></fieldset>');
    html.hide();
    jQuery("fieldset").filter(":last").after(html);

    html.slideDown("fast", function () {
        jQuery.each(data.filters, function (index, value) {
            var picker = {
                //incl_count:0,
                //excl_count:0,
                name:value[1],
                id:value[0],
                html:value[2]
            };

            picker_ids.push(value[0]);
            self.available_pickers.push(picker);
        });

        self.create_fieldsets();
        var num = 0;

        //noinspection JSUnresolvedVariable
        jQuery.each(data.existing.incl, function (index, value) {
            if (index > 0) {
                self.create_fieldset(self.incl, num);
            }

            jQuery.each(value, function (i, property) {
                self.add_filter(self.incl.prefix, '_group_' + num, property);
            });

            num += 1;
        });

        num = 0;
        //noinspection JSUnresolvedVariable
        jQuery.each(data.existing.excl, function (index, value) {
            if (index > 0) {
                self.create_fieldset(self.excl, num);
            }

            jQuery.each(value, function (i, property) {
                self.add_filter(self.excl.prefix, '_group_' + num, property);
            });

            num += 1;
        });

        jQuery("a#refresh-picked").delay(800).click();
    });
};
