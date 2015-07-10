# GoButler Python Development Challenge

### Requirements

Python 3.3.x or Python 3.4.x

### Usage

The script will read the CSV content from stdin and write the JSON to stdout. If it encounters an error, a message will be written to stderr.

There are 2 ways to run the script.

#####  Method 1: Install the package and expose the `entry_point` command.

**Note**: The setup script uses `setuptools`. If that is not installed in your environment, consider using method 2.

```sh
$ python setup.py install

$ cat foo.csv | gobutler-challenge
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
```

Start testing.
```sh
$ py.test
```

To run the tests with Python 3.3 and Python 3.4 (and do a Flake8 check)
```
$ tox
```
