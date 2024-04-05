import time
import logging

from pymeasure.instruments.keithley import Keithley2450
from pymeasure.experiment import Procedure, FloatParameter, IntegerParameter, Parameter, BooleanParameter, ListParameter, Metadata
from pymeasure.adapters import FakeAdapter

from . import config
from .utils import SONGS
from .display import send_telegram_alert

log = logging.getLogger(__name__)


class BaseProcedure(Procedure):
    """Base procedure for all device-related measurements. It defines the basic
    parameters that are common to all the measurements, such as chip
    parameters.
    """
    # Procedure version. When modified, increment
    # <parameter name>.<parameter property>.<procedure startup/shutdown>
    procedure_version = Parameter('Procedure version', default='1.0.0')

    # Chip Parameters
    show_more = BooleanParameter('Show more', default=False)
    chip_name = Parameter('Chip name', default='Chip 1')
    info = Parameter('Information', default='None')

    # Metadata
    start_time = Metadata('Start time', fget=time.time)

    INPUTS = ['show_more', 'chip_name', 'info']
    

class MagnetProcedure(BaseProcedure):
    """Base procedure for all magnet-related measurements. It defines the basic
    parameters that are common to all the measurements.

    :param total_time: The total time of the measurement in min.
    :param orientation: The orientation of the chip with respect to the magnet.
    :param magnet_d: The distance from the chip to the magnet in cm.
    """
    total_time = FloatParameter('Total time', units='min', default=120.)
    orientation = ListParameter('Orientation', default='NE', choices=['NE', 'NW', 'SE', 'SW'])
    magnet_d = FloatParameter('Magnet distance', units='cm', default=10.)

    INPUTS = BaseProcedure.INPUTS + ['total_time', 'orientation', 'magnet_d']
    

class BaseHtProcedure(MagnetProcedure):
    """Measures a time-dependant voltage with four probes (2 channels)
    with a Keithley 2450.
    :param sense_curr: The current applied to the first channel in A.
    :param sense_comp: The compliance of the first channel in V.
    :param force_curr: The current applied to the second channel in pA.
    :param force_comp: The compliance of the second channel in mV.
    """
    sense_curr = FloatParameter('Sense current', units='A', default=0.)
    sense_comp = FloatParameter('Sense compliance', units='V', default=5e-2)
    force_curr = FloatParameter('Force current', units='A', default=1e-4)
    force_comp = FloatParameter('Force compliance', units='V', default=1.)
    
    # Additional Parameters, preferably don't change
    sampling_t = FloatParameter('Sampling time (excluding Keithley)', units='s', default=0., group_by='show_more')
    N_avg = IntegerParameter('N_avg', default=2, group_by='show_more')
    Vrange = FloatParameter('Vrange', units='V', default=100, group_by='show_more')   # Does NOTHING for now
    
    INPUTS = MagnetProcedure.INPUTS + ['sense_curr', 'sense_comp', 'force_curr', 'force_comp', 'sampling_t', 'N_avg']
    DATA_COLUMNS = ['t (s)', 'VDS (V)', 'V2 (V)']
    
    def get_keithley_time(self):
        return float(self.meter.ask(':READ? "IVBuffer", REL')[:-1])
    
    def startup(self):
        log.info("Setting up instruments")
        try:
            self.meter = Keithley2450(config['Adapters']['keithley2450'])
            # self.meter = Keithley2450(FakeAdapter())
        except Exception as e:
            log.error("Could not connect to instruments", exc_info=True)
            raise e

        # Keithley 2450 meter
        self.meter.reset()
        self.meter.write(':TRACe:MAKE "IVBuffer", 100000')
        self.meter.use_front_terminals()
        self.meter.write(':VOLT:RSENse ON')  # Enable 4-wire sense for voltage measurements
        self.meter.measure_voltage(voltage=self.Vrange)
        
        self.meter.apply_current(compliance_voltage=self.sense_comp)
        self.meter.enable_source()
        time.sleep(0.5)
        
    def execute(self):
        raise NotImplementedError("This method must be implemented in a subclass")
    
    def shutdown(self):
        if not hasattr(self, 'meter'):
            log.info("No instruments to shutdown.")
            return

        for freq, t in SONGS['triad']:
            self.meter.beep(freq, t)
            time.sleep(t)

        self.meter.shutdown()
        log.info("Instruments shutdown.")
        
        send_telegram_alert(
            f"Finished Ht measurement for {self.chip_name}!"
        )
