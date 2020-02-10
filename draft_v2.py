# --- built in ---
import os
import abc
import sys
import time
import logging

from collections import OrderedDict

# --- 3rd party ---
# --- my module ---

'''

Attributes:
    Original class:
        __draftclass__: The draft class wrapping the original non-draft class. This attribute is attached on
            the original class by DraftMeta in DraftMeta.__new__, if it inherits from Draftable.

    Draft class:
        __draftwrappedclass__: (None) The original class whcih is wrapped by the draft class. This attribute is 
            attached on the draft class.
        __draftwrappedparam__: (list, dict) The parameters used to instantiate an instance of the original class.
        __instancedict__: (dict) A <key, instance> mapping to store generated instances.

    Original class instance:
        __draft__: The draft object that the class instance instantiated from. This attribute is attached on
            the original class instances in Draft.instantiate.
        __instancename__: The name (key) of the instance. This attribute is attached on the original class
            instances in Draft.instantiate.

    Draft class instance:
        __draftwrappedclass__: The original class whcih is wrapped by the draft class. This attribute is 
            attached on the draft class.
        __draftwrappedparam__: The parameters used to instantiate an instance of the original class.
        __instancedict__: A (key, instance) mapping to store generated instances.

Main instances:

    Original class:
        __instantiate__: The constructor to instantiate a new object from the draft class. This attribute is
            attached by inheriting from Draftable.
    Draft class:    
        __instantiate__: The constructor to instantiate a new object from the draft class. This attribute is
            attached by inheriting from Draftable.
    
    Original class instance:

    Draft class instance:
    
'''


__all__ = [
    'Draft',
    'Draftable',
    'Instantiate',
    'is_draft',
    'is_subdraft'
]

DEBUG = False

def _draft_factory(cls):
    '''
    _darft_factory
    
    Create a custom Draft class for given cls
    
    Args:
        cls: Class
    '''
    
    # make class name
    class_name = 'Draft'
    # if (cls.__name__[0].isupper() or
    #         (not cls.__name__[0].isalpha())):
    #     class_name = 'Draft'
    # else:
    #     class_name = 'Draft_'

    base_draft = get_baseclass()
        
    class_name = class_name + '[' + cls.__name__ + ']'
    base_class = (base_draft, )
    
    # Custom function for custom Draft
    def __init__(self, *args, **kwargs):
        
        # call super
        _Draft.__init__(self, *args, **kwargs)

    
    def __repr__(self):
        '''
        __repr__ sample: <Draft '__main__.A'>
        '''

        class_repr = repr(self.__draftwrappedclass__)
        default_repr = type.__repr__(self.__draftwrappedclass__)

        if class_repr == default_repr:
            return class_repr.replace('<class', '<{}'.format(base_draft.__name__))
        else:
            return '<{}: '.format(base_draft.__name__) + class_repr + '>'

    def __instantiate__(self, *args, **kwargs):
        '''
        Override instantiate interface
        
        Call class.__instantiate__
        '''

        inst = self.__draftwrappedclass__.__instantiate__(*args, **kwargs)

        setattr(inst, '__instancename__', None)

        return inst

    
    # build attributes dictionary
    attributes = {'__init__': __init__,
                  '__repr__': __repr__,
                  '__instantiate__': __instantiate__,
                  '__draftwrappedclass__': cls,
                  '__draftwrappedparam__': ([], {})}
                  
                  
    # instantiate custom draft class              
    draft_class = type(class_name, base_class, attributes)
    
    # set attributes
    #setattr(draft_class, '__draftwrappedclass__', cls)
    #setattr(draft_class, '__draftwrappedparam__', ([], {}))

    if DEBUG:
        print('Create draft:')
        print('    class_name: {}'.format(class_name))
        print('    base_class: {}'.format(base_class))
        print('    repr: {}'.format(repr(draft_class)))
    
    return draft_class
    
    
class _DraftMeta(abc.ABCMeta):
    '''
    _DraftMeta
    
    The metaclass for _Draft
    '''
    
    def __repr__(cls):
        '''
        __repr__ sample: <class 'Draft(__main__.A)'>
        '''

        if cls.__draftwrappedclass__ is not None:
            return '<class \'{}({}.{})\'>'.format(cls.__name__, 
                                        cls.__draftwrappedclass__.__module__,
                                        cls.__draftwrappedclass__.__name__)
        else:
            return '<class \'{}(None)\'>'.format(cls.__name__)


