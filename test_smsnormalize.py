from io import StringIO
import json
from unittest import mock

import pytest
import phonenumbers

import smsnormalize


class TestCreatePhonenumber:

    def test_number_with_country_code(self):
        numobj = smsnormalize._create_phonenumber('+63490941094')
        assert isinstance(numobj, phonenumbers.PhoneNumber)

    def test_number_without_country_code_is_parsed_correctly(self):
        numobj = smsnormalize._create_phonenumber('2608941966')
        assert isinstance(numobj, phonenumbers.PhoneNumber)

    def test_accepts_numeric_number(self):
        numobj = smsnormalize._create_phonenumber(2608941966)
        assert isinstance(numobj, phonenumbers.PhoneNumber)

    def test_raises_exception_with_invalid_string(self):
        with pytest.raises(smsnormalize.PhoneNumberParseError):
            smsnormalize._create_phonenumber('abcdefghij')


class TestNormalizePhonenumber:
    """Tests for smsnormalize.normalize_phonenumber."""

    def test_number_with_country_code_is_parsed_correctly(self):
        assert smsnormalize.normalize_phonenumber('+63490941094') == '63490941094'

    def test_number_without_country_code_is_parsed_correctly(self):
        assert smsnormalize.normalize_phonenumber('2608941966') == '12608941966'

    def test_accepts_numeric_number(self):
        assert smsnormalize.normalize_phonenumber(2608941966) == '12608941966'

    def test_raises_exception_with_invalid_string(self):
        with pytest.raises(smsnormalize.PhoneNumberParseError):
            smsnormalize.normalize_phonenumber('abcdefghij')

    @pytest.mark.parametrize('number, expected', [
        ('1111111111', '1111111111'),
        ('4125425345', '14125425345'),
        (4125425345, '14125425345'),
        (9121345813, '19121345813'),
        ('+6433512345', '6433512345'),
        ('+12129876543', '12129876543'),
        ('(212) 987-6543', '12129876543'),
    ])
    def test_output(self, number, expected):
        assert smsnormalize.normalize_phonenumber(number) == expected


class TestIsValidPhonenumber:

    @pytest.mark.parametrize('number, expected', [
        ('1111111111', False),
        ('4125425345', True),
        (4125425345, True),
        ('3434912134581399340234', False),
        ('5555555', False),
        ('Jun 1 2015', False),
        ('This is a message', False),
        ('00a12df6', False),
    ])
    def test_numbers(self, number, expected):
        assert smsnormalize.is_valid_phonenumber(number) == expected


class TestNormalizeDatetime:

    def test_return_type_is_string(self):
        result = smsnormalize.normalize_datetime('2015-01-01')
        assert type(result) is str

    def test_return_value(self):
        result = smsnormalize.normalize_datetime('2015-01-01')
        assert result == '2015-01-01T00:00:00'

    def test_converts_gmt_string(self):
        datestring = 'Mon, Jun 22 2015 09:12:45 GMT'
        result = smsnormalize.normalize_datetime(datestring)
        assert result == '2015-06-22T09:12:45'

    def test_converts_gmt_string_without_day(self):
        datestring = 'Jun 22 2015 09:12:45 GMT'
        result = smsnormalize.normalize_datetime(datestring)
        assert result == '2015-06-22T09:12:45'


class TestRecordType:
    test_data = [
        '(212) 452-1214',
        '(415) 999-1234',
        '2015-04-23 04:55:12',
        '00a12df6',
        'This is a sample text.'
    ]

    def test__get_id(self):
        record = smsnormalize.RecordType(self.test_data)
        assert record._get_id() == '00a12df6'

    def test__get_datetime(self):
        record = smsnormalize.RecordType(self.test_data)
        assert record._get_datetime() == '2015-04-23T04:55:12'

    def test__get_message(self):
        record = smsnormalize.RecordType(self.test_data)
        assert record._get_message() == 'This is a sample text.'

    def test__get_sender(self):
        record = smsnormalize.RecordType(self.test_data)
        assert record._get_sender() == '12124521214'

    def test__get_receiver(self):
        record = smsnormalize.RecordType(self.test_data)
        assert record._get_receiver() == '14159991234'


class TestRecordTypeA:
    test_data = [
        '(212) 452-1214',
        '(415) 999-1234',
        'This is a sample text',
        '2015-04-23 04:55:12',
        '00a12df6'
    ]

    def test_initialized_correctly(self):
        record = smsnormalize.RecordTypeA(self.test_data)
        assert record.id == '00a12df6'
        assert record.datetime == '2015-04-23T04:55:12'
        assert record.message == 'This is a sample text'
        assert record.sender == '12124521214'
        assert record.receiver == '14159991234'


