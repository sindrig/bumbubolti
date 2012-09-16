from django.db import models

class ScoreField(models.Field):
    description = 'Holds the score for a match'
    __metaclass__ = models.SubfieldBase
    def db_type(self, connection):
        return 'char(10)'
        
    def to_python(self, value):
        if isinstance(value, tuple):
            return value
        return tuple([int(val) for val in value.split('-')])
        
    def get_prep_value(self, value):
        if len(value) != 2 or not all([isinstance(val, int) or isinstance(val, 
                    (str, unicode)) and val.isdigit() for val in value]):
            raise ValidationError('Value has to be a list/tuple of length 2 containing only digits: ("%s")'%repr(value))
        return '-'.join([str(val) for val in value])