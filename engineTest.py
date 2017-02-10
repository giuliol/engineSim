from engine import Engine
import numpy as np
import sounddevice as sd

eng = Engine(Engine.TYPE_V12, Engine.WAVEFORM_DEFAULT)

sound = eng.roar(800, 3000)
sound = np.append(sound, eng.roar(2000, 2000))
sound = np.append(sound, eng.roar(2500, 1000))
sound = np.append(sound, eng.roar(3500, 1000))
sound = np.append(sound, eng.roar(6000, 1000))
# sound = np.append(sound, eng.roar(8500, 1000))
# sound = np.append(sound, eng.roar(10500, 1000))
# sound = np.append(sound, eng.roar(11500, 2000))

sound = np.append(sound, eng.roar(1000, 4000))

eng.sayHi()
sd.play(sound)
sd.wait()