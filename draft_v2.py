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
Some attributes:

    __draftclass__: The draft class wrapping the original class. Attached on the original 
        class inherited from BaseDraft by DraftMeta in DraftMeta.__new__.
    __draftwrappedclass__: The original class which is wrapped by draft class. Attached on 
        the draft class. 
    __draftwrappedparam__: The parameters to instantiate an instance of the original class.
        Attached on the draft class.
    __instantiate__: The constructor to instantiate a new object from draft classes. 
        Attached by inheriting from BaseDraft.
    __instancename__: The name (key) of the instance.

'''


__all__ = [
    'Draft',
    'BaseDraft',
    'Instantiate',
]

DEBUG = True


def Instantiate(draft, key='d', ignore=True):
    if isinstance(draft, Draft):
        return draft.instantiate(key, ignore)
        
    elif isinstance(draft, _Draft):


def _draft_factory(cls):
    '''
    _darft_factory
    
    Create a custom Draft class for given cls
    
    Args:
        cls: Class
    '''
    
    # make class name
    if (cls.__name__[0].isupper() or
            (not cls.__name__[0].isalpha())):
        class_name = 'Draft'
    else:
        class_name = 'Draft_'
        
    class_name = class_name + cls.__name__
    base_class = (_Draft, )
    
    # Custom function for custom Draft
    def __init__(self, *args, **kwargs):
        
        # call super
        _Draft.__init__(self)
        # save params
        self.__draftwrappedparam__ = (args, kwargs)
        
    def __repr__(self):
    
        draft_repr = '<Draft: '
        class_repr = repr(self.__class__.__draftwrappedclass__)
        
        if class_repr.startswith('<'):
            return class_repr.replace('<', draft_repr, 1)
        else:
            return draft_repr + class_repr + '>'
    
    # build attributes dictionary
    attributes = {'__init__': __init__,
                  '__repr__': __repr__,
                  '__draftwrappedclass__', cls,
                  '__draftwrappedparam__', ([], {})}
                  
                  
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
    
        draft_repr = '<Draft: '
        class_repr = repr(cls.__draftwrappedclass__)
        
        if class_repr.startswith('<'):
            return class_repr.replace('<', draft_repr, 1)
        else:
            return draft_repr + class_repr + '>'


class _Draft(metaclass=_DraftMeta):
    '''
    _Draft
    
    The base class of _Draft
    
    Used by Draft and _draft_factory
    '''

    __draftwrappedclass__ = None
    __draftwrappedparam__ = ([], {})
    
    def __init__(self):
        # create attributes
        self.__draftwrappedclass__ = self.__class__.__draftwrappedclass__
        self.__draftwrappedparam__ = self.__class__.__draftwrappedparam__
        
        self._instance_dict = OrderedDict()
    
    @abc.abstractmethod
    def __instantiate__(self, *args, **kwargs):
        '''
        Interface for instantiating new objects
        '''
        pass

    
class Draft(_Draft):
    '''
    Draft

    A class wrapper. With this wrapper, you can predefine your class instance
    without actually create one. After that, you can call Draft.instantiate() 
    to create one.

    Notice that isinstance/issubclass can check inside the Draft, which means
    the wrapped class will also be checked.

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
    
    #_Draft.__draftwrappedclass__
    #_Draft.__draftwrappedparam__
    
    def __init__(self, cls):
        super(Draft, self).__init__()
        
        # create attributes
        self.__draftwrappedclass__ = cls
        self.__draftwrappedparam__ = self.__class__.__draftwrappedparam__
        
        
    def __call__(self, *args, **kwargs):
        # set params
        self.__draftwrappedparam__ = (args, kwargs)

        return self
        
    def __repr__(self):
        # make repr
        draft_repr = '<{}( '.format(self.__class__.__name__)
        class_repr = repr(self.__draftwrappedclass__)
        
        if class_repr.startswith('<'):
            return class_repr.replace('<', draft_repr, 1)
        else:
            return draft_repr + class_repr + ' )>'
    
    def instantiate(self, key='d', ignore=True):
        '''
        instantiate an object from predefined parameters
        
        Args:
            key: (hashable object, e.g. int, str)
            ignore: ignore instance already exists error
        '''
        
        # make new instance
        if key not in self._instance_dict:
            # get params
            args, kwargs = self.__draftwrappedparam__
            
            # make instance 
            self._instance_dict[key] = self.__draftwrappedclass__(*args, **kwargs)
            
            # set instance name
            setattr(self._instance_dict[key], '__instancename__', key)
            
        else:
            if not ignore:
                raise RuntimeError('Key condlict! The instance of {} for key {} '\
                            'already exists'.format(self.__draftwrappedclas__, key))
                
        return self._instance_dict[key]
        
    def instance(self, key='d'):
        '''
        Get instance by key
        '''
        
        if key not in self._instance_dict:
            raise RuntimeError('The instance of {} for key {} does not exist'.format(
                                self._inner_class, key))
                                
        return self._instance_dict[key]
        
        
