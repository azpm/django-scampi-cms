/**
 Picking Form Builder
 */

class Pickers {
    constructor() {
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

    update_element_index(elem, prefix, replace, ndx, formrow) {
        const idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
            replacement = replace + '-' + ndx + '-';

        //loop over the elem for compound form elements
        elem.each((_, value) => {
            //get the django.jQuery friendly value
            const ptr = django.jQuery(value);
            //update the prefix-# values for each element
            if (ptr.attr("for")) {
                ptr.attr("for", ptr.attr("for").replace(idRegex, replacement));
            }
            if (ptr.attr('name')) {
                ptr.attr('name', ptr.attr('name').replace(idRegex, replacement));
                //ptr.attr('name', label);
            }
            if (ptr.attr('id')) {
                const curr_id = ptr.attr('id');
                ptr.attr('id', ptr.attr('id').replace(idRegex, replacement));
                if (curr_id !== ptr.attr('id')) {
                    django.jQuery.event.trigger('filter_id_update', [ptr.attr('id'), formrow]);
                }
            }

        });

    }

    bundle_filters() {
        [this.incl, this.excl].forEach((filter_type) => {
            const type = filter_type.prefix;
            const fieldsets = django.jQuery("fieldset." + type + "_group");
            //order the form count correctly
            const total_forms = django.jQuery("#id_" + type + "-TOTAL_FORMS");
            filter_type.total_forms = 0; //always set the base counter to zero

            fieldsets.each((k, v) => {
                const fieldset = django.jQuery(v);
                const form_rows = django.jQuery(fieldset).find("div.form-row:not([name=filter_adder])");

                form_rows.each((_, form_row) => {
                    const div = django.jQuery(form_row); //if you're trying to follow along this is a django.jQuery friendly object of a form row
                    //order the item correctly
                    this.update_element_index(django.jQuery(div).find("label ~ input,select"), "form", type, k, div);
                });

                //increase form count for each group
                if (form_rows.length > 0) { //only if we had a group
                    filter_type.total_forms += 1;
                }
            });

            total_forms.val(filter_type.total_forms);
        });

        return true;
    }

    add_filter(type, group_suffix, initial) {
        const id_pointer = type + group_suffix;

        let index = null;
        let picking_filter = null;

        if (initial === null) {
            index = django.jQuery("#" + id_pointer + "_picking_element").val();
            if (index in this.available_pickers) {
                picking_filter = this.available_pickers[index];
            }
            else {
                if (window.console && window.console.log) {
                    window.console.log('cannot add filter', type, group_suffix, index, id_pointer);
                }
                return;
            }
        }
        else {
            index = django.jQuery("#" + id_pointer + "_picking_element option:contains('" + initial[1] + "')").val();
            picking_filter = {
                name:initial[1],
                html:initial[2]
            };
        }

        //remove ability to add this filter element to the group again
        django.jQuery("#" + id_pointer + "_picking_element option[value='" + index + "']").remove();
        //add the filter box
        django.jQuery("#" + id_pointer + "_filters > div.form-row").filter(":last").after('<div class="form-row" data-filter-ptr="' + index + '"><div><label>' + picking_filter.name + '</label>' + picking_filter.html + '&nbsp;<a class="inline-deletelink">Delete</a></div></div>');
        //add "remove filter" action to little grey x button
        django.jQuery("#" + id_pointer + "_filters > div.form-row").filter(":last").find("a").bind("click", (e) => {
            this.remove_filter(e.target, id_pointer, index);
        });

        this.bundle_filters();
    }

    remove_filter(elem, id_pointer, picker_id) {
        console.log('remove filter called');
        if (picker_id in this.available_pickers) {
            const picking_filter = this.available_pickers[picker_id];

            //add back to list of available filters
            django.jQuery("#" + id_pointer + "_filters select[name*='picking_elements']").append('<option value="' + picker_id + '">' + picking_filter.name + '</option>');
        }
        else {
            window.alert("Fatal error, filter id is no longer available. Please contact the web team");
        }

        //remove the form row no matter what
        django.jQuery(elem).parent().parent().remove();
        this.bundle_filters();
    }

    create_fieldsets() {
        //loop over the types in make fieldsets
        [this.incl, this.excl].forEach((value) => {
            //create the base fieldsets
            django.jQuery('input[name*="csrfmiddlewaretoken"]').after('<input type="hidden" name="' + value.prefix + '-TOTAL_FORMS" id="id_' + value.prefix + '-TOTAL_FORMS" value="0"/><input type="hidden" name="' + value.prefix + '-INITIAL_FORMS" id="id_' + value.prefix + '-INITIAL_FORMS" value="0"/><input type="hidden" name="' + value.prefix + '-MAX_NUM_FORMS" id="id_' + value.prefix + '-MAX_NUM_FORMS" value=""/><input type="hidden" name="includes-pickers" value="1"/>');
            this.create_fieldset(value, 0);
        });
    }

    create_fieldset(type, num) {
        const img = django.jQuery("img[alt*='Add Another']").filter(":last");
        const group_suffix = '_group_' + num;
        const id_pointer = type.prefix + group_suffix;

        const html = django.jQuery('<fieldset class="module aligned ' + type.prefix + '_group" id="' + id_pointer + '_filters"><h2 id="' + id_pointer + '" style="background:' + type.bar_color + ' !important;">' + type.label + ' Picking Group</h2><div class="description"></div><div class="form-row" id="' + id_pointer + '_filter_adder" name="filter_adder"><div><label for="' + id_pointer + 'picking_element">Filter Using:</label><select name="picking_elements" id="' + id_pointer + '_picking_element"><option>---------</option></select><a class="add-another" id="' + id_pointer + '_add_filter"></a></div></div></fieldset>');

        html.hide();

        if (num === 0) {
            //create the base fieldsets
            django.jQuery("fieldset").filter(":last").after(html);
            django.jQuery("fieldset." + type.prefix + "_group > div.description").append('<a class="addlink" id="' + id_pointer + '_add_group">Add Group</a>');

            //bind click to adding a new group
            django.jQuery("#" + id_pointer + "_add_group").bind("click", () => {
                this.create_fieldset(type, num += 1);
            });
        }
        else {
            //create the base fieldsets
            django.jQuery("fieldset." + type.prefix + "_group").filter(":last").after(html);
            django.jQuery("fieldset#" + id_pointer + "_filters > div.description").append("<a class='deletelink' id='" + id_pointer + "_delete_group'>Delete Group</a>");

            //bind click to adding a new group
            django.jQuery("#" + id_pointer + "_delete_group").bind("click",  (e) => {
                this.delete_fieldset(e.target);
            });
        }

        //add available picking fields to the select boxes
        this.available_pickers.forEach((value, index) => {
            django.jQuery("#" + id_pointer + "_filters select[name*='picking_elements']").append('<option value="' + index + '">' + value.name + '</option>');
        });

        //First we add the little green plus sign image, then we bind clicking it to ourself "add_filter"
        const addFilter = django.jQuery("#" + id_pointer + "_add_filter");
        addFilter.append(img.clone());
        addFilter.on("click",  (e) => {
            e.stopPropagation();
            this.add_filter(type.prefix, group_suffix, null);
        });

        html.slideDown("fast");
    }

    delete_fieldset(elem) {
        django.jQuery(elem).parent().parent().remove();
    }

    process_available(data) {
        this.available_pickers = data.filters.map(([id, name, html]) => ({
            name: name,
            id: id,
            html: html
        }));

        this.create_fieldsets();

        const process = (haystack, idx, val) => {
            if (idx > 0) {
                this.create_fieldset(haystack, 0);
            }

            val.forEach((prop) => {
                this.add_filter(haystack.prefix, '_group_' + idx, prop)
            });
        };

        data.existing.incl.forEach((val, idx) => {
            process(this.incl, idx, val);
        });

        data.existing.excl.forEach((val, idx) => {
            process(this.excl, idx, val);
        });
    }
}
