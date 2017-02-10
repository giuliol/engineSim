import numpy as np
import scipy as sp
import matplotlib.pyplot as plt


class Engine:
    TYPE_SINGLE = 1
    TYPE_PARALLEL_TWIN = 2
    TYPE_V90_TWIN = 3
    TYPE_V60_TWIN = 4
    TYPE_INLINE_4 = 5
    # TYPE_V8_CROSSPLANE = 6
    TYPE_V8_FLATPLANE = 7
    TYPE_FLAT_4 = 8
    TYPE_RS_250 = 9
    TYPE_INLINE_5 = 10
    TYPE_INLINE_3 = 11
    TYPE_INLINE_6 = 12
    TYPE_V12 = 13
    TYPE_INLINE_4_CROSSPLANE = 14
    TYPE_2STROKE_SINGLE = 15

    WAVEFORM_4STROKE = 1
    WAVEFORM_2STROKE = 2

    my_type = -1

    FS = 44100

    def __init__(self, engine_type, firing_waveform):
        self.my_type = engine_type
        self.waveform = self.getWaveForm(firing_waveform)

    def sayHi(self):
        print("hi! I'm an engine!")

    def roar(self, rpms, milliseconds):

        # cycle is a vector of NC floats, each in [0 ,720]
        # each float is a firing event, NC = number of cylinders
        cycle = self.buildCycle(self.my_type)

        # punchedCard is a vector of NC * rpms /60 * milliseconds/1000 firing events.
        # Each is a time coordinate in ms
        punchedCard = self.spin(cycle, rpms, milliseconds)

        # sound is a vector containing sound samples (in [-1,1])
        sound = self.render(punchedCard, self.FS, self.waveform)

        return sound

    def getWaveForm(self, firing_waveform):
        return {

            self.WAVEFORM_4STROKE: self.getGaussianPulse(150, 0.018, 8),
            self.WAVEFORM_2STROKE: self.getGaussianPulse(220, 0.2, 8)

        }.get(firing_waveform, "{} is not a known waveform".format(firing_waveform))

    # cycle is a vector of NC floats, each in [0 ,360]
    # each float is a firing event, NC = number of cylinders
    def buildCycle(self, my_type):
        return {
            self.TYPE_SINGLE: np.array([0]),
            self.TYPE_2STROKE_SINGLE: np.array([0, 360]),
            self.TYPE_PARALLEL_TWIN: np.array([0, 180]),
            self.TYPE_V90_TWIN: np.array([0, 270]),
            self.TYPE_V60_TWIN: np.array([0, 420]),
            self.TYPE_INLINE_4: np.array([0, 180, 360, 540]),
            self.TYPE_FLAT_4: np.array([0, 180, 360, 540]),
            self.TYPE_V8_FLATPLANE: np.array([0, 90, 180, 270, 360, 450, 540, 630]),  # not sure
            # self.TYPE_V8_CROSSPLANE: np.array([0, 180, 360, 540]),
            self.TYPE_RS_250: np.array([0, 90, 360, 450]),
            self.TYPE_INLINE_5: np.array([0, 144, 288, 432, 576]),
            self.TYPE_INLINE_3: np.array([0, 240, 480]),
            self.TYPE_INLINE_6: np.array([0, 120, 240, 360, 480, 600]),
            self.TYPE_V12: np.array([0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660]),
            self.TYPE_INLINE_4_CROSSPLANE: np.array([0, 270, 360, 630])

        }.get(my_type, "{} is not a known engine layout".format(my_type))

        # punchedCard is a vector of NC * rpms / 2 / 60 * milliseconds/1000 firing events.
        # Each is a time coordinate in ms

    def spin(self, cycle, rpms, milliseconds):
        nCycles = 1
        duration = 0
        convFactor = 120. / (720. * rpms)
        punchedCard = np.array(())

        while duration < milliseconds / 1000.:
            # events = np.vstack((events, cycle + (120. / rpms)))
            punchedCard = np.append(punchedCard, cycle * convFactor + (120. / rpms) * nCycles)
            nCycles += 1
            duration += 120. / rpms

        return punchedCard

    # todo
    # sound is a vector containing sound samples (in [-1,1])
    def render(self, punchedCard, FS, waveform):
        pulseLength = len(waveform) / FS
        soundSamples = int(sp.ceil(punchedCard[-1] * FS + len(waveform)))
        sound = np.zeros([soundSamples, 1])

        rrll = 0
        factor = 1
        for punch in punchedCard:
            initialSample = int(punch * FS)
            i = 0
            rrll += 1
            if rrll == 2:
                if factor == 0.35:
                    factor = 1.0
                else:
                    factor = 0.35
                rrll = 0

            ran = np.random.uniform(0.8, 1.1, 1)
            for sample in waveform:
                if self.my_type == self.TYPE_FLAT_4:
                    sound[initialSample + i] += sample * factor * ran
                else:
                    sound[initialSample + i] += sample * ran

                i += 1
        trim = 13000
        return sound[:-trim]

    def getGaussianPulse(self, f, noise_amplitude, noise_var):
        fs = 44100
        # f = 200
        duration = 0.08  # secs
        t = np.arange(44100 * duration) / fs
        var = 80
        sin1 = np.sin(2 * np.pi * f * t)
        # top = 0.18
        ran = np.random.uniform(0 - noise_amplitude, noise_amplitude, int(sp.floor(44100 * duration)))

        src = sin1  # + ran
        sound = src * self.gaussian(t, 0.05 / fs, 1.0 / fs * var) + ran * self.gaussian(t, 0.05 / fs,
                                                                                        1.0 / fs * var * noise_var)

        print(sound.shape)
        echos = np.zeros([len(sound) * 2])
        print(echos.shape)
        echosTimes = np.array(
            [0, duration / 5.5637, 3.2 * duration / 5.5847, 2.5 * duration / 5.412, 5 * duration / 5.412])
        echosFactors = [1, 0.2, 0.1, 0.15, 0.07]
        echosIndexes = echosTimes * fs
        i = 0
        print(echosTimes)
        print(echosIndexes)
        for factor in echosFactors:
            # print(echosIndexes[i])
            print(i)
            print(type(echos[int(echosIndexes[i])]))
            echos[int(echosIndexes[i])] = factor
            i += 1

        print(len(echos))
        print(len(sound))

        print(echos[echos != 0])
        echoed = np.convolve(sound, echos)
        # plt.plot(echos, 'g')
        # plt.plot(sound, 'r')
        # plt.plot(echoed, 'b')
        # plt.show()
        return echoed

    def gaussian(self, x, mu, sig):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