class _Draft(metaclass=_DraftMeta):
    '''
    _Draft
    
    The raw class of Draft
    
    Used by Draft and _draft_factory
    '''

    __draftwrappedclass__ = None     # class attribute
    __draftwrappedparam__ = None     # instance attribute

    def __new__(cls, *args, **kwargs):
        inst = super(_Draft, cls).__new__(cls)

        inst.__draftwrappedparam__ = ([], {})

        return inst
    
    def __init__(self, *args, **kwargs):
        # initialize instance attributes
        self.__draftwrappedparam__ = (args, kwargs)
    
    def __call__(self):
        '''
        Same as __instantiate__
        '''
        return self.__instantiate__()

    def __instantiate__(self):
        '''
        Interface to instantiate an anonymous object

        Call class.__new__
        '''
        args, kwargs = self.__draftwrappedparam__
        inst = self.__draftwrappedclass__(*args, **kwargs)

        return inst



class _default:
    '''Default key'''
    def __str__(self):
        return 'default'

    
class Draft(_Draft):
    '''
    Draft

    A class wrapper. With this wrapper, you can predefine your class instance
    without actually create one. After that, you can call Draft.instantiate() 
    to create one.

    Notice that isinstance/issubclass can check inside the Draft, which means
    the wrapped class will also be checked.

    Attributes:
        __draftwrappedclass__:
        __draftwrappedparam__:
        default:
    

    Example usage:

    >>> @Draft
    ... class A():
    ...     def __init__(self, x, y, z):
    ...         self.args = (x, y, z)

    >>> draft_a = A(1, 2, 3)
        
    >>> isinstance(draft_a, Draft) # True
    >>> isinstance(draft_a, A)     # also True, this behavior is affected by DraftMeta.

    >>> a = draft_a.instantiate()

    >>> isinstance(a, Draft)       # False
    >>> isinstance(a, A)           # True
    '''

    default = _default

    __instancedict__ = None

    def __new__(cls, *args, **kwargs):
        inst = super(Draft, cls).__new__(cls, *args, **kwargs)

        # create attribute
        setattr(inst, '__instancedict__', OrderedDict())

        return inst


    def __init__(self, cls):
        # initialize instance attributes
        self.__draftwrappedclass__ = cls
        
        
    def __call__(self, *args, **kwargs):
        '''
        Initialize parameters
        '''
        # set params
        super(Draft, self).__init__(*args, **kwargs)

        return self

    def __repr__(self):
        '''
        __repr__ sample: <Draft '__main__.A'>
        '''

        class_repr = repr(self.__draftwrappedclass__)

        if class_repr == type.__repr__(self.__draftwrappedclass__):
            return class_repr.replace('<class', '<{}'.format(self.__class__.__name__))
        else:
            return '<{}: '.format(self.__class__.__name__) + class_repr + '>'

    def __len__(self):
        '''
        Count number of instances
        '''
        return len(self.__instancedict__)

    def __getitem__(self, key=_default):
        '''
        Get instance by key
        '''
        return self.instance(key)

    def __contains__(self, item):
        '''
        Whether containing instance (not key!!!!)
        '''
        return item in self.__instancedict__.values()
    
    def __instantiate__(self, *args, **kwargs):
        '''
        Interface to instantiate an anonymous object

        Call class.__new__

        This function is overwritten by the _draft_factory
        '''

        inst = self.__draftwrappedclass__(*args, **kwargs)

        setattr(inst, '__instancename__', None)

        return inst
    

    def instantiate(self, key=_default, ignore=True):
        '''
        Instantiate an object from predefined parameters
        
        Args:
            key: (hashable object, e.g. int, str)
            ignore: (bool) ignore instance already exists error
        '''
        
        # make new instance
        if key not in self.__instancedict__:
            # get params
            args, kwargs = self.__draftwrappedparam__
            
            # make instance 
            inst = self.__instantiate__(*args, **kwargs)
            
            # set instance name
            setattr(inst, '__instancename__', key)
            # set original draft
            setattr(inst, '__draft__', self)

            self.__instancedict__[key] = inst
            
        else:
            if not ignore:
                raise RuntimeError('Key condlict! The instance of {} for key {} '\
                            'already exists'.format(self.__draftwrappedclass__, key))
                
        return self.__instancedict__[key]
        
    def instance(self, key=_default):
        '''
        Get instance by key (same as __getitem__)
        '''
        
        if key not in self.__instancedict__:
            raise RuntimeError('The instance of {} for key {} does not exist'.format(
                                self.__draftwrappedclass__, key))
                                
        return self.__instancedict__[key]
        

_BASEDRAFT = Draft

def get_baseclass():
    return _BASEDRAFT

def set_baseclass(draft):
    global _BASEDRAFT
    assert issubclass(draft, Draft), 'draft must inherit from Draft'
    _BASEDRAFT = draft
        

'''
=======================================
=        DraftMeta, Draftable         =
=======================================
'''
        
