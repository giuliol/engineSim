import numpy as np
import scipy as sp


# import matdplotlib.pyplot as plt

class Engine:
    TYPE_SINGLE = 1
    TYPE_PARALLEL_TWIN = 2
    TYPE_V90_TWIN = 3
    TYPE_V60_TWIN = 4
    TYPE_INLINE_4 = 5
    TYPE_V8_CROSSPLANE = 6
    TYPE_V8_FLATPLANE = 7
    TYPE_FLAT_4 = 8
    TYPE_RS_250 = 9
    TYPE_INLINE_5 = 10
    TYPE_INLINE_3 = 11
    TYPE_INLINE_6 = 12
    TYPE_V12 = 13
    TYPE_INLINE_4_CROSSPLANE = 14
    TYPE_2STROKE_SINGLE = 15
    TYPE_BIG_BANG_4 = 16
    TYPE_V4_VFR = 17

    WAVEFORM_4STROKE = 1
    WAVEFORM_2STROKE = 2

    my_arch = -1
    twoStroke = False

    REV_DURATION = 12000
    REVS_IDLE = 1000

    FS = 44100

    def __init__(self, engine_type, firing_waveform):
        self.my_arch = engine_type
        self.waveform = self.getWaveForm(firing_waveform, self.FS) - np.mean(self.getWaveForm(firing_waveform, self.FS))
        if firing_waveform == self.WAVEFORM_2STROKE:
            self.twoStroke = True
        else:
            self.twoStroke = False
        # from matplotlib import pyplot as plt
        # plt.plot(np.arange(len(self.waveform)) / self.FS, self.waveform)
        # plt.show()

    def sayHi(self):
        print("hi! I'm an engine!")

    def rev(self, top):
        # cycle is a vector of NC floats, each in [0 ,720]
        # each float is a firing event, NC = number of cylinders
        cycle = self.buildCycle(self.my_arch)
        print(cycle)

        # punchedCard is a vector of NC * rpms /60 * milliseconds/1000 firing events.
        # Each is a time coordinate in ms
        punchedCard = self.spin(cycle, top, self.REV_DURATION)

        # sound is a vector containing sound samples (in [-1,1])
        import matplotlib.pyplot as plt
        # plt.plot(punchedCard, np.ones(punchedCard.shape), 'rd')
        # plt.show()
        sound = self.render(punchedCard, self.FS, self.waveform)
        # print("sound is {}".format(len(sound)))
        # plt.plot(np.arange(0, len(sound))/self.FS , sound)
        # plt.show()
        return sound

    def getWaveForm(self, firing_waveform, fs):
        return {
            self.WAVEFORM_4STROKE:
                0.73 * self.getGaussianPulse(80, fs, 0.008, 600, 2) +
                0.18 * self.getGaussianPulse(250, fs, 0.03, 200, 5) +
                0.05 * self.getGaussianPulse(560, fs, 0.0, 350, 5),

            self.WAVEFORM_2STROKE:
                0.3 * self.getGaussianPulse(80, fs, 0.018, 300, 8) +
                self.getGaussianPulse(450, fs, 0.18, 150, 5)

        }.get(firing_waveform, "{} is not a known waveform".format(firing_waveform))

    # cycle is a vector of NC floats, each in [0, 720]
    # each float is a firing event, NC = number of cylinders
    def buildCycle(self, my_type):
        return {
            self.TYPE_SINGLE: np.array([0]),
            self.TYPE_2STROKE_SINGLE: np.array([0, 360]),
            self.TYPE_PARALLEL_TWIN: np.array([0, 360]),
            self.TYPE_V90_TWIN: np.array([0, 270]),
            self.TYPE_V60_TWIN: np.array([0, 420]),
            self.TYPE_INLINE_4: np.array([0, 180, 360, 540]),
            self.TYPE_BIG_BANG_4: np.array([0, 90, 180, 630]),
            self.TYPE_V4_VFR: np.array([0, 90, 180, 630]),
            self.TYPE_FLAT_4: np.array([0, 180, 405, 585]),
            self.TYPE_V8_FLATPLANE: np.array([0, 90, 180, 270, 360, 450, 540, 630]),  # not sure
            self.TYPE_V8_CROSSPLANE: np.array([0, 90, 270, 360, 360, 450, 630, 720]),
            self.TYPE_RS_250: np.array([0, 90, 360, 450]),
            self.TYPE_INLINE_5: np.array([0, 144, 288, 432, 576]),
            self.TYPE_INLINE_3: np.array([0, 240, 480]),
            self.TYPE_INLINE_6: np.array([0, 120, 240, 360, 480, 600]),
            self.TYPE_V12: np.array([0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660]),
            self.TYPE_INLINE_4_CROSSPLANE: np.array([0, 270, 360, 630])

        }.get(my_type, "{} is not a known engine layout".format(my_type))

    # punchedCard is a vector of NC * rpms / 2 / 60 * milliseconds/1000 firing events.
    # Each is a time coordinate in ms
    def steady(self, cycle, rpms, milliseconds):
        punchedCard = np.array(())
        punchedCard = np.append(punchedCard, 0)
        nCycles = 0
        lastOne = 0

        # print("cycle {}".format(cycle))
        while punchedCard[-1] < milliseconds / 1000.:
            convFactor = 120. / (720. * rpms)
            punchedCard = np.append(punchedCard, cycle * convFactor + lastOne)
            lastOne = lastOne + 60. / rpms;
            nCycles += 1

        return punchedCard

    def spin(self, cycle, limiter, REV_DURATION):
        # creates the rpm profile.
        # Engine rpms are controlled similarly to reality, open throttle increases rpms exponentially, until limiter.
        # Closed throttle decreases them also exponentially, until idle.

        punchedCard = np.array(())
        punchedCard = np.append(punchedCard, 0)
        rpms = self.REVS_IDLE
        nCycles = 0
        lastOne = 0
        ran = 1
        rpmhistory = np.array(())
        while punchedCard[-1] < REV_DURATION / 1000.:
            convFactor = 120. / (720. * rpms)
            ran = 0.9 * ran + 0.1 * np.random.uniform(0.9, 1.1, 1)
            punchedCard = np.append(punchedCard, cycle * convFactor + lastOne)
            lastOne += 120. / rpms
            nCycles += 1

            # if between 1/3 and 2/3 of the simulation, open throttle
            if 2. / 3. * REV_DURATION / 1000. > punchedCard[-1] > 1. / 3. * REV_DURATION / 1000.:
                rpms = min(1.077 * rpms, limiter) * ran

            # ...otherwise, close the throttle!
            else:
                # two strokes have less mechanical resistance,
                # effective flywheel mass is enough to counteract internal friction longer
                # -> rpms drop slower when closing throttle.
                if self.twoStroke:
                    rpms = max(0.96 * rpms, self.REVS_IDLE) * ran
                else:
                    rpms = max(0.87 * rpms, self.REVS_IDLE) * ran

            rpmhistory = np.append(rpmhistory, rpms)

        from matplotlib import pyplot as plt
        # plt.plot(punchedCard, np.ones(punchedCard.shape), 'rd')
        # plt.plot(rpmhistory)
        # plt.show()

        return punchedCard

    # todo
    # sound is a vector containing sound samples (in [-1,1])
    def render(self, punchedCard, FS, waveform):
        pulseLength = len(waveform) / FS
        soundSamples = int(sp.ceil(punchedCard[-1] * FS + len(waveform)))
        sound = np.zeros([int(soundSamples * 1.2), 1])

        rrll = 0
        factor = 1
        ran = 1
        for punch in punchedCard:
            initialSample = int(punch * FS)
            i = 0
            rrll += 1
            if rrll == 2:
                if factor == 1:
                    factor = 0.9
                else:
                    factor = 1
                rrll = 0

            ran = 0.5 * ran + 0.5 * np.random.uniform(0.8, 1.2, 1)
            # ran =1
            shape = sound[initialSample:initialSample + len(waveform)].shape
            if self.my_arch == self.TYPE_FLAT_4:
                sound[initialSample:initialSample + len(waveform)] += np.reshape(waveform * factor * ran, shape)
            else:
                sound[initialSample:initialSample + len(waveform)] += np.reshape(waveform * ran, shape)

        trim = 15000
        # from matplotlib import pyplot as plt
        # plt.plot(sound)
        # plt.show()
        return sound[:-trim]

    def getGaussianPulse(self, f, fs, noise_amplitude, gaussian_var, noise_var):
        # f = 200
        duration = 0.08  # secs
        t = np.arange(44100 * duration) / fs
        sin1 = np.sin(2 * np.pi * f * t)
        # top = 0.18
        ran = np.random.uniform(0 - noise_amplitude, noise_amplitude, int(sp.floor(44100 * duration)))

        src = sin1  # + ran
        sound = src * self.gaussian(t, 0.05 / fs, 1.0 / fs * gaussian_var) + ran * self.gaussian(t, 0.05 / fs,
                                                                                                 1.0 / fs * gaussian_var * noise_var)

        # print(sound.shape)
        echos = np.zeros([len(sound) * 2])
        # print(echos.shape)
        echosTimes = np.array(
            [0, duration / 5.5637, 3.2 * duration / 5.5847, 2.5 * duration / 5.412, 5 * duration / 5.412])
        echosFactors = [1, 0.3, 0.15, 0.1, 0.1]
        echosIndexes = echosTimes * fs
        i = 0
        # print(echosTimes)
        # print(echosIndexes)
        for factor in echosFactors:
            # print(echosIndexes[i])
            # print(i)
            # print(type(echos[int(echosIndexes[i])]))
            echos[int(echosIndexes[i])] = factor
            i += 1

        # print(len(echos))
        # print(len(sound))
        #
        # print(echos[echos != 0])
        # echoed = np.convolve(sound, echos)
        # plt.plot(echos, 'g')
        # plt.plot(sound, 'r')
        # plt.plot(echoed, 'b')
        # plt.show()
        return np.convolve(sound, echos)
        # return sound

    def gaussian(self, x, mu, sig):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
