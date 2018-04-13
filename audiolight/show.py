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
    print("chunk %d" % stream.get_read_available())
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
    vol = 0.3 * np.sum(fft) + 0.7 * np.max(fft)
    return (freqPeak, vol)

data = {
    'FREQ_OFFSET': 50,
    'FREQ_PEROID': 600,
    'MAX_VOL': 2000,
    'AVG_VOL': 2000,
    'MIN_VOL': 2000,

    'LIGHT_MAX': 0.8,
}

def get_percent_loop(val, peroid, offset):
    return (val - offset) % peroid / peroid

def get_percent_minmax(val, mi, mx):
    if (mx - mi) <= 0:
        return 0.0
    val = max(mi, min(val, mx))
    return (val - mi) / (mx - mi)

def hex2(val):
    h = hex(val)[2:]
    return h if len(h) == 2 else '0' + h

def update_vol(current_vol):
    min_vol = data['MIN_VOL']
    avg_vol = data['AVG_VOL']
    max_vol = data['MAX_VOL']
    data['AVG_VOL'] = 0.9 * avg_vol + 0.1 * current_vol
    data['MIN_VOL'] = min(0.98 * min_vol + 0.02 * avg_vol, current_vol)
    data['MAX_VOL'] = max(0.98 * max_vol + 0.02 * avg_vol, current_vol)

async def main_loop(bulb, stream):
    avg_freq = data['FREQ_OFFSET']
    avg_vol = 0
    while True:
        freq, volume = await analyze_sound(stream)
        update_vol(volume)
        avg_freq = 0.99 * avg_freq + 0.01 * freq
        h = get_percent_loop(avg_freq, data['FREQ_PEROID'], data['FREQ_OFFSET'])
        s = 1.0
        avg_vol = 0.3 * avg_vol + 0.7 * volume
        v = get_percent_minmax(avg_vol, data['MIN_VOL'], data['MAX_VOL'])
        rgb = colorsys.hsv_to_rgb(h * 360, s, v)
        rgb_hex = ''.join([hex2(int(255 * x)) for x in rgb])
        assert len(rgb_hex) == 6
        print('min: %10d avg: %10d max: %10d' % (
            data['MIN_VOL'], data['AVG_VOL'], data['MAX_VOL']))
        print("freq: %10d vol: %10d" % (freq, volume))
        print("change color: %s" % rgb_hex)
        bulb.set_color(data['LIGHT_MAX'], rgb_hex)

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
