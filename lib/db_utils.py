import sqlalchemy.types as types


class ChoiceType(types.TypeDecorator):
    # https://stackoverflow.com/questions/6262943/sqlalchemy-how-to-make-django-choices-using-sqlalchemy

    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]
