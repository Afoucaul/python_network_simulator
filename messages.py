import ast


ENCODING = 'ascii'


class Field:
    def __init__(self, name, valueType):
        self.name = name
        self.valueType = valueType

    def expand(self, value):
        if self.valueType is list:
            return ast.literal_eval(str(value, ENCODING))
        else:
            return self.valueType(value)


class Message:
    types = {}

    def __init__(self, *args):
        for i, value in enumerate(args):
            self.__setattr__(self.fields[i].name, value)

    def __bytes__(self):
        data = "{}".format(type(self).__name__)
        for it_field in self.fields:
            data += ';'
            data += str(self.__getattribute__(it_field.name))

        return bytes(data, ENCODING)

    @classmethod
    def register(cls, newClass):
        cls.types[newClass.__name__] = newClass
        return newClass

    @classmethod
    def to_object(cls, data):
        splitted = data.split(b';')
        messageType = cls.types[str(splitted[0], ENCODING)]

        if messageType.__init__ is not cls.__init__:
            messageObject = messageType(
                *[messageType.fields[i].expand(value)
                  for i, value in enumerate(splitted[1:])])
        else:
            messageObject = messageType()
            for i, value in enumerate(splitted[1:]):
                messageObject.__setattr__(
                    messageType.fields[i].name,
                    messageType.fields[i].expand(value))

        return messageObject


@Message.register
class NewSlaveMessage(Message):
    fields = (Field('port', int),)


@Message.register
class NodeListMessage(Message):
    fields = (Field('ports', list),)


@Message.register
class SlaveLeftMessage(Message):
    fields = (Field("port", int),)


def make(data):
    return Message.to_object(data)
