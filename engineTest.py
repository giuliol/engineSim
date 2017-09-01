from engine import Engine
import sounddevice as sd


eng = Engine(Engine.TYPE_V12, Engine.WAVEFORM_4STROKE)

sound = eng.rev(3000);

eng.sayHi()
sd.play(sound)
sd.wait()
