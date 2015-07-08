import csv

import phonenumber as pn
import dateutil.parser as dateutil


DEFAUL_REGION = 'US'


def normalize_phonenumber(phonenumber):
    phonenumber = str(phonenumber)

    try:
        numobj = pn.parse(phonenumber)
    except pn.NumberParseException:
        numobj = pn.parse(phonenumber, DEFAUL_REGION)

    return '{code}{national_num}'.format(
        code=numobj.country_code, national_num=numobj.national_number)


class RecordType(object):
    column_map = []

    def __init__(self, data):
        self.data

    def _datetime(self):
        pass

    @property
    def datetime(self):
        return self._datetime()

    def _id(self):
        pass

    @property
    def id(self):
        return self._id()

    def _sender(self):
        pass

    @property
    def sender(self):
        return self._sender()

    def _receiver(self):
        pass

    @property
    def receiver(self):
        return self._receiver()

    def _message(self):
        pass

    @property
    def message(self):
        return self._message()


class RecordTypeA(RecordType):
    column_map = ['sender', 'receiver', 'message', 'datetime', 'id']

    def _sender(self):
        number = self.data[0]
        return normalize_phonenumber(number)

    def _receiver(self):
        number = self.data[1]
        return normalize_phonenumber(number)

    def _id(self):
        return self.data[-1]

    def _datetime(self):
        return dateutil.parse(self.data[-2])

    def _message(self):
        return ','.join(self.data[2:-2])


class RecordTypeB(RecordType):
    column_map = ['datetime', 'id', 'sender', 'receiver', 'message']

    def _sender(self):
        number = self.data[3]
        return normalize_phonenumber(number)

    def _receiver(self):
        number = self.data[4]
        return normalize_phonenumber(number)

    def _id(self):
        return self.data[2]

    def _datetime(self):
        return dateutil.parse(self.data[:2])

    def _message(self):
        return ','.join(self.data[5:])


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