class DraftMeta(abc.ABCMeta):

    '''
    DraftMeta

    A meta class for Draftable class. The custom Draft class (a subclass of Draft) for 
    those subclasses inherited from this meta class is created and assigned to the 
    subclass.__draftclass__.

    Notice that isinstance/issubclass will check inside the Draft class, which means the 
    original class wrapped by Draft will also be examinated.


    Example usage:

        DO NOT USE THIS CLASS DIRECTLY. Please inherit from Draftable.

    >>> class MyModule(Draftable):
    ...     def __init__(self, inputs):
    ...         pass

    '''

    def __new__(_cls, name, bases, namespace, **kwargs):
    
        cls = super().__new__(_cls, name, bases, namespace, **kwargs)
        setattr(cls, '__draftclass__', _draft_factory(cls))
        
        return cls
        
    def __instancecheck__(cls, instance):

        if isinstance(instance, _Draft): # Draft vs Draftable
            return False
            
        return super().__instancecheck__(instance)

    def __subclasscheck__(cls, subclass):
    
        if issubclass(subclass, _Draft):
            inner_class_check = super().__subclasscheck__(subclass.__draftwrappedclass__)
        else:
            inner_class_check = False
            
        return inner_class_check or super().__subclasscheck__(subclass)



class Draftable(metaclass=DraftMeta):
    '''
    Draftable

    A wrapper class, but actually, this class is only responsible for wrapping the original class 
    using Draft class predefined and stored in __draftclass__ by DraftMeta. This class doesn't 
    store any parameters for constructing the instance. Just wrapping something on the original 
    class in the instance creation time. The params are passed when calling 
    __draftclass__.__instantiate__, and an instance of the original class will be created.

    Attributes:
        __draft__: The original draft that instantiate the instance
        __instancename__: The instance name (key) to instantiate

    Main interfaces:
        __new__: Create new draft instance using __draftclass__ attached on the original class.
        __init__: Do nothing
        __instantiate__: Instantiate a new instance of the original class.
    '''

    __draft__ = None
    __instancename__ = None
    
    def __new__(cls, *args, **kwargs):
    
        if not hasattr(cls, '__draftclass__'):
            raise RuntimeError(('The class inherited from Draftable does not contain __draftclass__ attribute.'
                                ' Please do not overwrite __metaclass__ attribute of the class.'))
        
        # create draft using __draftclass__
        draft = cls.__draftclass__(*args, **kwargs)

        return draft
        
    def __init__(self, *args, **kwargs):
        '''
        Do nothing
        '''
        pass

    @classmethod
    def __instantiate__(cls, *args, **kwargs):
        '''
        Instantiate a new instance, same as the original __new__ function
        '''
        inst = super(Draftable, cls).__new__(cls)

        # create instance attributes
        setattr(inst, '__instancename__', cls.__instancename__)
        setattr(inst, '__draft__', cls.__draft__)
        
        inst.__init__(*args, **kwargs)

        return inst



def Instantiate(draft, key=Draft.default, ignore=True):
    if isinstance(draft, Draft):
        inst = draft.instantiate(key, ignore)
    else:
        inst = draft
    
    return inst


def is_draft(obj, _class=None):
    '''
    If _class is None, check if the given object is an instance of BaseDraft.
    Else, check if the given object is a draft of the given class.
    '''

    if _class is None:
        # check if the object is an instance of base draft class
        return isinstance(obj, get_baseclass())
    else:
        # check if the object is an draft of the main class
        return (hasattr(obj, '__draftwrappedclass__') and obj.__draftwrappedclass__ is _class)

def is_subdraft(obj, subclass=None):
    '''
    If subclass is None, check if the given object is an instance of BaseDraft.
    (This feature is exactly the same as is_draft)
    Else, check if the given object is a draft or sub-draft of the given class.
    '''

    if subclass is None:
        # check if the object is an instance of base draft class
        return isinstance(obj, get_baseclass())
    else:
        # check if the object is an draft of the main class
        return (hasattr(obj, '__draftwrappedclass__') and issubclass(obj.__draftwrappedclass__, subclass))


