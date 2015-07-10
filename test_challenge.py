import pytest
import phonenumbers

import challenge


class TestNormalizePhonenumber:
    """Tests for challenge.normalize_phonenumber."""

    def test_number_with_country_code_is_parsed_correctly(self):
        assert challenge.normalize_phonenumber('+63490941094') == '63490941094'

    def test_number_without_country_code_is_parsed_correctly(self):
        assert challenge.normalize_phonenumber('2608941966') == '12608941966'

    def test_accepts_numeric_number(self):
        assert challenge.normalize_phonenumber(2608941966) == '12608941966'

    def test_raises_exception_with_invalid_string(self):
        with pytest.raises(phonenumbers.NumberParseException):
            challenge.normalize_phonenumber('abcdefghij')

    @pytest.mark.parametrize('number, expected', [
        ('1111111111', '1111111111'),
        ('4125425345', '14125425345'),
        (4125425345, '14125425345'),
        (9121345813, '19121345813'),
        ('+6433512345', '6433512345'),
        ('+12129876543', '12129876543'),
        # add () num-num format
    ])
    def test_output(self, number, expected):
        assert challenge.normalize_phonenumber(number) == expected


class TestRecordType:
    test_data = [
        '(212) 452-1214',
        '(415) 999-1234',
        '2015-04-23 04:55:12',
        '00a12df6',
        'This is a sample text.'
    ]

    def test__id(self):
        record = challenge.RecordType(self.test_data)
        assert record._id() == '00a12df6'

    def test__datetime(self):
        record = challenge.RecordType(self.test_data)
        assert record._datetime() == '2015-04-23T04:55:12'

    def test__message(self):
        record = challenge.RecordType(self.test_data)
        assert record._message() == 'This is a sample text.'

    def test__sender(self):
        record = challenge.RecordType(self.test_data)
        assert record._sender() == '12124521214'

    def test__receiver(self):
        record = challenge.RecordType(self.test_data)
        assert record._receiver() == '14159991234'


class TestRecordTypeA:
    test_data = [
        '(212) 452-1214',
        '(415) 999-1234',
        'This is a sample text',
        '2015-04-23 04:55:12',
        '00a12df6'
    ]

    def test_id(self):
        record = challenge.RecordTypeA(self.test_data)
        assert record.id == '00a12df6'

    def test_datetime(self):
        record = challenge.RecordTypeA(self.test_data)
        assert record.datetime == '2015-04-23T04:55:12'

    def test_message(self):
        record = challenge.RecordTypeA(self.test_data)
        assert record.message == 'This is a sample text'

    def test_sender(self):
        record = challenge.RecordTypeA(self.test_data)
        assert record.sender == '12124521214'

    def test_receiver(self):
        record = challenge.RecordTypeA(self.test_data)
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

    def test_id(self):
        record = challenge.RecordTypeB(self.test_data)
        assert record.id == '4125425345'

    def test_datetime(self):
        record = challenge.RecordTypeB(self.test_data)
        assert record.datetime == '2015-06-22T09:12:45'

    def test_message(self):
        record = challenge.RecordTypeB(self.test_data)
        assert record.message == 'This is a part 2 of a multipart message'

    def test_sender(self):
        record = challenge.RecordTypeB(self.test_data)
        assert record.sender == '49231971134'

    def test_receiver(self):
        record = challenge.RecordTypeB(self.test_data)
        assert record.receiver == '12129876543'
