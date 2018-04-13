# Bluetooth Chsmartbulb Python API

About Chsmartbulb see https://github.com/pfalcon/Chsmartbulb-led-bulb-speaker.
I change some socket value and it work!
The code can control the bulb which "iLight pro" App can control.
Only impliment changing the color, turning on/off,
changing to white/yellow mode.

For detials, see audiolight/bulb.py

## Example

``` python
from audiolight.bulb import Bulb

mac_addr = 'Your_bulb_mac_addr'

bulb = Bulb(mac_addr)
bulb.connect()

bulb.set_mode(True, True) # To color mode & enabled
bulb.set_color(1.0, '0000ff') # Set color to blue
```

## Can not work?
Try the script test-script/light.py, and try to get the bluetooth log from the
official app to see if the protocol is the same as this one.

## Light show

A sample script that can record the sound from the Linux computer(with the help
of pulseaudio), and chang the color of the bulb. Run the below script and set
up the pulseaudio to redirect the output sound to this script. Then you can see
the bulb react with the song you playing.

``` bash
python -m audiolight.show MAC_ADDR
```
