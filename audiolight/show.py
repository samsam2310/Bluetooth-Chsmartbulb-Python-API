import asyncio
import colorsys
import functools
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
import sys
import select

from .bulb import Bulb

np.set_printoptions(suppress=True) # don't use scientific notation

CHUNK = 4096 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)


async def analyze_sound(stream):
    while stream.get_read_available() < CHUNK:
        await asyncio.sleep(0.01) 
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    # Smooth the FFT by windowing data
    data = data * np.hanning(len(data))
    fft = abs(np.fft.fft(data).real)
    # Keep only first half(negative)
    fft = fft[:int(len(fft)/2)]
    freq = np.fft.fftfreq(CHUNK, 1.0/RATE)
    # Keep only first half(negative)
    freq = freq[:int(len(freq)/2)]
    freqPeak = freq[np.where(fft==np.max(fft))[0][0]] + 1
    return (freqPeak, np.max(fft))

data = {
    'MAX_FREQ': 2500,
    'MIN_FREQ': 50,
    'MAX_VOL': 2000000,
    'MIN_VOL': 50000,
}

def get_percent(val, mi, mx):
    val = max(mi, min(val, mx))
    return (val - mi) / (mx - mi)

def hex2(val):
    h = hex(val)[2:]
    return h if len(h) == 2 else '0' + h

async def main_loop(bulb, stream):
    while True:
        freq, volume = await analyze_sound(stream)
        h = get_percent(freq, data['MIN_FREQ'], data['MAX_FREQ'])
        s = 1.0
        v = get_percent(volume, data['MIN_VOL'], data['MAX_VOL'])
        rgb = colorsys.hsv_to_rgb(h, s, v)
        rgb_hex = ''.join([hex2(int(255 * x)) for x in rgb])
        assert len(rgb_hex) == 6
        # print("change color: %s" % rgb_hex)
        bulb.set_color(1.0, rgb_hex)

async def get_user_input():
    print("Hi:", end='')
    while True:
        await asyncio.sleep(0.01)
        i, o, e = select.select([sys.stdin], [], [], 0.01)
        if not i:
            continue
        return sys.stdin.readline().strip()

async def command_loop(ioloop):
    while True:
        cmd = await get_user_input()
        if cmd == 'q':
            ioloop.stop()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s BULB_MAC" % sys.argv[0])
        sys.exit(-1)

    bulb = Bulb(sys.argv[1])
    bulb.connect()
    bulb.set_mode(True, True)

    pa = pyaudio.PyAudio()
    stream = pa.open(
                format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                frames_per_buffer=CHUNK)

    event_loop = asyncio.get_event_loop()
    asyncio.ensure_future(main_loop(bulb, stream))
    asyncio.ensure_future(command_loop(event_loop))

    try:
        event_loop.run_forever()
    except:
        event_loop.close()
        bulb.set_mode(False, True)
        bulb.set_warm_brightness(0.1)
        stream.stop_stream()
        stream.close()
        pa.terminate()
