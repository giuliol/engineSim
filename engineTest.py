from engine import Engine
import numpy as np
import sounddevice as sd

start = 500
short = 500

eng = Engine(Engine.TYPE_RS_250, Engine.WAVEFORM_2STROKE)

sound = eng.roar(200, 4000)
sound = np.append(sound, eng.roar(900, 2000))
sound = np.append(sound, eng.roar(1000, 1000))
sound = np.append(sound, eng.roar(2000, 1000))
sound = np.append(sound, eng.roar(3000, 1000))
sound = np.append(sound, eng.roar(4000, 2000))
sound = np.append(sound, eng.roar(1000, 4000))

import matplotlib.pyplot as plt

plt.plot(np.arange(len(sound)) / 44100, sound)
plt.show()

eng.sayHi()
sd.play(sound)
sd.wait()
