from engine import Engine
import numpy as np
import sounddevice as sd

eng = Engine(Engine.TYPE_SINGLE, Engine.WAVEFORM_DEFAULT)

sound = eng.roar(1000, 3000)
sound = np.append(sound, eng.roar(2000, 1000))
sound = np.append(sound, eng.roar(2500, 1000))
sound = np.append(sound, eng.roar(4500, 1000))
sound = np.append(sound, eng.roar(5000, 1000))
sound = np.append(sound, eng.roar(6500, 1000))
sound = np.append(sound, eng.roar(7500, 1000))
sound = np.append(sound, eng.roar(9500, 2000))
sound = np.append(sound, eng.roar(1000, 4000))

eng.sayHi()
sd.play(sound)
sd.wait()