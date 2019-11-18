# --- built in ---
import os
import abc
import sys
import time
import logging

# --- 3rd party ---
# --- my module ---

'''
Some attributes:

    __draftclass__: The draft class wrapping the original class. Attached on the original class inherited from BaseDraft by DraftMeta in DraftMeta.__new__.
    __draftwrappedclass__: The original class wrapped by draft class. Attached on the draft class. 
    __instantiate__: The constructor to instantiate a new object from draft classes. Attached on the original class inherited from BaseDraft.

'''


class Draft():
    '''
    Draft

    A class wrapper. With this wrapper, you can predefine your class instance
    without actually create one. After that, you can call Draft.instantiate() 
    to create one.

    Notice that, 

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

    def __init__(self, cls):
        self._inner_class = cls
        self._instances_dict = OrderedDict()
        self._inst_params = ([], {})

    def __call__(self, *args, **kwargs):
        self._inst_params = (args, kwargs)

        return self

    # === properties ===

    @property
    def __draftwrappedclass__(self):
        return self._inner_class

    @property
    def __draftparams__(self):
        return self._inst_params

    def instantiate(self, key='default', ignore=True):
        '''
        instantiate an predefined object

        Args:
            key: (hashable object, e.g. int, str)
            ignore: ignore instance not exist error
        '''

        if key not in self._instances_dict:
            args, kwargs = self._inst_params
            self._instances_dict[key] = self._inner_class.__instantiate__(*args, **kwargs)
        else:
            if not ignore:
                raise RuntimeError("Key condlict! The instance of {} for key {} already exists".format(self._inner_class, key))


        return self._instances_dict[key]

    def instance(self, key='default'):
        '''
        Get instance by key
        '''
        if key not in self._instances_dict:
            raise RuntimeError('The instance of {} for key {} does not exist'.format(self._inner_class, key))

        return self._instances_dict[key]



class DraftMeta(abc.ABCMeta):
    '''
    DraftMeta

    A meta class for Draft class
    '''

    def __new__(_cls, name, bases, namespace, **kwargs):
        cls = super(DraftMeta, _cls).__new__(name, bases, namespace, **kwargs)
        cls.__draftclass__ = DraftFactory(cls)

    def __instancecheck__(cls, instance):

        if isinstance(instance, Draft):
            inner_class_check = super(abc.ABCMeta, cls).__subclasscheck__(instance.__draftwrappedclass__)
        else:
            inner_class_check = False

        return inner_class_check or super(abc.ABCMeta, cls).__instancecheck__(instance)


    def __subclasscheck__(cls, subclass):

        if issubclass(subclass, Draft) and hasattr(subclass, __wrapped__):
            subclass.__wrapped__


class BaseDraft():
    '''
    BaseDraft

    A class wrapper, but actually, this class is only responsible for wrapping the origin class using the 
    draft class predefined in the __draftclass__, neither storing the params like a container, nor acting
    as a wrapper class. Just wrapping something on the original class in creation time. The params are
    passed when __draftclass__ call __instantiate__, and an instance of original class will be created.

    Functions:
        __new__: Create new draft instance using __draftclass__ attached on the original class.
        __init__: Do nothing
        __instantiate__: Instantiate a new instance of the original class.
    '''
    __metaclass__ = DraftMeta

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

    def __instantiate__(self, *args, **kwargs):
        
        pass


class A(BaseDraft):
    def __init__(self, name):
        super(BaseDraft, self).__init__()
        self.name = name

    def introduce(self):
        return 'My name is {}.'.format(name)


class B(A):
    def __init__(self, gender, name):
        super(A, self).__init__(name)
        self.gender = gender

    def introduce(self):
        return super(A, self).introduce() + 'I\'m a {}.'.format(self.gender)





if __name__ == '__main__':
    print('=== A ===')
    draft_a = A(name='joehsiao')
    a = draft_a.intantiate()
    print(a.introduce())

    print('\n=== B ===')
    draft_b = B(gender='boy', name='joehsiao')
    b = draft_b.instantiate()
    print(b.introduce())