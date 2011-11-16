from django import template
from django.template.loader import render_to_string
from django.db.models import Max

register = template.Library()

class layout_node(template.Node):
    def __init__(self, slice):
        self.slice = template.Variable(slice)
    
    def render(self, context):
        slice = self.slice.resolve(context)
        
        #get all boxes for this slice        
        box_collection = slice.namedbox_set.filter(active=True)
        maximum_y = box_collection.aggregate(max_y = Max('gridy'))['max_y']
        grid = []
        
        if maximum_y is not None:
            for i in range(0, maximum_y):
                grid.append([ [],[],[] ])

            for box in box_collection:
                grid[box.gridy-1][box.gridx-1].append(box)
        
        template = "%s/layout/boxgrid.html" % slice.commune.theme.keyname
        return render_to_string(template, {'grid': grid}, context)
        
def generate_layout(parser, token):
    try:
        tag_name, slice = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]
    
    return layout_node(slice)

register.tag('generate_layout', generate_layout)