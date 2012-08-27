try:
    from south.modelsinspector import add_introspection_rules
    
    #south introspection: crypto fields
    add_introspection_rules([], ["^libscampi\.core\.fields\.crypto\.EncryptedTextField"])
    add_introspection_rules([], ["^libscampi\.core\.fields\.crypto\.EncryptedCharField"])
    add_introspection_rules([], ["^libscampi\.core\.fields\.crypto\.EncryptedDateField"])
    add_introspection_rules([], ["^libscampi\.core\.fields\.crypto\.EncryptedDateTimeField"])
    add_introspection_rules([], ["^libscampi\.core\.fields\.crypto\.EncryptedIntField"])
    add_introspection_rules([], ["^libscampi\.core\.fields\.crypto\.EncryptedLongField"])
    add_introspection_rules([], ["^libscampi\.core\.fields\.crypto\.EncryptedFloatField"])

    #south introspection: pickling
    add_introspection_rules([], ["^libscampi\.core\.fields\.pickle\.PickledObjectField"])
    
except ImportError:
    pass

from libscampi.core.fields.pickle import PickledObjectField
from libscampi.core.fields.crypto import EncryptedTextField, EncryptedCharField, EncryptedDateField, EncryptedDateTimeField, EncryptedIntField, EncryptedLongField, EncryptedFloatField
from libscampi.core.fields.user import UserModelChoiceField, UserModelMultipleChoiceField