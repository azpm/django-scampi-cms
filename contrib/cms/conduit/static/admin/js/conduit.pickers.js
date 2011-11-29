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
    };
    
    this.excl = {
        prefix: "excl",
        label: "Exclusion",
        total_forms: 0,
        initial_forms: 0,
        max_forms: 0,
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
 				<label>'+picking_filter.name+'</label>'+picking_filter.html+'\
 			</div> \
 			<a href="#" class="deletelink">Remove</a> \
 		</div>');
 	
	//im leaving this here because I liked the selector and don't want to forget it 	
 	//self.update_element_index(jQuery("#"+type+"_picker_filters > div.form-row").filter(":last").find("label ~ input,select"), "form", type, (type == "incl") ? picking_filter.incl_count : picking_filter.excl_count);
    
    jQuery("#"+id_pointer+"_filters > div.form-row").filter(":last").find("a").bind("click", function() { self.remove_filter(this, type, picking_filter.id); });
}

Pickers.prototype.remove_filter = function(elem, type, picking_elem)
{  
    jQuery(elem).parent().remove(); //remove the form row no matter what
}

Pickers.prototype.bundle_filters = function() {
	var self = this;
    
    var temp_types = [self.incl, self.excl];
    
    //reset counters in the available filters
    jQuery.each(self.available_pickers, function(picker_index, picker_value)
    {
    	picker_value.incl_count = 0;
        picker_value.excl_count = 0;
    });
    
     //loop over the types in make fieldsets
	jQuery.each(temp_types, function(index, value) 
    {
    	var type = value.prefix;
    	var form_rows = jQuery("#"+value.prefix+"_picker_filters > div.form-row:not(#"+type+"-filter-adder)");
    	//loop over the form rows
    	jQuery.each(form_rows, function(div_index, div_value)
    	{
    		var div = jQuery(div_value); //if you're trying to follow along this is a jquery friendly object of a form row
    		var picker_ptr = div.attr("data-filter-ptr");
    		var picking_filter = self.available_pickers[picker_ptr];
			
			//order the item correctly
			self.update_element_index(jQuery(div).find("label ~ input,select"), "form", type, (type == "incl") ? picking_filter.incl_count : picking_filter.excl_count);
			
			//order the form count correctly
			var total_forms = jQuery("#id_"+type+"-TOTAL_FORMS");
    
			if (type == "incl") //update inclusion form
			{
				picking_filter.incl_count++;
				if (picking_filter.incl_count > total_forms.val())
				{
					total_forms.val(picking_filter.incl_count);
				}
			}
			else //update exclusion form
			{
				picking_filter.excl_count++;
				if (picking_filter.excl_count > total_forms.val())
				{
					total_forms.val(picking_filter.excl_count);
				}
			}
			
    	});
	});
	
	return true;
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
        jQuery("form").filter("input[type=hidden]:last").after('\
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
            <h2 id="'+id_pointer+'">'+type.label+' Picking Group</h2> \
            <div class="form-row" id="'+id_pointer+'_filter_adder"> \
                <div> \
                    <label for="'+id_pointer+'picking_element">Filter Using:</label> \
                    <select name="picking_elements" id="'+id_pointer+'_picking_element"><option>---------</option></select> \
                    <a href="#" class="add-another" id="'+id_pointer+'_add_filter"></a> \
                </div> \
            </div> \
        </fieldset>';

    if (num == 0)
    {
        //create the base fieldsets
        jQuery("fieldset").filter(":last").after(html);
    }
    else
    {
        //create the base fieldsets
        jQuery("fieldset[name='"+type.prefix+"_group']").filter(":last").after(html);
        
    }
    
    //add available picking fields to the select boxes
    jQuery.each(self.available_pickers, function(index, value) 
    {
        jQuery("#"+id_pointer+"_filters").filter("select[name*='picking_elements']").append('<option value="'+index+'">'+value.name+'</option>');
    });
    
    /**
    First we add the little green plus sign image, then we bind clicking it to ourself "add_filter"
    */
    jQuery("#"+id_pointer+"_add_filter").append(img.clone());
    jQuery("#"+id_pointer+"_add_filter").bind("click", function() { self.add_filter(type.prefix, group_suffix); });

    
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