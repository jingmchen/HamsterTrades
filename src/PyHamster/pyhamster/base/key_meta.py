# Metaclass for Keys or Constants
#   - Provide structured nested hierarchy constants for readability
#   - Prevent write-access to constants during runtime

import re

class KeyMeta(type):
    """Metaclass with lazy attribute resolution (reference evaluated only upon access)."""
    _frozen = False

    def __getattribute__(cls, name):
        val = super().__getattribute__(name)
        if isinstance(val, _Key): # If lazy marker
            return val.resolve()
        return val
    
    def __setattr__(cls, name, value):
        if type.__getattribute__(cls, '_frozen'):
            raise AttributeError(f"{cls.__name__} is frozen; prohibits write access to '{name}'")
        super().__setattr__(name, value)

class _Key:
    """A string with {dotted.path} placeholders resolved against a root."""
    _root = None # Set during freeze()

    def __init__(self, template, cast=None):
        self.template = template
        self.cast = cast
    
    def resolve(self):
        def replace(match):
            path = match.group(1).split('.')
            obj = _Key._root
            for part in path:
                obj = getattr(obj, part)
            return str(obj)
        result = re.sub(r'\{([\w.]+)\}', replace, self.template)
        return self.cast(result) if self.cast else result

def K(template, cast=None):
    return _Key(template, cast)

def freeze(cls, root=None):
    if root is not None:
        _Key._root = root
    for attr_name in dir(cls):
        if attr_name.startswith('__'):
            continue
        attr = type.__getattribute__(cls, attr_name)
        if isinstance(attr, type) and isinstance(type(attr), KeyMeta):
            freeze(attr)
    
    type.__setattr__(cls, '_frozen', True)
    return cls