import allure
from pywinauto import Application

from utils.mcu_com_driver import *
from utils.pcan_drive import *


class TestClass_Power5:

    def setup(self):
        with open(r"print.txt", "w") as op:
            op.write("---test case print---\n")
            op.close()

    @allure.feature("power")
    @allure.description('备电切换到Listen芯片状态确认')
    def test_power5(self):
        mypcan = MyPcan()
        m_objTimer = TimerRepeater("NM_BGW", float(640) / 1000, "00 00 01 00 00 00 00 00", mypcan, 0x505)
        m_objTimer.start()
        app = Application().connect(path=r'C:\Users\liu_k1\Desktop\it9000\IT9000.exe')
        app['IT9000']['12.00V/1.00A'].click()
        tbox_control = tbox_control_com_class()
        tbox_control.wait_msg("[Power]NAD Standbyout over")
        app['IT9000']['0.00V/0.00A'].click()
        m_objTimer.stop()
        app['IT9000']['12.00V/1.00A'].click()
        tbox_control.wait_msg("[Power]Nad sleep Res,GPIO1 set low")
        m_objTimer.start()
        tbox_control.wait_msg("[Power]NAD Req Reset itself")
        m_objTimer.stop()
        app['IT9000']['0.00V/0.00A'].click()
        with open(r"print.txt", "r") as c:
            line = c.readlines()
            c = '\n'.join([i for i in line]).replace("\n\n", "\n")
            allure.attach(c, 'printlog', allure.attachment_type.TEXT)
            assert "[Power]NAD Standbyout over" in c
            assert "[Power]Nad sleep Res,GPIO1 set low" in c
            assert "[Power]NAD Req Reset itself" not in c
