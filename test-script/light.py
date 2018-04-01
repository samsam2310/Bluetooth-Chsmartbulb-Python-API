from bluetooth import *
import sys

def h(v):
    return binascii.unhexlify(v)

if sys.version < '3':
    input = raw_input

addr = None

if len(sys.argv) < 2:
    print("no device specified.  Searching all nearby bluetooth devices for")
    print("the SampleServer service")
else:
    addr = sys.argv[1]
    print("Searching for SampleServer on %s" % addr)

# SPP
uuid = "00001101-0000-1000-8000-00805F9B34FB"
service_matches = find_service(uuid=uuid, address=addr)

if len(service_matches) == 0:
    print("couldn't find the service")
    sys.exit(1)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s" % (name, host))

# Create the client socket
sock = BluetoothSocket(RFCOMM)
sock.connect((host, port))

# 507 (log record # as shown in Wireshark)
# sock.send(b"01234567")
sock.send(h('3031323334353637'))

# 508
sock.send(h("01fe0000510210000000008000000080"))
r = sock.recv(16)
print(binascii.hexlify(r))
assert r == h("01fe0000410210000100000000000000")
print('Yee')

# 512
def doSomeThing():
    sock.send(h("01fe0000530018000000000000000080e207031f063b3800"))
    sock.send(h("01fe00005181180000000000000000000d0801020200000e"))
    sock.send(h("01fe00005181180000000000000000000d07020201000e00"))
    sock.send(h("01fe00005181180000000000000000000d07ff0201000e00"))

    sock.send(h("01fe00005181180000000000000000000d06ff020b0e0000"))

    sock.send(h("01fe0000510010000000008000000080"))

    r = sock.recv(16)
    print(binascii.hexlify(r))
    # 01fe0000418118000000000000000000
    r = sock.recv(8)
    print(binascii.hexlify(r))
    # 0d0801020202010e

# doSomeThing()

# ----- Test -----
# 01fe000051811c0000000000000000000d0c0202020000000000000e
# 01fe000041811f0000000000000000000d0fff02010100040002f90201010e

# 01fe000051812000000000000000000057410f0297cfb249ee8999add5ffe900
# 01:fe:00:00:41:81:18:00:00:00:00:00:00:00:00:00:0d:08:ff:02:0b:00:01:0e
# 01:fe:00:00:41:00:28:00:00:00:00:00:00:00:00:00:00:1f:00:1f:00:00:00:05:00:00:00:00:00:00:00:00:00:8c:6a:c8:02:e0:c1:9f
# 01fe000041811c0000000000000000000d0c02020201ff00ffdd000e

def get41811c():
    r = sock.recv(28)
    print(binascii.hexlify(r))

# Color ?
# print("change color")
# def color(st,c):
#     return "01fe000051811c0000000000000000000d0a02030c%s%s0e0000" % (st, c)
# sock.send(h(color("ff","0000ff")))
# get41811c()
# 01fe000041811c0000000000000000000d0c02040101ff00b7ff000e

print("open")
def open(color_mode, op):
    return "01fe00005181180000000000000000000d07%s0301%s0e00" % (
            "02" if color_mode else "01",
            "01" if op else "02"
        )
def yellowToWhite(percent):
    assert percent >= 0.0 and percent <= 1.0
    return "01fe00005181180000000000000000000d07010302000e00" % (
            # hex(int(255 * percent))
            # "01" if o else "02"
        )
sock.send(h(yellowToWhite(1)))
get41811c()
# 01fe000041811c0000000000000000000d0c0202140101020202020e

# ----- Test End ----
exit(1)
#
# Stuff below, while coded from btsnoop_hci.log, doesn't work -
# good-looking replies are received, but the bulb doesn't change
# the color.
#

# 519
sock.send(h("01fe0000510010000000008000000080"))
r = sock.recv(40)
# assert r == h("01fe0000410028000000000000000000001f00160000000500000200000000000007467002100000")

sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

# 528
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

# 531
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

# 534
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

# 537
sock.send(h("01fe0000538310000000ff0000000000"))
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

# 542
sock.send(h("01fe0000510010000000008000000080"))
sock.send(h("01fe000053831000ff00000000000000"))
print("546", repr(sock.recv(40)))

# 547
sock.send(h("01fe0000510010000000008000000080"))
print("549", repr(sock.recv(40)))

# 555
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

# 592
sock.send(h("01fe0000510010000000008000000080"))
print(598, repr(sock.recv(40)))

# 599
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

# 602
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))
# 605
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))
# 608
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))
# 614
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))
# 617
sock.send(h("01fe0000510010000000008000000080"))
print(repr(sock.recv(40)))

sock.close()