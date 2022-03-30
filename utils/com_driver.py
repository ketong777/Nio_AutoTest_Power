import re
import time
from utils.nio_constant import *
import serial

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("print.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -\n%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class tbox_control_com_class():

    def __init__(self, com):
        self.s = serial.Serial(com, 115200, timeout=1)
        self.s.write('\n'.encode())
        time.sleep(1)
        self.s.write(('%s\n' % COM_USERNAME).encode())
        time.sleep(1)
        self.s.write(('%s\n' % COM_PASSWORD).encode())
        app_output = self.s.readlines()
        output_data = "\n".join([i.decode().strip() for i in app_output])
        logger.info(output_data)

    def send_command(self, command):
        self.s.write(('%s\n' % command).encode())
        time.sleep(1)

    def s_exit(self):
        self.s.write(chr(0X03).encode())
        time.sleep(1)

    def s_wait(self, wait_time=0):
        time.sleep(wait_time)
        app_output = self.s.readlines()
        output_data = "\n".join([i.decode().strip() for i in app_output])
        logger.info(output_data)

# if __name__ == '__main__':
#     com_control = tbox_control_com_class()
