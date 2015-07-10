import csv

import phonenumbers as pn
import dateutil.parser as dateutil


DEFAULT_REGION = 'US'


def normalize_phonenumber(phonenumber):
    phonenumber = str(phonenumber)

    try:
        numobj = pn.parse(phonenumber)
    except pn.NumberParseException:
        numobj = pn.parse(phonenumber, DEFAULT_REGION)

    return '{code}{national_num}'.format(
        code=numobj.country_code, national_num=numobj.national_number)


def normalize_datetime(datestring):
    dateobj = dateutil.parse(datestring)
    return dateobj.replace(microsecond=0, tzinfo=None).isoformat()


def normalize_message(message):
    pass


class RecordType(object):
    sender_index = 0
    receiver_index = 1
    datetime_index = 2
    id_index = 3
    message_index = slice(4, None)

    def __init__(self, data):
        self.data = data

    def _phonenumber(self, index):
        number = self.data[index]
        return normalize_phonenumber(number)

    def _datetime(self):
        return normalize_datetime(self.data[self.datetime_index])

    @property
    def datetime(self):
        return self._datetime()

    def _id(self):
        return self.data[self.id_index]

    @property
    def id(self):
        return self._id()

    def _sender(self):
        return self._phonenumber(self.sender_index)

    @property
    def sender(self):
        return self._sender()

    def _receiver(self):
        return self._phonenumber(self.receiver_index)

    @property
    def receiver(self):
        return self._receiver()

    def _message(self):
        return ','.join(self.data[self.message_index])

    @property
    def message(self):
        return self._message()


class RecordTypeA(RecordType):
    sender_index = 0
    receiver_index = 1
    datetime_index = -2
    message_index = slice(2, -2)
    id_index = -1


class RecordTypeB(RecordType):
    sender_index = 3
    receiver_index = 4
    datetime_index = 1
    message_index = slice(5, None)
    id_index = 2


class Record(object):
    pass


class Normalizer(object):

    def __init__(self):
        self.normalized_records = []

    def normalize_row(self, row):
        pass

    @classmethod
    def normalize(cls, fileobj):
        n = cls()

        for row in csv.reader(fileobj):
            n.normalize_row(row)
