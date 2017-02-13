from engine import Engine
import numpy as np
import sounddevice as sd

start = 500
short = 500

eng = Engine(Engine.TYPE_INLINE_4_CROSSPLANE, Engine.WAVEFORM_4STROKE)

# sound = eng.roar(950, 6000)
sound = eng.rev(6000);

# sound = np.append(sound, eng.roar(900, 2000))
# sound = np.append(sound, eng.roar(8000, 2000))
# sound = np.append(sound, eng.roar(12000, 1000))
# # sound = np.append(sound, eng.roar(2500, 4000))
# # sound = np.append(sound, eng.roar(5000, 4000))
#
# # sound = np.append(sound, eng.roar(4000, 1000))
# sound = np.append(sound, eng.roar(6000, 2000))
# sound = np.append(sound, eng.roar(8000, 1000))
# sound = np.append(sound, eng.roar(10000, 1000))
# sound = np.append(sound, eng.roar(12000, 1000))

# sound = np.append(sound, eng.roar(850, 4000))


eng.sayHi()
sd.play(sound)
sd.wait()
