from engine import Engine
import numpy as np
import sounddevice as sd

start = 500
short = 500

eng = Engine(Engine.TYPE_FLAT_4, Engine.WAVEFORM_4STROKE)

sound = eng.roar(200, 2000)
# sound = np.append(sound, eng.roar(900, 2000))
sound = np.append(sound, eng.roar(850, 4000))
# sound = np.append(sound, eng.roar(2000, 1000))
sound = np.append(sound, eng.roar(2500, 4000))
sound = np.append(sound, eng.roar(5000, 4000))

# sound = np.append(sound, eng.roar(4000, 1000))
# sound = np.append(sound, eng.roar(6000, 1000))
# sound = np.append(sound, eng.roar(8000, 1000))
# sound = np.append(sound, eng.roar(10000, 1000))
# sound = np.append(sound, eng.roar(12000, 1000))

sound = np.append(sound, eng.roar(850, 4000))

import matplotlib.pyplot as plt

plt.plot(np.arange(len(sound)) / 44100, sound)
plt.show()

eng.sayHi()
sd.play(sound)
sd.wait()
