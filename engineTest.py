from engine import Engine
import sounddevice as sd


eng = Engine(Engine.TYPE_V90_TWIN, Engine.WAVEFORM_4STROKE)

sound = eng.rev(6000)

eng.sayHi()
sd.play(sound, eng.FS)
sd.wait()
