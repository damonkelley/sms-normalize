import csv
from functools import reduce
import json

import phonenumbers as pn
import dateutil.parser as dateutil


DEFAULT_REGION = 'US'


class PhoneNumberParseError(Exception):
    pass


def _create_phonenumber(phonenumber):
    phonenumber = str(phonenumber)

    try:
        return pn.parse(phonenumber)
    except pn.NumberParseException:
        pass

    try:
        return pn.parse(phonenumber, DEFAULT_REGION)
    except pn.NumberParseException:
        raise PhoneNumberParseError('Unable to parse the phone number.')


def is_valid_phonenumber(phonenumber):
    try:
        numobj = _create_phonenumber(phonenumber)
    except PhoneNumberParseError:
        return False

    return pn.is_valid_number(numobj)


def normalize_phonenumber(phonenumber):
    numobj = _create_phonenumber(phonenumber)
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
        self.id = self._get_id()
        self.message = self._get_message()
        self.sender = self._get_sender()
        self.receiver = self._get_receiver()
        self.datetime = self._get_datetime()

    def _phonenumber(self, index):
        number = self.data[index]
        return normalize_phonenumber(number)

    def _get_datetime(self):
        return normalize_datetime(self.data[self.datetime_index])

    def _get_id(self):
        return self.data[self.id_index]

    def _get_sender(self):
        return self._phonenumber(self.sender_index)

    def _get_receiver(self):
        return self._phonenumber(self.receiver_index)

    def _get_message(self):
        return ','.join(self.data[self.message_index])

    def __add__(self, other):
        self.message = '{} {}'.format(self.message, other.message)
        return self

    def __repr__(self):
        return '<{0}: {1} | {2}>'.format(
            self.__class__.__name__, self.id, self.message)


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


def create_record(data):
    # Get the first two items and throw away the rest.
    sender, receiver, *rest = data

    if is_valid_phonenumber(sender) and is_valid_phonenumber(receiver):
        return RecordTypeA(data)

    return RecordTypeB(data)

def merge_common_records(records):
    for record in records:
        common = [r for r in records if r.id == record.id]

        if len(common) > 1:
            record = reduce(lambda r1, r2: r1 + r2, common)

            records = [r for r in records if r is record or r not in common]

    return records

def convert_records_to_json(records):
    dict_records = []

    for record in records:
        record_dict = {
            'from': record.sender,
            'to': record.receiver,
            'sid': record.id,
            'message': record.message,
            'time': record.datetime
        }

        dict_records.append(record_dict)

    return json.dumps(dict_records, indent=2, sort_keys=True)

def main(input_stream, output_stream):
    reader = csv.reader(input_stream)

    records = [create_record(row) for row in reader]
    records = merge_common_records(records)
    json_records = convert_records_to_json(records)

    output_stream.write(json_records)


if __name__ == '__main__':
    import sys
    main(sys.stdin, sys.stdout)
