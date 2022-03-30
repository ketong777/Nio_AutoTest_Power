import allure

from utils.mcu_com_driver import *
from utils.pcan_drive import *
from pywinauto import Application


class TestClass_Power1:

    def setup(self):
        with open(r"print.txt", "w") as op:
            op.write("---test case print---\n")
            op.close()

    @allure.feature("power")
    @allure.description('反复休眠打断唤醒后确认芯片状态')
    def test_power1(self):
        app = Application().connect(path=r'C:\Users\liu_k1\Desktop\it9000\IT9000.exe')
        app['IT9000']['12.00V/1.00A'].click()
        mypcan = MyPcan()
        m_objTimer = TimerRepeater("NM_BGW", float(640) / 1000, "00 00 01 00 00 00 00 00", mypcan, 0x505)
        m_objTimer.start()
        tbox_control = tbox_control_com_class()
        tbox_control.wait_msg("[Power]NAD Standbyout over")
        m_objTimer.stop()
        tbox_control.wait_msg("[Power]Nad sleep Res,GPIO1 set low")
        m_objTimer.start()
        tbox_control.s_wait(30)
        m_objTimer.stop()
        tbox_control.wait_msg("[Power]MCU will goto Sleep Mode")
        app['IT9000']['0.00V/0.00A'].click()
        with open(r"print.txt", "r") as c:
            line = c.readlines()
            c = '\n'.join([i for i in line]).replace("\n\n", "\n")
            allure.attach(c, 'printlog', allure.attachment_type.TEXT)
            assert "[Power]NAD Standbyout over" in c
            assert "[Power]Nad sleep Res,GPIO1 set low" in c
            assert "[Power]MCU will goto Sleep Mode" in c
            assert "[Power]NAD Sleep timeout,Force poweroff" not in c
