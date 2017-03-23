# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division

id2obj = {}


class DictObject(dict):
    def __init__(self, seq=None, **kwargs):
        super(DictObject, self).__init__(seq or (), **kwargs)

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError('"{}" object has no attribute "{}"'.format(self.__class__.__name__, name))

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError('"{}" object has no attribute "{}"'.format(self.__class__.__name__, name))


def objectify(o):
    try:
        return _objectify(o)
    finally:
        id2obj.clear()


def _objectify(o):
    id_ = id(o)
    if id_ not in id2obj:
        if isinstance(o, Entity):
            id2obj[id_] = o
        elif isinstance(o, DictObject):
            key = o.pop('_key_', None)
            id2obj[id_] = Entity(o, key=key) if key else o
        elif isinstance(o, dict):
            key = o.pop('_key_', None)
            if key:
                id2obj[id_] = Entity(((k, _objectify(v)) for k, v in o.items()), key=key)
            else:
                id2obj[id_] = DictObject((k, _objectify(v)) for k, v in o.items())
        elif isinstance(o, (tuple, set, list)):
            id2obj[id_] = o.__class__(_objectify(e) for e in o)
        else:
            id2obj[id_] = o
    return id2obj[id_]


class Entity(DictObject):
    KEY = ('id', )

    def __init__(self, seq=None, key=None, **kwargs):
        if key is None:
            key_ = self.__class__.KEY
        else:
            if isinstance(key, basestring):
                key_ = (key, )
            else:
                key_ = tuple(key)
            if key_ == self.__class__.KEY:
                key_ = self.__class__.KEY
        super(Entity, self).__init__(seq, _key_=key_, **kwargs)
        if all(getattr(self, attr_name, None) is None for attr_name in self._key_):
            raise Exception('{} does not have any of {}'.format(self, self._key_))

    @classmethod
    def serialize(cls, **kwargs):
        kwargs.pop('_hash', None)
        return kwargs

    @classmethod
    def deserialize(cls, **kwargs):
        return cls(**kwargs)

    def clone(self, **overridden_attributes):
        serialized = self.serialize(**dict(self, **overridden_attributes))
        return self.deserialize(**serialized)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return all(getattr(self, attr_name) == getattr(other, attr_name) for attr_name in self._key_)

    def __hash__(self):
        if not self.get('_hash'):
            self._hash = hash(tuple(self.get(attr_name) for attr_name in self._key_))
        return self._hash

    def __repr__(self):
        return '<{}: {}>'.format(type(self).__name__, ', '.join('{}={}'.format(attr_name, getattr(self, attr_name, None)) for attr_name in self._key_))
