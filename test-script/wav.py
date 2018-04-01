"""PyAudio Example: Play a wave file."""

import pyaudio
import wave
import sys
import audioop

CHUNK = 100000

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

print(wf.getframerate())

# open stream (2)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=6)

# read data
data = wf.readframes(CHUNK)
# org_data = wf.readframes(CHUNK)
# datas = audioop.ratecv(org_data, 2, 1, wf.getframerate(), 48000, None)
# data = datas[0]

# play stream (3)
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(CHUNK)
print("played")
# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()