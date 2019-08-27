import time
import multiprocessing
from threading import Thread, Event
from Queue import Queue
from random import randint
from datetime import datetime

from numpy import nonzero

from pympler import asizeof, tracker

DESIRED_DETECTOR_AREA_3_PERCENT = 1966  # 3% of the detector area in pixels
DESIRED_DETECTOR_AREA_4_PERCENT = 2621
DESIRED_DETECTOR_AREA_5_PERCENT = 3276

time_fmt = '%Y-%m-%d_%H:%M:%S'
prev_file_time = datetime.strptime(datetime.now().strftime(time_fmt), time_fmt)


def set_file_time():
    global prev_file_time        
    current_time_ts = time.mktime(datetime.strptime(datetime.now().strftime(time_fmt), time_fmt).timetuple())
    prev_file_time_ts = time.mktime(prev_file_time.timetuple())
    if current_time_ts - prev_file_time_ts >= 28800:
        prev_file_time = datetime.strptime(datetime.now().strftime(time_fmt), time_fmt)


def get_frame_data(dev, conn):
#    print('in the process')
    #try:
    frame = dev.lastAcqFrameRefInc()
    f_data = frame.data()
    conn.send(f_data)
    conn.close()
    #except Exception as e:
    #print(e)
#    print('exitting the process')


def put_into_queue(q, acq, counts, conn):
    q.put(acq, counts)
    conn.send(q)
    conn.close()
    
class MiniPIXAcquisition(Thread):
    def __init__(self,
                 minipix,
                 pixet,
                 variable_frate=False,
                 shutter_time=.5,
                 detector_area=DESIRED_DETECTOR_AREA_3_PERCENT,
                 **kwargs):
        """
        :param minipix: MiniPIX object
        :param variable_frate: Capture with a variable frame rate if set to true
        :param shutter_time: Initial shutter time
         :param detector_area: Detector area parameter used by variable frame rate algorithm
        """
        Thread.__init__(self, **kwargs)
        self.minipix = minipix
        self.pixet = pixet
        self.variable = variable_frate
        self.shutter_time = shutter_time
        self.detector_area = detector_area
        self.max_shutter_time = 2
        self.min_shutter_time = .03  # 30 frames per second
        self.max_ramp_rate = 0
        self.data = Queue()
        self.stop_acquisitions = Event()
        self.shutdown_flag = Event()
        self.file_time = prev_file_time
        
    def _take_aquisition(self):
        """
        :param shutter_time: Length of time to expose MiniPIX for
        :return:
        """

        global prev_file_time
        set_file_time()
        file_prefix = ''
        if 'MiniPIX' in self.minipix.fullName():
            file_prefix = 'mp'
        elif 'FITPix' in self.minipix.fullName():
            file_prefix = 'fp'
        self.minipix.doSimpleAcquisition(1,
                                         self.shutter_time,
                                         self.pixet.PX_FTYPE_AUTODETECT,
                                         file_prefix + '_output' + '-' + str(prev_file_time) + '.pmf')
        paren_conn ,child_conn = multiprocessing.Pipe()
        frame_thread_process = multiprocessing.Process(target = get_frame_data, args = (self.minipix, child_conn,))
        #print('start')
        frame_thread_process.start()
        frame_data = paren_conn.recv()
        frame_thread_process.terminate()
        #print('killed')
        
        #print(len(frame_data))
    

        """
        parent_conn, child_conn = multiprocessing.Pipe()
        frame_data_process = multiprocessing.Process(target = get_frame_data, args = (self.minipix, child_conn,))
        frame_data_process.start()
        frame_data = parent_conn.recv()
        frame_data_process.terminate()
        """
        return frame_data

    @staticmethod
    def _total_hit_pixels(frame):
        """
        :param frame: Frame of acquired MiniPIX data
        :return:
        """
        total_hit_pixels = len(nonzero(frame)[0])
        return total_hit_pixels

    def _variable_frame_rate(self):
        acq = self._take_aquisition()
        count = self._total_hit_pixels(acq)
        self.data.put((acq, count))

        while not self.stop_acquisitions.is_set():
            hit_rate = count / self.shutter_time
            if hit_rate != 0:
                self.shutter_time = self.detector_area / hit_rate
            else:
                self.shutter_time = self.max_shutter_time

            if self.shutter_time < self.min_shutter_time:
                self.shutter_time = self.min_shutter_time
            if self.shutter_time > self.max_shutter_time:
                self.shutter_time = self.max_shutter_time

            acq = self._take_aquisition()
            count = self._total_hit_pixels(acq)
            self.data.put((acq, count))

    def _constant_frame_rate(self):
        while not self.stop_acquisitions.is_set():
            acq = self._take_aquisition()
            """
            parent_conn, child_conn = multiprocessing.Pipe()
            queue_process = multiprocessing.Process(target = put_into_queue, args = (self.data, acq, self._total_hit_pixels(acq), child_conn,))
            queue_process.start()
            self.data = parent_conn.recv()
            queue_process.terminate()
            """
            self.data.put((acq, self._total_hit_pixels(acq)))
            #print(self.data.qsize())
            
    def _begin_acquisitions(self):
        if self.variable:
            self._variable_frame_rate()
        else:
            self._constant_frame_rate()

    def pause_acquisitions(self):
        self.stop_acquisitions.set()

    def start_acquisitions(self):
        self.stop_acquisitions.clear()

    def shutdown(self):
        self.stop_acquisitions.set()
        self.shutdown_flag.set()

    def get_last_acquisition(self, block=True):
        return self.data.get(block=block)

    def run(self):
        while not self.shutdown_flag.is_set():
            self._begin_acquisitions()




def take_acquisition(device, shutter_time, pixet):
    """
    :param shutter_time: Length of time to expose MiniPIX for
    :return:
    """

    global prev_file_time
    set_file_time()
    file_prefix = ''
    if 'MiniPIX' in self.device.fullName():
        file_prefix = 'mp'
    elif 'FITPix' in self.device.fullName():
        file_prefix = 'fp'
    self.device.doSimpleAcquisition(1,
                                     self.shutter_time,
                                     self.pixet.PX_FTYPE_AUTODETECT,
                                     file_prefix + '_output' + '-' + str(prev_file_time) + '.pmf')
    #frame = self.device.lastAcqFrameRefInc()
    
    return frame.data()