class TestRecordTypeB:
    test_data = [
        'Mon',
        'Jun 22 2015 09:12:45 GMT',
        '4125425345',
        '+49231971134',
        '+12129876543',
        'This is a part 2 of a multipart message'
    ]

    def test_initialized_correctly(self):
        record = smsnormalize.RecordTypeB(self.test_data)
        assert record.id == '4125425345'
        assert record.datetime == '2015-06-22T09:12:45'
        assert record.message == 'This is a part 2 of a multipart message'
        assert record.sender == '49231971134'
        assert record.receiver == '12129876543'


class TestCreateRecord:

    @mock.patch('smsnormalize.RecordTypeA')
    @mock.patch('smsnormalize.RecordTypeB')
    def test_returns_record_type_a(self, mock_record_b, mock_record_a):
        test_data = [
            '(212) 452-1214',
            '(415) 999-1234',
            'This is a sample text',
            '2015-04-23 04:55:12',
            '00a12df6'
        ]

        smsnormalize.create_record(test_data)

        assert mock_record_a.call_count == 1
        assert mock_record_b.call_count == 0
        mock_record_a.assert_called_with(test_data)

    @mock.patch('smsnormalize.RecordTypeA')
    @mock.patch('smsnormalize.RecordTypeB')
    def test_creates_record_type_b(self, mock_record_b, mock_record_a):
        test_data = [
            'Mon',
            'Jun 22 2015 09:12:45 GMT',
            '4125425345',
            '+49231971134',
            '+12129876543',
            'This is a part 2 of a multipart message'
        ]

        smsnormalize.create_record(test_data)

        assert mock_record_b.call_count == 1
        assert mock_record_a.call_count == 0
        mock_record_b.assert_called_with(test_data)


class TestMergeCommonRecords:
    test_data1 = [
        'Mon',
        'Jun 22 2015 09:12:45 GMT',
        '4125425345',
        '+49231971134',
        '+12129876543',
        'Message A.'
    ]
    test_data2 = [
        'Mon',
        'Jun 22 2015 09:12:45 GMT',
        '4125425345',
        '+49231971134',
        '+12129876543',
        'Message B.'
    ]

    test_data3 = [
        '(212) 452-1214',
        '(415) 999-1234',
        'This is a sample text',
        '2015-04-23 04:55:12',
        '00a12df6'
    ]

    def test_messages_are_concatenated(self):
        records = [
            smsnormalize.RecordTypeB(self.test_data1),
            smsnormalize.RecordTypeB(self.test_data2)
        ]

        records = smsnormalize.merge_common_records(records)

        assert len(records) == 1

        record = records.pop()
        assert record.message == 'Message A. Message B.'

    def test_merged_records_are_filtered_out(self):
        records = [
            smsnormalize.RecordTypeB(self.test_data1),
            smsnormalize.RecordTypeB(self.test_data2),
            smsnormalize.RecordTypeA(self.test_data3)
        ]

        records = smsnormalize.merge_common_records(records)

        assert len(records) == 2
        assert isinstance(records.pop(), smsnormalize.RecordTypeA)
        assert isinstance(records.pop(), smsnormalize.RecordTypeB)


class TestConvertRecordsToJson:
    test_data1 = [
        'Mon',
        'Jun 22 2015 09:12:45 GMT',
        '4125425345',
        '+49231971134',
        '+12129876543',
        'Message A.'
    ]
    test_data2 = [
        '(212) 452-1214',
        '(415) 999-1234',
        'This is a sample text',
        '2015-04-23 04:55:12',
        '00a12df6'
    ]

    def test_json_output(self):
        records = [
            smsnormalize.RecordTypeB(self.test_data1),
            smsnormalize.RecordTypeA(self.test_data2)
        ]

        output = json.loads(smsnormalize.convert_records_to_json(records))

        assert len(output) == 2

        record1 = output.pop(0)
        assert record1.get('from', False)
        assert record1.get('to', False)
        assert record1.get('sid', False)
        assert record1.get('message', False)
        assert record1.get('time', False)

        record2 = output.pop()
        assert record2.get('from', False)
        assert record2.get('to', False)
        assert record2.get('sid', False)
        assert record2.get('message', False)
        assert record2.get('time', False)


class TestMain:

    def test_main(self):
        output_stream = StringIO()
        with open('test_data/input.csv') as f:
            smsnormalize.main(f, output_stream)

        results = json.loads(output_stream.getvalue())
        assert type(results) is list
        assert len(results) == 6
