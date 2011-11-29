/**
 Picking Form Builder
*/


function Pickers() {
    this.incl = {
        prefix: "incl",
        label: "Inclusion",
        total_forms: 0,
        initial_forms: 0,
        max_forms: 0,
        bar_color: "#9ac4a7"
    };
    
    this.excl = {
        prefix: "excl",
        label: "Exclusion",
        total_forms: 0,
        initial_forms: 0,
        max_forms: 0,
        bar_color: "#c49b98"
    };
    
    this.available_pickers = new Array();
    
    this.existing_options = {
        incl: new Array(),
        excl: new Array()
    };
    
    this.raw_data = null;
}

Pickers.prototype.update_element_index = function(elem, prefix, replace, ndx) 
{
	var idRegex = new RegExp(prefix + '-(\\d+|__prefix__)-'),
		replacement = replace + '-' + ndx + '-';
		
	//loop over the elem for compound form elements
	jQuery.each(elem, function(index, value) 
    {
    	//get the jQuery friendly value
		var ptr = jQuery(value);
		//update the prefix-# values for each element
		if (ptr.attr("for")) ptr.attr("for", ptr.attr("for").replace(idRegex, replacement));
		if (ptr.attr('id')) ptr.attr('id', ptr.attr('id').replace(idRegex, replacement));
		if (ptr.attr('name')) ptr.attr('name', ptr.attr('name').replace(idRegex, replacement));
	});
}

Pickers.prototype.bundle_filters = function() 
{
    var self = this;
    var temp_types = [self.incl, self.excl];
    
    jQuery.each(temp_types, function(index, value)
    {
        var type = value.prefix;
        var fieldsets = jQuery("fieldset[name="+type+"_group]");
        
        jQuery.each(fieldsets, function(k, v)
        {
            //reset counters in the available filters, this is done for each group
            jQuery.each(self.available_pickers, function(picker_index, picker_value)
            {
                picker_value.incl_count = 0;
                picker_value.excl_count = 0;
            });
            
            //order the form count correctly
			var total_forms = jQuery("#id_"+type+"-TOTAL_FORMS");
            var count = k+1;
            var form_rows = jQuery(v).filter("div.form-row:not([name=filter_adder]");
            
            jQuery.each(form_rows, function(k2, form_row) 
            {
                var div = jQuery(form_row); //if you're trying to follow along this is a jquery friendly object of a form row
                var picker_ptr = div.attr("data-filter-ptr");
                var picking_filter = self.available_pickers[picker_ptr];
                
                //order the item correctly
                self.update_element_index(jQuery(div).find("label ~ input,select"), "form", type, (type == "incl") ? picking_filter.incl_count : picking_filter.excl_count);
            });
            
            //increase form count for each group
            total_forms.val(count);
        });
    });
    
    return true;
}

Pickers.prototype.add_filter = function(type, group_suffix)
{
	var self = this;
	var id_pointer = type+group_suffix;
    
	var index = jQuery("#"+id_pointer+"_picking_element").val();
 	if (index in self.available_pickers)
 	{
 		var picking_filter = self.available_pickers[index];
 	}
 	else
 	{
 		return;
 	}
    
    //remove ability to add this filter element to the group again
    jQuery("#"+id_pointer+"_picking_element option[value='"+index+"']").remove();
 	//add the filter box
    jQuery("#"+id_pointer+"_filters > div.form-row").filter(":last").after('\
 		<div class="form-row" data-filter-ptr="'+index+'">\
 			<div>\
 				<label>'+picking_filter.name+'</label>'+picking_filter.html+'&nbsp;<a class="inline-deletelink">Delete</a> \
 			</div> \
 		</div>');
 	
	//im leaving this here because I liked the selector and don't want to forget it 	
 	//self.update_element_index(jQuery("#"+type+"_picker_filters > div.form-row").filter(":last").find("label ~ input,select"), "form", type, (type == "incl") ? picking_filter.incl_count : picking_filter.excl_count);
    
    jQuery("#"+id_pointer+"_filters > div.form-row").filter(":last").find("a").bind("click", function() { self.remove_filter(this, id_pointer, index); });
}

