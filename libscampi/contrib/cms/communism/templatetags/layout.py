from django import template
from django.template.loader import render_to_string
from django.db.models import Max

register = template.Library()


class LayoutNode(template.Node):
    def __init__(self, page_slice):
        self.slice = template.Variable(page_slice)

    def render(self, context):
        page_slice = self.slice.resolve(context)

        # get all boxes for this slice
        box_collection = page_slice.namedbox_set.select_related(
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
                grid[box.gridy - 1][box.gridx - 1].append(box)

        try:
            theme = context['cms_page']['theme']
        except (KeyError, ValueError):
            return ""
        else:
            tpl = "%s/layout/boxgrid.html" % theme.keyname

        return render_to_string(tpl, {'grid': grid}, context)


def generate_layout(parser, token):
    try:
        tag_name, page_slice = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents.split()[0]

    return LayoutNode(page_slice)


register.tag('generate_layout', generate_layout)
