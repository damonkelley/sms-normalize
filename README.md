# GoButler Python Development Challenge

### Requirements

Python 3.3 - 3.5

### Usage

The script will read the CSV content from `stdin` and write the JSON to `stdout`. 

If it encounters an error while parsing a record, that record is skipped and a message is logged to `stderr`.

There are 2 ways to run the script.

#####  Method 1: Install the package and expose the `entry_point` command.

**Note**: The setup script uses `setuptools`. If that is not installed in your environment, consider using method 2.

```sh
$ python setup.py install

$ cat foo.csv | gobutler-challenge

# Ignore the error output
$ cat foo.csv | gobutler-challenge 2> /dev/null
```

##### Method 2: Run the script directly.

```sh
# Install the dependencies.
$ pip install -r requirements.txt

$ cat foo.csv | python challenge.py
```

#### Tests

To run the tests, first install the test requirements.
```sh
$ pip install -r requirements.txt
$ pip install -r requirements-test.txt
```

Start testing.
```sh
$ py.test
```

To run the tests with Python 3.3 and Python 3.4 (and do a Flake8 check)
```
$ tox
```

### Accepted Data

This script attempts to reconcile incomplete or malformed data. The exact approach I have taken is as follows.

##### IDs

All IDs are accepted.

##### Messages

All messages are accepted and if multiple records share an ID, those records are merged in the order that they appear in the incoming data. 

Because a message could present any combination of characters, it is difficult to determine it's validity.

##### Phone Numbers

In this script there is such a thing a _valid phone number_. Such a number is a string or integer that can be parsed using the [`phonenumber`](https://github.com/daviddrysdale/python-phonenumbers) library. The script does not check that parsed number exists in any registry however.

The script will also use the US country code for numbers that do not include region information.

If a number can not be parsed at all, an exception is raised and the record is skipped.

##### Dates and Times

Any date/datetime string is allowed as long as the string is well-formed. A non-well-formed datestring will raise an exception when parsed, which will cause the script to skip the record.

An example of a non-well-formed datestring is `2015-06-45 00:00:00`, because it is not possible to have 45 days in a month.