if __name__ == '__main__':
    
    class A(Draftable):
        def __init__(self, name):
            super(A, self).__init__()
            self.name = name

        def introduce(self):
            return 'My name is {}.'.format(self.name)

    class B(A):
        def __init__(self, gender, name):
            super(B, self).__init__(name)
            self.gender = gender

        def introduce(self):
            return super(B, self).introduce() + ' I\'m a {}.'.format(self.gender)

    
    print('Print A:', A)
    print('Print B:', B)

    assert issubclass(A, Draftable), 'A is not a subclass of Draftable'
    assert issubclass(B, Draftable), 'B is not a subclass of Draftable'

    print('Stage 1: clear')

    draft_a = A(name='Ending2015a')
    draft_b = B(gender='boy', name='Ending2015a')
    
    print('type(draft_a):', type(draft_a))
    print('type(draft_b):', type(draft_b))
    print('draft_a:', draft_a)
    print('draft_b:', draft_b)

    assert not isinstance(draft_a, Draftable), 'draft_a is an instance of Draftable'
    assert not isinstance(draft_b, Draftable), 'draft_b is an instance of Draftable'
    assert not isinstance(draft_a, A), 'draft_a is an instance of A'
    assert not isinstance(draft_b, B), 'draft_b is an instance of B'
    assert not isinstance(draft_a, B), 'draft_a is an instance of B'
    assert not isinstance(draft_b, A), 'draft_b is an instance of A'
    assert isinstance(draft_a, Draft), 'draft_a is not an instance of Draft'
    assert isinstance(draft_b, Draft), 'draft_b is not an instance of Draft'

    assert issubclass(type(draft_a), Draftable), 'type(draft_a) is not a subclass of Draftable'
    assert issubclass(type(draft_b), Draftable), 'type(draft_b) is not a subclass of Draftable'
    assert issubclass(type(draft_a), A), 'type(draft_a) is not a subclass of A'
    assert issubclass(type(draft_b), B), 'type(draft_b) is not a subclass of B'
    assert issubclass(type(draft_b), A), 'type(draft_b) is not a subclass of A'
    assert issubclass(type(draft_a), Draft), 'type(draft_a) is not a subclass of Draft'
    assert issubclass(type(draft_b), Draft), 'type(draft_b) is not a subclass of Draft'

    print('Stage 2: Clear')

    a = Instantiate(draft_a)
    b = Instantiate(draft_b)

    print('type(a):', type(a))
    print('type(b):', type(b))
    print('a:', a)
    print('b:', b)

    assert isinstance(a, Draftable), 'a is not an instance of Draftable'
    assert isinstance(b, Draftable), 'b is not an instance of Draftable'
    assert isinstance(a, A), 'a is not an instance of A'
    assert isinstance(b, B), 'b is not an instance of B'
    assert not isinstance(a, B), 'a is an instance of B'
    assert isinstance(b, A), 'b is not an instance of A'
    assert not isinstance(a, Draft), 'a is an instance of Draft'
    assert not isinstance(b, Draft), 'b is an instance of Draft'

    assert issubclass(type(a), Draftable), 'type(a) is not a subclass of Draftable'
    assert issubclass(type(b), Draftable), 'type(b) is not a subclass of Draftable'
    assert issubclass(type(a), A), 'type(a) is not a subclass of A'
    assert issubclass(type(b), B), 'type(b) is not a subclass of B'
    assert not issubclass(type(a), B), 'type(a) is a subclass of B'
    assert issubclass(type(b), A), 'type(b) is not a subclass of A'
    assert not issubclass(type(a), Draft), 'type(a) is a subclass of Draft'
    assert not issubclass(type(b), Draft), 'type(b) is a subclass of Draft'

    print('Stage 3: Clear')

    assert not is_draft(A), 'A is a draft'
    assert not is_draft(B), 'B is a draft'
    assert is_draft(draft_a), 'draft_a is not a draft'
    assert is_draft(draft_b), 'draft_b is not a draft'
    assert not is_draft(a), 'a is a draft'
    assert not is_draft(b), 'b is a draft'

    assert is_draft(draft_a, A), 'draft_a is not a draft of A'
    assert is_draft(draft_b, B), 'draft_b is not a draft of B'
    assert not is_draft(draft_a, B), 'draft_a is a draft of B'
    assert not is_draft(draft_b, A), 'draft_b is a draft of A'

    assert is_subdraft(draft_a, A), 'draft_a is not a sub-draft of A'
    assert is_subdraft(draft_b, B), 'draft_b is not a sub-draft of B'
    assert not is_subdraft(draft_a, B), 'draft_a is a sub-draft of B'
    assert is_subdraft(draft_b, A), 'draft_b is a sub-draft of A'

    assert not is_draft(a, A), 'a is a draft of A'
    assert not is_draft(b, B), 'b is a draft of B'
    assert not is_draft(a, B), 'a is a draft of B'
    assert not is_draft(b, A), 'b is a draft of A'

    assert not is_draft(a, draft_a), 'a is a draft of draft_a'
    assert not is_draft(b, draft_b),'b is a draft of draft_b'
    assert not is_draft(a, draft_b), 'a is a draft of draft_b'
    assert not is_draft(b, draft_a),'b is a draft of draft_a'

    print('Stage 4: Clear')