Pickers.prototype.remove_filter = function(elem, id_pointer, picker_id)
{  
    var self = this;
	
    if (picker_id in self.available_pickers)
 	{
 		var picking_filter = self.available_pickers[picker_id];
        
        //add back to list of available filters
        jQuery("#"+id_pointer+"_filters select[name*='picking_elements']").append('<option value="'+picker_id+'">'+picking_filter.name+'</option>');
 	}
 	else
 	{
 		alert("Fatal error, filter id is no longer available. Please contact the web team");
 	}
   
    //remove the form row no matter what
    jQuery(elem).parent().parent().remove(); 
}

Pickers.prototype.create_fieldsets = function()
{
    var self = this;
	var img = jQuery("img[alt*='Add Another']").filter(":last");
    
    var temp_types = [self.incl, self.excl];
    
    //loop over the types in make fieldsets
	jQuery.each(temp_types, function(index, value) 
    {
        //create the base fieldsets
        jQuery('input[name*="csrfmiddlewaretoken"]').after('\
            <input type="hidden" name="'+value.prefix+'-TOTAL_FORMS" id="id_'+value.prefix+'-TOTAL_FORMS" value="0"> \
            <input type="hidden" name="'+value.prefix+'-INITIAL_FORMS" id="id_'+value.prefix+'-INITIAL_FORMS" value="0"> \
            <input type="hidden" name="'+value.prefix+'-MAX_NUM_FORMS" id="id_'+value.prefix+'-MAX_NUM_FORMS" value=""> \
            ');
        self.create_fieldset(value, 0);
            
    });
}

Pickers.prototype.create_fieldset = function(type, num) 
{
    var self = this;
    var img = jQuery("img[alt*='Add Another']").filter(":last");
    var group_suffix = '_group_'+num;
    var id_pointer = type.prefix+group_suffix;
    
    var html = '\
        <fieldset class="module aligned" name="'+type.prefix+'_group" id="'+id_pointer+'_filters"> \
            <h2 id="'+id_pointer+'" style="background-color:'+type.bar_color+';">'+type.label+' Picking Group</h2> \
            <div class="description"></div> \
            <div class="form-row" id="'+id_pointer+'_filter_adder" name="filter_adder"> \
                <div> \
                    <label for="'+id_pointer+'picking_element">Filter Using:</label> \
                    <select name="picking_elements" id="'+id_pointer+'_picking_element"><option>---------</option></select> \
                    <a class="add-another" id="'+id_pointer+'_add_filter"></a> \
                </div> \
            </div> \
        </fieldset>';

    if (num == 0)
    {
        //create the base fieldsets
        jQuery("fieldset").filter(":last").after(html);
        jQuery("fieldset[name='"+type.prefix+"_group'] > div.description").append('<a class="addlink" id="'+id_pointer+'_add_group">Add Group</a>');
        
        //bind click to adding a new group
        jQuery("#"+id_pointer+"_add_group").bind("click", function() { self.create_fieldset(type, num+=1); });
    }
    else
    {
        //create the base fieldsets
        jQuery("fieldset[name='"+type.prefix+"_group']").filter(":last").after(html);
        jQuery("fieldset#"+id_pointer+"_filters > div.description").append("<a class='deletelink' id='"+id_pointer+"_delete_group'>Delete Group</a>");
        
        //bind click to adding a new group
        jQuery("#"+id_pointer+"_delete_group").bind("click", function() { self.delete_fieldset(this); });
    }
    
    //add available picking fields to the select boxes
    jQuery.each(self.available_pickers, function(index, value) 
    {
        jQuery("#"+id_pointer+"_filters select[name*='picking_elements']").append('<option value="'+index+'">'+value.name+'</option>');
    });
    
    //First we add the little green plus sign image, then we bind clicking it to ourself "add_filter"
    jQuery("#"+id_pointer+"_add_filter").append(img.clone());
    jQuery("#"+id_pointer+"_add_filter").bind("click", function() { self.add_filter(type.prefix, group_suffix); });
   
}

Pickers.prototype.delete_fieldset = function(elem)
{
    //remove the form row no matter what
    jQuery(elem).parent().parent().remove();
}

Pickers.prototype.process_available = function(data) {
    var self = this;
    
    jQuery.each(data.filters, function(index, value) {
        var picker = {
            incl_count: 0,
            excl_count: 0,
            name: value[1],
            id: value[0],
            html: value[2]
        };
        
        self.available_pickers.push(picker);
    });
    
    this.create_fieldsets();
    /*
    jQuery.each(data.existing.incl, function(index, value) 
    {
        jQuery.each(value, function(i, property)
        {
            alert(i);
        });
    });*/
}