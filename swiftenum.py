import enum

class SwiftEnum(tuple, enum.Enum):
    def __new__(cls, clsargs):
        value = len(cls.__members__) + 1
        def func(*args):
            if len(args) != len(clsargs):
                raise TypeError('{}.{}() takes {} arguments ({} given)'.format(
                    cls.__name__,
                    func._name_,
                    len(clsargs),
                    len(args)))
            obj = tuple.__new__(cls, args)
            obj._value_ = value
            obj._name_ = func._name_
            return obj
        func._value_ = func.value = value
        return func
    def __str__(self):
        return '{}.{}({})'.format(type(self).__name__,
                                  self.name,
                                  ', '.join(map(repr, self)))
    __repr__ = __str__
    def __hash__(self, other):
        return hash((self._name_, tuple.__hash__(self)))
    def __eq__(self, other):
        return (tuple.__eq__(self, other) and
                type(self) == type(other) and
                self._name_ == other._name_)
