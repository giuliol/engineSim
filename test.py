import sounddevice as sd
from pylab import *


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))




fs = 44100
f = 100
duration = 0.03 # secs
t = np.arange(44100*duration)/fs
var = 80
sin1 = np.sin(2 * np.pi * f * t)
top = 0.2
ran = np.random.uniform(0-top,top,int(floor(44100*duration)))

src = sin1 # + ran
sound = src * gaussian(t, 0.05 / fs , 1 / fs * var) + ran * gaussian(t, 0.05 / fs , 1 / fs * var *3)
# sd.play(sound, fs)

# plt.plot(t,sound)
# plt.show()

target = 3
rumble = np.zeros([1,target*fs])

i = 0

print(len(rumble[0]))
a = 0

while i < len(rumble[0])-len(sound):
    for sample in sound:
        rumble[0,i] += sample
        i += 1
    if a==0:
        i -= int(ceil(len(sound)/15))
        a = 1
    else:
        i -= int(ceil(len(sound)/2))
        a = 0
# plt.plot(rumble.flatten())
# plt.show()

sd.play(rumble.flatten())
sd.wait()

sd.play(rumble.flatten(),fs*1.5)
sd.wait()

# sd.play(rumble.flatten(),fs*3)
# sd.wait()


