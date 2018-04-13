##
# author: Chung-Sheng Wu
# email: samsam2310@gmail.com
#
# Chsmartbulb controler
# Similar to this one: https://github.com/pfalcon/Chsmartbulb-led-bulb-speaker,
# but I change some socket value and it work!
# The code can control the bulb with "ilight pro" app can control.
# Only can control the color, the color or white/yellow mode.
#
# Some thing about protocol:
#   send exp: 01fe0000510210000000008000000080
#   recv exp: 01fe000041811f0000000000000000000d0fff02010100040002f90201010e
#   Start with : 01fe0000
#   41,51 to read, write
#   A unknown byte, and then a byte represent size of the message, exp:
#   01fe00005102 "10" 000000008000000080 => 0x10 => 16 bytes
##

import bluetooth as bt
import logging

SPP_SERVICE_UUID = '00001101-0000-1000-8000-00805F9B34FB'

def hex2(val):
    h = hex(val)[2:]
    return h if len(h) == 2 else '0' + h

def _check_connected(func):
    def wrapper(self, *args, **kargs):
        if not self.is_connected():
            raise Exception('Need to connect first!')
        return func(self, *args, **kargs)

    return wrapper

class Bulb():
    def __init__(self, mac_addr):
        self._mac_addr = mac_addr
        service_matches = bt.find_service(
            uuid=SPP_SERVICE_UUID, address=mac_addr)

        if len(service_matches) == 0:
            raise Exception("Couldn't find the service.")

        first_match = service_matches[0]
        self._port = first_match["port"]
        self._name = first_match["name"]
        self._host = first_match["host"]

        self._sock = None
        self._heart_beat_counter = 0

    @staticmethod
    def _h(value):
        return bt.binascii.unhexlify(value)

    def _send_hex_string(self, hex_string):
        self._heart_beat_counter += 1
        if self._heart_beat_counter >= 10:
            self._heart_beat_counter = 0
            self._heart_beat()

        self._sock.send(self._h(hex_string))

    def _recv_bytes(self, n_bytes):
        r = self._sock.recv(n_bytes)
        logging.info('Receive: %s' % bt.binascii.hexlify(r))

    def _heart_beat(self):
        # Send maybe a query message or a heartbeat message.
        # Official app do this about once per second.
        self._sock.send(self._h('01fe0000510210000000008000000080'))
        self._recv_bytes(16)

    def connect(self):
        self._sock = bt.BluetoothSocket(bt.RFCOMM)
        self._sock.connect((self._host, self._port))

        # First of all, send '01234567'
        self._send_hex_string('3031323334353637')
        self._heart_beat()

    def disconnect(self):
        self._sock.close()
        self._sock = None

    def is_connected(self):
        return self._sock is not None

    @staticmethod
    def _get_open_code(is_color_mode, is_enabled):
        return "01fe00005181180000000000000000000d07%s0301%s0e00" % (
                "02" if is_color_mode else "01",
                "01" if is_enabled else "02"
            )

    @_check_connected
    def set_mode(self, is_color_mode, is_enabled):
        """ Set the bulb mode.
            is_color_mode: True to set to color mode, False to set to
                white/yellow mode.
            is_enabled: False to disable(close) the bulb.
        """
        code = self._get_open_code(is_color_mode, is_enabled)
        self._send_hex_string(code)
        self._recv_bytes(28)

    @staticmethod
    def _get_yellow_white_code(percent):
        assert percent >= 0.0 and percent <= 1.0
        return "01fe00005181180000000000000000000d07010303%s0e00" % (
                hex2(int(255 * percent))
            )

    @_check_connected
    def set_warm_color(self, percent):
        """ Set the yellow white percent when the mode is white/yellow mode.
            percent: 0.0 to 1.0, yellow to white.
        """
        code = self._get_open_code(percent)
        self._send_hex_string(code)
        self._recv_bytes(28)

    @staticmethod
    def _get_warm_brightness_code(percent):
        assert percent >= 0.0 and percent <= 1.0
        return "01fe00005181180000000000000000000d07010302%s0e00" % (
                hex2(int(16 * percent)) # 0x00 ~ 0x10
            )

    @_check_connected
    def set_warm_brightness(self, percent):
        """ Set the brightness when the mode is white/yellow mode.
            percent: 0.0 to 1.0.
        """
        code = self._get_warm_brightness_code(percent)
        self._send_hex_string(code)
        self._recv_bytes(28)

    @staticmethod
    def _get_color_code(brightness, hex_color):
        return "01fe000051811c0000000000000000000d0a02030c%s%s0e0000" % (
                hex2(int(255 * brightness)),
                hex_color
            )

    @_check_connected
    def set_color(self, brightness, hex_color):
        """ Set the color when the mode is color mode.
            brightness: 0.0 to 1.0, the brightness.
            hex_color: RGB 6 bytes hex color.
        """
        if hex_color == '000000':
            brightness = 0.1
            hex_color = '110000'
        code = self._get_color_code(brightness, hex_color)
        self._send_hex_string(code)
        self._recv_bytes(28)
