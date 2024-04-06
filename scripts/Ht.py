"""
This Script is used to measure the Hall time-dependent voltage of the device
when a magnetic field is applied.
It uses a Keithley 2450 as four-probe meter.
"""
import time
import logging
import numpy as np
from lib.display import display_experiment
from lib.procedures import BaseHtProcedure

log = logging.getLogger(__name__)


class Ht(BaseHtProcedure):
    """Measures a time-dependant Hall voltage with a four-probe (2 channels)
    Keithley 2450.
    """
    def measuring_loop(self, t_end: float):
        avg_array = np.zeros(self.N_avg)
        keithley_time = self.get_keithley_time()
        while keithley_time < t_end:
            if self.should_stop():
                log.error('Measurement aborted')
                break

            self.emit('progress', 100 * keithley_time / self.total_time * 60)

            # Take the average of N_avg measurements
            for j in range(self.N_avg):
                avg_array[j] = self.meter.voltage

            keithley_time = self.get_keithley_time()
            self.emit('results', dict(zip(self.DATA_COLUMNS, [keithley_time, self.meter.source_voltage, np.mean(avg_array)])))
            avg_array[:] = 0.
            time.sleep(self.sampling_t)
    
    def execute(self):
        log.info("Starting the measurement")
        if self.sense_curr != 0.:
            self.meter.ramp_to_current(self.source_curr)
        
        self.measuring_loop(self.total_time * 60)


if __name__ == "__main__":
    display_experiment(Ht, "Hall Time-dependent Voltage Measurement")
    