# Catalyze PaaS CLI
Build status: [![Circle CI](https://circleci.com/gh/catalyzeio/catalyze-paas-cli.svg?style=svg&circle-token=0c5e5a36e771343a7ecc71990657378dcc0d2581)](https://circleci.com/gh/catalyzeio/catalyze-paas-cli)

CLI tool for interacting with environments hosted on [Catalyze](https://catalyze.io/)'s Platform-as-a-Service.

## Installing

Either of these methods requires python 2.7, [pip](https://pip.pypa.io/en/latest/installing.html), and setuptools (`pip install setuptools`).

(note for OS X users: versions before 2.7.8 can result in SSL EOF errors. If you run into those, try upgrading to 2.7.8.)

To verify installation: `catalyze version`

### From PyPI

```
pip install catalyze
```

### From Source

1. Clone this repo
2. `python setup.py install`

## Usage

`catalyze --help`

## Issues, Support, and Help

For bugs with the CLI itself, please open github issues. For platform questions and problems, please [email Catalyze support](mailto:support@catalyze.io) (support@catalyze.io).
