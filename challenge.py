import csv
from functools import reduce
import json
import logging
import sys

import dateutil.parser as dateutil
import phonenumbers as pn


logging.basicConfig(
    stream=sys.stderr, format='[\033[0;31m%(levelname)s\033[0m] %(message)s')

DEFAULT_REGION = 'US'

ERROR_MSG = (
    'Unable to parse and convert the record with ID: {id}.\n'
    '\tRESULT: Skip\n'
    '\tMSG: {error}'
)


class ParseError(Exception):
    pass


class PhoneNumberParseError(ParseError):
    pass


class DateTimeParseError(ParseError):
    pass


def _create_phonenumber(phonenumber):
    """Creates a phonenumber.PhoneNumber object from a phone number
    string or integer.

    A PhoneNumberParseError is raised if it is unable to parse the number.

    Arguments:
        phonenumber - a valid phonenumber string or integer.
    """
    phonenumber = str(phonenumber)

    # Attempt to parse the number without a region.
    try:
        return pn.parse(phonenumber)
    except pn.NumberParseException:
        pass

    # Try again to parse the number with the default region code.
    try:
        return pn.parse(phonenumber, DEFAULT_REGION)

    except pn.NumberParseException:
        raise PhoneNumberParseError(
            'Unable to parse phone number {0}'.format(phonenumber))


def is_valid_phonenumber(phonenumber):
    """Checks if a phone number is valid.

    Returns a boolean.

    Arguments:
        phonenumber - a valid phonenumber string or integer.
    """
    try:
        numobj = _create_phonenumber(phonenumber)
    except PhoneNumberParseError:
        return False

    return pn.is_valid_number(numobj)


def normalize_phonenumber(phonenumber):
    """Normalize a phone number.

    Returns a phone number in the form of <country code><national number>.

    Example:
        (212) 234-2332 -> 12122342332

    Arguments:
        phonenumber - a valid phonenumber string or integer.
    """
    numobj = _create_phonenumber(phonenumber)

    return '{code}{national_num}'.format(
        code=numobj.country_code, national_num=numobj.national_number)


def normalize_datetime(datestring):
    """Normalize a datestring.

    Returns a new datestring in the ISO 8601 format. A
    DateTimeParseError is raised if datestring is malformed.

    Arguments:
        datestring - a valid datetime datestring.
    """
    try:
        dateobj = dateutil.parse(datestring)
    except ValueError:
        raise DateTimeParseError(
            'Date string {0} is malformed'.format(datestring))

    # Remove the microseconds and timezone if present.
    return dateobj.replace(microsecond=0, tzinfo=None).isoformat()


class RecordType(object):
    """The parsed object representation of the raw data."""
    sender_index = 0
    receiver_index = 1
    datetime_index = 2
    id_index = 3
    message_index = slice(4, None)

    def __init__(self, data):
        """Initialize a new RecordType.

        Arguments:
            data - a list of raw record data.
        """
        self.data = data
        self.id = self._get_id()
        self.message = self._get_message()
        self.sender = self._get_sender()
        self.receiver = self._get_receiver()
        self.datetime = self._get_datetime()

    def _phonenumber(self, index):
        """Get and parse the phone phone number at the given index."""
        number = self.data[index]
        return normalize_phonenumber(number)

    def _get_datetime(self):
        """Get and parse the datestring using the datetime_index."""
        return normalize_datetime(self.data[self.datetime_index])

    def _get_id(self):
        """Get the ID from using the id_index."""
        return self.data[self.id_index]

    def _get_sender(self):
        """Get and parse the phone number using the sender_index."""
        return self._phonenumber(self.sender_index)

    def _get_receiver(self):
        """Get and parse the phone number using the receiver_index."""
        return self._phonenumber(self.receiver_index)

    def _get_message(self):
        """Get and normalize the message using the message_index."""
        return ','.join(self.data[self.message_index])

    def __add__(self, other):
        """Concatenate the message attributes when to Records
        are added together.
        """
        self.message = '{} {}'.format(self.message, other.message)
        return self

    def __repr__(self):
        return '<{0}: {1} | {2}>'.format(
            self.__class__.__name__, self.id, self.message)


class RecordTypeA(RecordType):
    """A Subclass the of the RecordType class.

    This defines the precise index or slice for information in
    records of type A.
    """
    sender_index = 0
    receiver_index = 1
    datetime_index = -2
    message_index = slice(2, -2)
    id_index = -1


class RecordTypeB(RecordType):
    """A Subclass the of the RecordType class.

    This defines the precise index or slice for information in
    records of type B.
    """
    sender_index = 3
    receiver_index = 4
    datetime_index = 1
    message_index = slice(5, None)
    id_index = 2


def create_record(data):
    """Create a Record object from a list of raw record data.

    Returns a Record object.

    Arguments:
        data - a list of raw record data.

    This function will determine, based on the structure of the data,
    which record type to use in order to instantiate and return a
    new object.
    """
    # Get the first two items and throw away the rest.
    sender, receiver, *rest = data  # noqa

    # Use RecordTypeA if the first two element are valid phone numbers.
    if is_valid_phonenumber(sender) and is_valid_phonenumber(receiver):
        return RecordTypeA(data)

    return RecordTypeB(data)


def merge_common_records(records):
    """Merge record messages that share a common ID.

    Returns a list of JSON encoded objects.

    Arguments:
        records - A list of Record objects.
    """
    for record in records:
        # Find all the Records that also have the id of the current Record.
        common = [r for r in records if r.id == record.id]

        if len(common) > 1:
            # Leverage the __and__ method to concatenate the record messages.
            record = reduce(lambda r1, r2: r1 + r2, common)

            # Filter out any Record that is in the list of common Records and
            # is not the current record.
            # This will prevent Records that have already been merged from
            # being merged again.
            records = [r for r in records if r is record or r not in common]

    return records


def convert_records_to_json(records):
    """Convert a list of Record objects to JSON.

    Returns a list of JSON encoded objects.

    Arguments:
        records - A list of Record objects.

    JSON encoded objects have different key names than their Record object
    counterparts. The translation is as follows:
        record.sender    -> from
        record.receiver  -> to
        record.id        -> sid
        record.message   -> message
        recored.datetime -> time
    """
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


def main(input_stream=sys.stdin, output_stream=sys.stdout):
    """Parses the incoming CSV data and converts it to JSON.

    Errors are written to stderr.

    Arguments:
        input_stream - a file object with the CSV data.
        output_stream - a file object the JSON will be written to.
    """
    reader = csv.reader(input_stream)

    records = []
    for row in reader:
        # Attempt to create a new Record object. If a parse error is
        # encountered, skip it and log the error.
        try:
            record = create_record(row)
        except ParseError as err:
            logging.error(ERROR_MSG.format(id=record.id, error=str(err)))
            continue

        records.append(record)

    # Join any records that share an ID and convert to JSON.
    records = merge_common_records(records)
    json_records = convert_records_to_json(records)

    output_stream.write(json_records)


if __name__ == '__main__':
    main()
