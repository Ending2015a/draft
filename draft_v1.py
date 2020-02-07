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
    'BaseDraft',        
]

def _draft_factory(cls):
    
    if cls.__name__[0].isupper() or (not cls.__name__[0].isalpha()):
        class_name = 'Draft'
    else:
        class_name = 'Draft_'

    class_name = class_name + cls.__name__
    base_class = (Draft, )

    # instantiate draft
    def __init__(self, *args, **kwargs):
        Draft.__init__(self)
        Draft.__call__(self, *args, **kwargs)

    def __repr__(self):
        draft_repr = '<Draft: '
        if repr(cls).startswith('<'):
            return repr(cls).replace('<', draft_repr, 1)
        else:
            return draft_repr + repr(cls) + '>'

    attributes = {'__init__': __init__,
                  '__repr__': __repr__}

    draft_class = type(class_name, base_class, attributes)
    setattr(draft_class, '__draftwrappedclass__', cls)
    setattr(draft_class, '__draftwrappedparam__', ([], {}))

    print('create draft:')
    print('    class_name: {}'.format(class_name))
    print('    base_class: {}'.format(base_class))
    print('    repr: {}'.format(repr(draft_class)))


    return draft_class


class Draft():
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

    __draftwrappedclass__ = None
    __draftwrappedparam__ = ([], {})

    def __init__(self, cls=None):

        dcls = type(self).__draftwrappedclass__
        cls = cls if dcls is None else dcls
        assert cls is not None, 'The cls must not be None'

        self.__draftwrappedclass__ = cls
        self.__draftwrappedparam__ = type(self).__draftwrappedparam__
        self._instance_dict = OrderedDict()


    def __call__(self, *args, **kwargs):
        self.__draftwrappedparam__ = (args, kwargs)

        return self

    # === properties ===

    def instantiate(self, key='default', ignore=True):
        '''
        instantiate an predefined object

        Args:
            key: (hashable object, e.g. int, str)
            ignore: ignore instance not exist error
        '''

        if key not in self._instance_dict:
            args, kwargs = self.__draftwrappedparam__
            self._instance_dict[key] = self.__draftwrappedclass__.__instantiate__(*args, **kwargs)
            setattr(self._instance_dict[key], '__instancename__', key)

        else:
            if not ignore:
                raise RuntimeError("Key condlict! The instance of {} for key {} already exists".format(self._inner_class, key))


        return self._instance_dict[key]

    def instance(self, key='default'):
        '''
        Get instance by key
        '''
        if key not in self._instance_dict:
            raise RuntimeError('The instance of {} for key {} does not exist'.format(self._inner_class, key))

        return self._instance_dict[key]



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

        print('in DraftMeta: create new class: {}'.format(name))

        cls = super(DraftMeta, _cls).__new__(_cls, name, bases, namespace, **kwargs)
        cls.__draftclass__ = _draft_factory(cls)

        return cls

    def __instancecheck__(cls, instance):

        if isinstance(instance, Draft):
            inner_class_check = super(abc.ABCMeta, cls).__subclasscheck__(instance.__draftwrappedclass__)
        else:
            inner_class_check = False

        return inner_class_check or super(abc.ABCMeta, cls).__instancecheck__(instance)


    def __subclasscheck__(cls, subclass):

        if issubclass(subclass, Draft) and hasattr(subclass, __wrapped__):
            subclass.__wrapped__
            #TODO: complete subclass check


class BaseDraft(metaclass=DraftMeta):
    '''
    BaseDraft

    A class wrapper, but actually, this class is only responsible for wrapping the origin class using the 
    draft class predefined and stored in __draftclass__, neither storing the params like a container, nor 
    acting as a wrapper class. Just wrapping something on the original class in the instance creation time. 
    The params are passed when calling __draftclass__.__instantiate__, and an instance of the original 
    class will be created.

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
        draft_repr = '{}[{!r}]'.format(type(self).__draftclass__.__name__, self.__instancename__)
        module = type(self).__module__
        qualname = type(self).__qualname__

        return "<{}: {}.{} object at {}>".format(draft_repr, module, qualname, hex(id(self)))

    @classmethod
    def __instantiate__(cls, *args, **kwargs):
        ins = super(BaseDraft, cls).__new__(cls)        
        ins.__init__(*args, **kwargs)

        setattr(ins, '__instancename__', None)

        return ins
        



if __name__ == '__main__':


    class A(BaseDraft):
        def __init__(self, name):
            super(BaseDraft, self).__init__()
            self.name = name

        def introduce(self):
            return 'My name is {}.'.format(self.name)


    class B(A):
        def __init__(self, gender, name):
            super(B, self).__init__(name)
            self.gender = gender

        def introduce(self):
            return super(B, self).introduce() + ' I\'m a {}.'.format(self.gender)


    print(A)
    print(B)

    print('=== A ===')
    draft_a = A(name='joehsiao')
    print('draft_a repr: {}'.format(repr(draft_a)))
    a = draft_a.instantiate()
    print('a repr: {}'.format(repr(a)))
    print(a.introduce())

    print('\n=== B ===')
    draft_b = B(gender='boy', name='joehsiao')
    print('draft_b repr: {}'.format(repr(draft_b)))
    b = draft_b.instantiate()
    print('b repr: {}'.format(repr(b)))
    print(b.introduce())
