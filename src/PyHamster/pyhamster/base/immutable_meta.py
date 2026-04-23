# Immutable metaclass

class ImmutableMeta(type):
    """
    Immutable class.

    - Unable to set class attribute values.
    - Unable to delete class attributes.
    """
    
    def __setattr__(cls, name, value):
        if hasattr(cls, name):
            raise Exception(f"Cannot modify immutable object: '{name}'")
    
    def __delattr__(self, name):
        raise Exception(f"Cannot delete immutable object: '{name}'")