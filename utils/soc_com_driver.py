import re
import time

import serial
from utils.nio_constant import *
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("print.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -\n%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class tbox_control_com_class():

    def __init__(self):
        self.s = serial.Serial(COM_PORT_SOC, 115200, bytesize=8, parity='N', stopbits=1, timeout=1)
        self.s.write(('%s\n' % COM_USERNAME).encode())
        time.sleep(1)
        self.s.write(('%s\n' % COM_PASSWORD).encode())
        time.sleep(1)

    def send_command(self, command):
        self.s.write(('%s\n' % command).encode())
        time.sleep(1)

    def s_exit(self):
        self.s.write(chr(0X03).encode())

    def s_wait(self, wait_time=0):
        time.sleep(wait_time)
        app_output = self.s.readlines()
        output_data = "\n".join([i.decode().strip() for i in app_output])
        logger.info(output_data)

    def lose_rate(self):
        if not self.s.isOpen():
            self.s.open()
        try:
            time.sleep(1)
            for i in range(40):
                time.sleep(1)
                app_output = self.s.readlines()
                output_data = "\n".join([i.decode().strip() for i in app_output])
                time.sleep(1)
                logger.info(output_data)
                # output_data = "123123|    8.0%|\n1qwasfa|    25.0%|\nasdagasd|    5.0%|\n"
                results = re.findall(r"(.*) (.*).0%(.*)\n", output_data, re.M)
                if results:
                    for result in results:
                        if int(result[1]) >= 10:
                            break
        except Exception as e:
            logger.info(str(e))

# if __name__ == '__main__':
#     t = tbox_control_com_class()
#     t.lose_rate()
