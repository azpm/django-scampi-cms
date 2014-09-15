from django import template
from django.template.loader import render_to_string
from django.db.models import Max

register = template.Library()


class LayoutNode(template.Node):
    def __init__(self, html_slice):
        self.html_slice = template.Variable(html_slice)
    
    def render(self, context):
        html_slice = self.html_slice.resolve(context)
        
        #get all boxes for this slice        
        box_collection = html_slice.namedbox_set.select_related(
            'template__id',
            'template__content',
            'content',
            'content__template',
            'staticpicker__content'
        ).filter(active=True)

        maximum_y = box_collection.aggregate(max_y=Max('gridy'))['max_y']
        grid = []
        
        if maximum_y is not None:
            for i in range(0, maximum_y):
                grid.append([[], [], []])

            for box in box_collection:
                grid[box.gridy-1][box.gridx-1].append(box)
        
        try:
            theme = context['cms_page']['theme']
        except (KeyError, ValueError):
            return ""
        else:
            tpl = "{}/layout/boxgrid.html".format(theme.keyname)
        
        return render_to_string(tpl, {'grid': grid}, context)


@register.tag
def generate_layout(parser, token):
    try:
        tag_name, html_slice = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "{0!r:s} tag requires arguments".format(token.contents.split()[0])

    return LayoutNode(html_slice)