'''
        
# only those classes inherited from BaseDraft have __instantiate__ function.
            #      self.__draftwrappedclass__.__instantiate__(*args, **kwargs)
            if hasattr(self.__draftwrappedclass__, '__instantiate__'):
                self._instance_dict[key] = self.__draftwrappedclass__.__instantiate__(*args, **kwargs)
            else:
'''               
        
        
class DraftMeta(abc.ABCMeta):

    '''
    DraftMeta

    A meta class for BaseDraft class. The custom Draft class (a subclass of Draft) for 
    those subclasses inherited from this meta class is created and assigned to the 
    subclass.__draftclass__.

    Notice that isinstance/issubclass will check inside the Draft class, which means the 
    original class wrapped by Draft will also be examinated.


    Example usage:

        DO NOT USE THIS CLASS DIRECTLY. Please inherit from BaseDraft.

    >>> class MyModule(BaseDraft):
    ...     def __init__(self, inputs):
    ...         pass

    '''

    def __new__(_cls, name, bases, namespace, **kwargs):
    
        cls = super(DraftMeta, _cls).__new__(_cls, name, bases, namespace, **kwargs)
        setattr(cls, '__draftclass__', _draft_factory(cls))
        
        return cls
        
    def __instancecheck__(cls, instance):
    
        if isinstance(instance, _Draft):
            inner_class_check = super(abc.ABCMeta, cls).__subclasscheck__(instance.__draftwrappedclass__)
        else:
            inner_class_check = False
            
        return inner_class_check or super(abc.ABCMeta, cls).__instancecheck__(instance)

    def __subclasscheck__(cls, subclass):
    
        if issubclass(subclass, _Draft):
            inner_class_check = super(abc.ABCMeta, cls).__subclasscheck__(subclass.__draftwrappedclass__)
        else:
            inner_class_check = False
            
        return inner_class_check or super(abc.ABCMeta, cls).__subclasscheck__(subclass)



class Draftable(metaclass=DraftMeta):
    '''
    Draftable

    A wrapper class, but actually, this class is only responsible for wrapping the original class 
    using Draft class predefined and stored in __draftclass__ by DraftMeta. This class doesn't 
    store any parameters for constructing the instance. Just wrapping something on the original 
    class in the instance creation time. The params are passed when calling 
    __draftclass__.__instantiate__, and an instance of the original class will be created.

    Functions:
        __new__: Create new draft instance using __draftclass__ attached on the original class.
        __init__: Do nothing
        __instantiate__: Instantiate a new instance of the original class.
    '''
    
    __instancename__ = None
    
    def __new__(cls, *args, **kwargs):
    
        if not hasattr(cls, '__draftclass__'):
            raise RuntimeError(('The class inherited from BaseDraft does not contain __draftclass__ attribute.'
                                ' Please do not overwrite __metaclass__ attribute of the class.'))
        
        # create draft using __draftclass__
        draft = cls.__draftclass__(*args, **kwargs)

        return draft
        
    def __init__(self, *args, **kwargs):
        '''
        Do nothing
        '''
        pass
        
    def __repr__(self):
        draft_repr = '{}[{!r}]'.format(self.__class__.__draftclass__.__name__, self.__instancename__)
        module = self.__class__.__module__
        qualname = self.__class__.__qualname__

        return "<{}: {}.{} object at {}>".format(draft_repr, module, qualname, hex(id(self)))


    @classmethod
    def __instantiate__(cls, *args, **kwargs):
        ins = super(Draftable, cls).__new__(cls)
        ins.__init__(*args, **kwargs)
        
        self.__instancename__ = self.__class__.__instancename__
        
        return ins



#Draft/_Draft
draft_a = A() #Draftable
#Draftable
a = draft_a.instantiate()
isinstance(draft_a, A) #True
isinstance(draft_a, Draft) #True
isinstance(a, A) #True
isinstance(a, Draft) #False

issubclass(type(draft_a), A) #True
issubclass(type(draft_a), Draft) #True
issubclass(type(a), A)  #True
issubclass(type(a), Draft) #False
