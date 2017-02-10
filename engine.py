import numpy as np
import scipy as sp


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

    WAVEFORM_DEFAULT = 1

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

            self.WAVEFORM_DEFAULT: self.getGaussianPulse()

        }.get(firing_waveform, "{} is not a known waveform".format(firing_waveform))

    # cycle is a vector of NC floats, each in [0 ,360]
    # each float is a firing event, NC = number of cylinders
    def buildCycle(self, my_type):
        return {
            self.TYPE_SINGLE: np.array([0]),
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
        punchedCard = cycle * convFactor + (120. / rpms)

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

            for sample in waveform:
                if self.my_type == self.TYPE_FLAT_4:
                    sound[initialSample + i] = sample * factor
                else:
                    sound[initialSample + i] = sample

                i += 1
        return sound

    def getGaussianPulse(self):
        fs = 44100
        f = 100
        duration = 0.03  # secs
        t = np.arange(44100 * duration) / fs
        var = 80
        sin1 = np.sin(2 * np.pi * f * t)
        top = 0.2
        ran = np.random.uniform(0 - top, top, int(sp.floor(44100 * duration)))

        src = sin1  # + ran
        sound = src * self.gaussian(t, 0.05 / fs, 1.0 / fs * var) + ran * self.gaussian(t, 0.05 / fs,
                                                                                        1.0 / fs * var * 3)
        return sound

    def gaussian(self, x, mu, sig):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
