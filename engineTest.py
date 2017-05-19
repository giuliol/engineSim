from engine import Engine
import sounddevice as sd


eng = Engine(Engine.TYPE_2STROKE_SINGLE, Engine.WAVEFORM_2STROKE)

sound = eng.rev(7500);

eng.sayHi()
sd.play(sound)
sd.wait()
