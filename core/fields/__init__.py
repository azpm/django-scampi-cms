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
    add_introspection_rules([], ["^libscampi\.core\.fields\.pickle\.PickleField"])

    #south introspection: UUID
    add_introspection_rules([], ["^libscampi\.core\.fields\.uuid\.UUIDField"])
    
except ImportError:
    pass

from .uuid import UUIDField
from .pickle import PickleField
from .crypto import EncryptedTextField, EncryptedCharField, EncryptedDateField, EncryptedDateTimeField, EncryptedIntField, EncryptedLongField, EncryptedFloatField