import datetime
import threading
import time

from utils.PCANBasic import *
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("print.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -\n%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class TimerRepeater(object):

    def __init__(self, name, interval, canmsg, mypcan, id):
        self._name = name
        self._thread = None
        self._event = None
        self._target = canmsg
        self._interval = interval
        self.mypcan = mypcan
        self.id = id

    def _run(self):
        while not self._event.wait(self._interval):
            if self._name == "ReadMessages":
                self.mypcan.ReadMessage()
            else:
                self.mypcan.write_can_msg(self._target, self.id)

    def start(self):
        if (self._thread == None):
            self._event = threading.Event()
            self._thread = threading.Thread(None, self._run, self._name)
            self._thread.start()

    def stop(self):
        if (self._thread != None):
            self._event.set()
            self._thread = None


class MyPcan(object):
    IsFD = False
    PcanHandle = PCAN_USBBUS1
    Bitrate = PCAN_BAUD_500K
    BitrateFD = "f_clock_mhz=20, nom_brp=5, nom_tseg1=2, nom_tseg2=1, nom_sjw=1, data_brp=2, data_tseg1=3, data_tseg2=1, data_sjw=1"

    def __init__(self):
        self.ShowConfigurationHelp()  ## Shows information about this sample
        self.ShowCurrentConfiguration()  ## Shows the current parameters configuration
        try:
            self.m_objPCANBasic = PCANBasic()
            self.m_DLLFound = self.CheckForLibrary()
        except:
            logger.info(datetime.datetime.now(), "Unable to find the library: PCANBasic.dll !")
            self.m_DLLFound = False
            return
        # self.m_objPCANBasic.Uninitialize(PCAN_NONEBUS)
        stsResult = self.m_objPCANBasic.Initialize(self.PcanHandle, self.Bitrate)
        if stsResult != PCAN_ERROR_OK:
            logger.info("Can not initialize. Please check the defines in the code.")
            print("Can not initialize. Please check the defines in the code.")
            self.ShowStatus(stsResult)
            return
        logger.info("PCAN Successfully initialized.")
        print("PCAN Successfully initialized.")

    def write_can_msg(self, data, id):
        data = data.replace(" ", "")
        msgCanMessage = TPCANMsg()
        msgCanMessage.ID = id
        msgCanMessage.LEN = int(len(data) / 2)
        msgCanMessage.MSGTYPE = PCAN_MESSAGE_STANDARD.value
        for i in range(msgCanMessage.LEN):
            msgCanMessage.DATA[i] = int(data[2 * i:2 * i + 2], 16)
            pass
        self.m_objPCANBasic.Write(self.PcanHandle, msgCanMessage)

    def ReadMessage(self):
        """
        Function for reading CAN messages on normal CAN devices

        Returns:
            A TPCANStatus error code
        """
        ## We execute the "Read" function of the PCANBasic
        stsResult = self.m_objPCANBasic.Read(self.PcanHandle)

        if stsResult[0] == PCAN_ERROR_OK:
            ## We show the received message
            self.ProcessMessageCan(stsResult[1], stsResult[2])

        return stsResult[0]

    def ProcessMessageCan(self, msg, itstimestamp):
        """
        Processes a received CAN message

        Parameters:
            msg = The received PCAN-Basic CAN message
            itstimestamp = Timestamp of the message as TPCANTimestamp structure
        """
        microsTimeStamp = itstimestamp.micros + 1000 * itstimestamp.millis + 0x100000000 * 1000 * itstimestamp.millis_overflow

        logger.info("Type: " + self.GetTypeString(msg.MSGTYPE))
        logger.info("ID: " + self.GetIdString(msg.ID, msg.MSGTYPE))
        logger.info("Length: " + str(msg.LEN))
        # logger.info("Time: " + self.GetTimeString(microsTimeStamp))
        logger.info("Data: " + self.GetDataString(msg.DATA, msg.MSGTYPE))
        logger.info("----------------------------------------------------------")

    def GetIdString(self, id, msgtype):
        """
        Gets the string representation of the ID of a CAN message

        Parameters:
            id = Id to be parsed
            msgtype = Type flags of the message the Id belong

        Returns:
            Hexadecimal representation of the ID of a CAN message
        """
        if (msgtype & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            return '%.8Xh' % id
        else:
            return '%.3Xh' % id

    def GetTimeString(self, time):
        """
        Gets the string representation of the timestamp of a CAN message, in milliseconds

        Parameters:
            time = Timestamp in microseconds

        Returns:
            String representing the timestamp in milliseconds
        """
        fTime = time / 1000.0
        return '%.1f' % fTime

    def GetTypeString(self, msgtype):
        """
        Gets the string representation of the type of a CAN message

        Parameters:
            msgtype = Type of a CAN message

        Returns:
            The type of the CAN message as string
        """
        if (msgtype & PCAN_MESSAGE_STATUS.value) == PCAN_MESSAGE_STATUS.value:
            return 'STATUS'

        if (msgtype & PCAN_MESSAGE_ERRFRAME.value) == PCAN_MESSAGE_ERRFRAME.value:
            return 'ERROR'

        if (msgtype & PCAN_MESSAGE_EXTENDED.value) == PCAN_MESSAGE_EXTENDED.value:
            strTemp = 'EXT'
        else:
            strTemp = 'STD'

        if (msgtype & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            strTemp += '/RTR'
        else:
            if (msgtype > PCAN_MESSAGE_EXTENDED.value):
                strTemp += ' ['
                if (msgtype & PCAN_MESSAGE_FD.value) == PCAN_MESSAGE_FD.value:
                    strTemp += ' FD'
                if (msgtype & PCAN_MESSAGE_BRS.value) == PCAN_MESSAGE_BRS.value:
                    strTemp += ' BRS'
                if (msgtype & PCAN_MESSAGE_ESI.value) == PCAN_MESSAGE_ESI.value:
                    strTemp += ' ESI'
                strTemp += ' ]'

        return strTemp

    def GetDataString(self, data, msgtype):
        """
        Gets the data of a CAN message as a string

        Parameters:
            data = Array of bytes containing the data to parse
            msgtype = Type flags of the message the data belong

        Returns:
            A string with hexadecimal formatted data bytes of a CAN message
        """
        if (msgtype & PCAN_MESSAGE_RTR.value) == PCAN_MESSAGE_RTR.value:
            return "Remote Request"
        else:
            strTemp = b""
            for x in data:
                strTemp += b'%.2X ' % x
            return str(strTemp).replace("'", "", 2).replace("b", "", 1)

    def CheckForLibrary(self):
        """
        Checks for availability of the PCANBasic library
        """
        ## Check for dll file
        try:
            self.m_objPCANBasic.Uninitialize(PCAN_NONEBUS)
            return True
        except:
            print("Unable to find the library: PCANBasic.dll !")
            return False

    def ShowStatus(self, status):
        """
        Shows formatted status

        Parameters:
            status = Will be formatted
        """
        print("=========================================================================================")
        print(self.GetFormattedError(status))
        print("=========================================================================================")

    def GetFormattedError(self, error):
        """
        Help Function used to get an error as text

        Parameters:
            error = Error code to be translated

        Returns:
            A text with the translated error
        """
        ## Gets the text using the GetErrorText API function. If the function success, the translated error is returned.
        ## If it fails, a text describing the current error is returned.
        stsReturn = self.m_objPCANBasic.GetErrorText(error, 0x09)
        if stsReturn[0] != PCAN_ERROR_OK:
            return "An error occurred. Error-code's text ({0:X}h) couldn't be retrieved".format(error)
        else:
            message = str(stsReturn[1])
            return message.replace("'", "", 2).replace("b", "", 1)

    def ShowConfigurationHelp(self):
        """
        Shows/prints the configurable parameters for this sample and information about them
        """
        print("=========================================================================================")
        print("|                        PCAN-Basic TimerWrite Example                                |")
        print("=========================================================================================")
        print("Following parameters are to be adjusted before launching, according to the hardware used |")
        print("                                                                                         |")
        print("* PcanHandle: Numeric value that represents the handle of the PCAN-Basic channel to use. |")
        print("              See 'PCAN-Handle Definitions' within the documentation                     |")
        print("* IsFD: Boolean value that indicates the communication mode, CAN (false) or CAN-FD (true)|")
        print("* Bitrate: Numeric value that represents the BTR0/BR1 bitrate value to be used for CAN   |")
        print("           communication                                                                 |")
        print("* BitrateFD: String value that represents the nominal/data bitrate value to be used for  |")
        print("             CAN-FD communication                                                        |")
        print("  TimerInterval: The time, in milliseconds, to wait before trying to write a message     |")
        print("=========================================================================================")
        print("")

    def ShowCurrentConfiguration(self):
        """
        Shows/prints the configured paramters
        """
        print("Parameter values used")
        print("----------------------")
        print("* PCANHandle= " + self.FormatChannelName(self.PcanHandle, self.IsFD))
        print("* IsFD= " + str(self.IsFD))
        print("* Bitrate= " + self.ConvertBitrateToString(self.Bitrate))
        print("* BitrateFD= " + self.BitrateFD)
        print("")

    def ConvertBitrateToString(self, bitrate):
        """
        Convert bitrate c_short value to readable string

        Parameters:
            bitrate = Bitrate to be converted

        Returns:
            A text with the converted bitrate
        """
        m_BAUDRATES = {PCAN_BAUD_1M.value: '1 MBit/sec', PCAN_BAUD_800K.value: '800 kBit/sec',
                       PCAN_BAUD_500K.value: '500 kBit/sec', PCAN_BAUD_250K.value: '250 kBit/sec',
                       PCAN_BAUD_125K.value: '125 kBit/sec', PCAN_BAUD_100K.value: '100 kBit/sec',
                       PCAN_BAUD_95K.value: '95,238 kBit/sec', PCAN_BAUD_83K.value: '83,333 kBit/sec',
                       PCAN_BAUD_50K.value: '50 kBit/sec', PCAN_BAUD_47K.value: '47,619 kBit/sec',
                       PCAN_BAUD_33K.value: '33,333 kBit/sec', PCAN_BAUD_20K.value: '20 kBit/sec',
                       PCAN_BAUD_10K.value: '10 kBit/sec', PCAN_BAUD_5K.value: '5 kBit/sec'}
        return m_BAUDRATES[bitrate.value]

    def FormatChannelName(self, handle, isFD):
        """
        Gets the formated text for a PCAN-Basic channel handle

        Parameters:
            handle = PCAN-Basic Handle to format
            isFD = If the channel is FD capable

        Returns:
            The formatted text for a channel
        """
        handleValue = handle.value
        if handleValue < 0x100:
            devDevice = TPCANDevice(handleValue >> 4)
            byChannel = handleValue & 0xF
        else:
            devDevice = TPCANDevice(handleValue >> 8)
            byChannel = handleValue & 0xFF

        if isFD:
            return ('%s: FD %s (%.2Xh)' % (self.GetDeviceName(devDevice.value), byChannel, handleValue))
        else:
            return ('%s: %s (%.2Xh)' % (self.GetDeviceName(devDevice.value), byChannel, handleValue))

    def GetDeviceName(self, handle):
        """
        Gets the name of a PCAN device

        Parameters:
            handle = PCAN-Basic Handle for getting the name

        Returns:
            The name of the handle
        """
        switcher = {
            PCAN_NONEBUS.value: "PCAN_NONEBUS",
            PCAN_PEAKCAN.value: "PCAN_PEAKCAN",
            PCAN_ISA.value: "PCAN_ISA",
            PCAN_DNG.value: "PCAN_DNG",
            PCAN_PCI.value: "PCAN_PCI",
            PCAN_USB.value: "PCAN_USB",
            PCAN_PCC.value: "PCAN_PCC",
            PCAN_VIRTUAL.value: "PCAN_VIRTUAL",
            PCAN_LAN.value: "PCAN_LAN"
        }

        return switcher.get(handle, "UNKNOWN")

    def __del__(self):
        if self.m_DLLFound:
            self.m_objPCANBasic.Uninitialize(PCAN_NONEBUS)

#
# if __name__ == '__main__':
#     mypcan = MyPcan()
#     m_objTimer = TimerRepeater("naaaaaaw", float(640) / 1000, "0000120000000000", mypcan, 0x505)
#     m_objTimer.start()
#     time.sleep(1)
#     m_objTimerWriteBGW_02 = TimerRepeater("BGW_02", float(20) / 1000, "10 00", mypcan, 0x2C3)
#     m_objTimerWriteBGW_02.start()
    # time.sleep(1)
    # m_objTimer.stop()
    # input()
    # m_objTimer2 = TimerRepeater("HarzWarmSts", float(100) / 1000, "0008000000000000", mypcan, 0x2c0, 8)
    # m_objTimer3 = TimerRepeater("TurnlndcrSwtSts", float(100) / 1000, "00001000", mypcan, 0x297, 4)
    # m_objTimer3 = TimerRepeater("TCSActv", float(100) / 1000, "1000000000000000", mypcan, 0x05E, 8)
    # m_objTimer3 = TimerRepeater("VCUActGear", float(100) / 1000, "0000000400000000", mypcan, 0x217, 4)
    # m_objTimer3 = TimerRepeater("TurnlndcrSwtSts", float(100) / 1000, "00001000", mypcan, 0x297, 4)
    # time.sleep(5)
    # m_objTimer2 = TimerRepeater("ReadMessages", float(10) / 1000, None, mypcan, None)
    # m_objTimer2.start()

# time.sleep(5)
# m_objTimer2.stop()
# m_objTimer.stop()
