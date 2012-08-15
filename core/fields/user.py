from django.forms import ModelChoiceField, ModelMultipleChoiceField

class UserModelChoiceField(ModelChoiceField):
    """
    A ModelChoiceField to represent User
    select boxes in the Auto Admin
    """
    def label_from_instance(self, obj):
        return "%s (%s)"%(obj.get_full_name(), obj.username)

class UserModelMultipleChoiceField(ModelMultipleChoiceField):
    """
    Similar to UserModelChoiceField, provide a nicer-looking
    list of user names for ManyToMany Relations...
    """
    def label_from_instance(self, obj):
        return "%s (%s)"%(obj.get_full_name(), obj.username)