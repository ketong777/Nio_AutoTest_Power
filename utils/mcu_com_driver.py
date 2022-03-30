import datetime
import time
import serial
import logging
from utils.nio_constant import *

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("print.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -\n%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class tbox_control_com_class():

    def __init__(self):
        self.s = serial.Serial(COM_PORT_MCU, 115200, timeout=1)
        time.sleep(1)
        self.s.write(('%s\r' % MCU_PASSWORD).encode())

    def s_wait(self, wait_time):
        time.sleep(wait_time)
        app_output = self.s.readlines()
        output_data = "\n".join([i.decode().strip() for i in app_output])
        logger.info(output_data)

    def wait_msg(self, log_msg, wait_time=30):
        for times in range(wait_time):
            app_output = self.s.readlines()
            output_data = "\n".join([i.decode().strip() for i in app_output])
            logger.info(output_data)
            if log_msg in output_data:
                print(datetime.datetime.now(), times)
                break

    def s_exit(self):
        self.s.write(chr(0X03).encode())


if __name__ == '__main__':
    t = tbox_control_com_class()
