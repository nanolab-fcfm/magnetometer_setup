# Magnetometer Setup
Experimental setup for Magnetometer measurements.

## Installation
This project mainly uses [PyMeasure](https://pypi.org/project/PyMeasure/), although other packages such as NumPy and PyQT6 are used. To install this project, first clone the repository:

```bash
git clone https://github.com/nanolab-fcfm/magnetometer_setup.git
```
Then, create a virtual environment and activate it:

```bash
python -m venv <venv_name>
source <venv_name>/bin/activate
```

In Windows, use the following command to activate the virtual environment instead:

```
<venv_name>/scripts/activate
```

Finally, upgrade pip and install all necesary packages:
```python
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Usage
This project allows for the communication between the computer and the instruments used in the experimental setup, as well as the control of the instruments. So far, the following instruments are supported:
- Keithley 2450 SourceMeter ([Reference Manual](https://docs.rs-online.com/6c14/A700000007066480.pdf)) (Requires [NI-VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#480875) installed)

As well as all instruments available un the [PyMeasure library](https://pymeasure.readthedocs.io/en/latest/api/instruments/index.html).

The main window of the program can be run by executing the following command:

```python
python .
```

The main window will display all available procedures, and will allow you to run them. 

### Scripts
To start using the program, you should first set up the adapters needed to run a measurement. This is done by running

```python
python -m Scripts.setup_adapters
```

This interactive script will check all connected devices in your computer, and guide you to correctly set up every device in the configuration file `default_config.ini`. A new config file will be created; `config/config.ini`. This will override the default configuration, and you can later edit this file to your liking. To add more instruments, simply add their name to the `Adapters` section and run `setup_adapters.py`.

Each Script corresponds to a different procedure, and can be run independently. To run a script, use the following command:
```
python -m Scripts.<script_name>
```

## Testing
This project uses [PyTest](https://docs.pytest.org/en/stable/) for testing.
To run the tests, use the following command:
```
python -m pytest
```
Tests are stored in the `tests` folder, and are named `test_<module_name>.py`. You can add more tests by creating a new file in the `tests` folder, and naming it `test_<new_module_name>.py`. You can also check each test individually by running
```
python -m tests.<test_name>
```

