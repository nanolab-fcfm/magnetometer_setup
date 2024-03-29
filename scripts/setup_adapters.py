"""
This interactive script is used to configure the USB adapters for the
instruments that are used in the experiment scripts.
"""
import logging
from pymeasure.instruments.keithley import Keithley2450
import pyvisa
from lib import config, config_path

log = logging.getLogger(__name__)


def keithley_exists(adapter):
    try:
        K = Keithley2450(adapter)
        log.info(f"Keithley 2450 found at {adapter}")
        K.beep(3*440, 0.5)
        return True
    except:
        log.warning(f"Keithley 2450 not found at {adapter}")
        return False


def main():
    rm = pyvisa.ResourceManager()
    devices = rm.list_resources()

    is_keithley = False
    if 'keithley2450' not in config['Adapters'] or not keithley_exists(config['Adapters']['keithley2450']):
        for dev in devices:
            if 'USB0::0x05E6::0x2450' in dev and keithley_exists(dev):
                config['Adapters']['keithley2450'] = dev
                is_keithley = True
                break

        if not is_keithley:
            log.error("Keithley 2450 not found on any USB port. Connect the instrument and try again.")

    else:
        is_keithley = True
    
    with open(config_path, 'w') as f:
        config.write(f)

    log.info(f'New Adapter configuration saved to {config_path}')


if __name__ == "__main__":
    from scripts import log
    main()
