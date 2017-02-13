import numpy as np
import scipy as sp
# import matplotlib.pyplot as plt


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
    TYPE_BIG_BANG_4 = 16
    TYPE_V4_VFR = 17
    WAVEFORM_4STROKE = 1
    WAVEFORM_2STROKE = 2

    my_type = -1

    REV_DURATION = 3000
    REVS_IDLE = 850

    FS = 44100

    def __init__(self, engine_type, firing_waveform):
        self.my_type = engine_type
        self.waveform = self.getWaveForm(firing_waveform)

    def sayHi(self):
        print("hi! I'm an engine!")


    def rev(self, top):
        # cycle is a vector of NC floats, each in [0 ,720]
        # each float is a firing event, NC = number of cylinders
        cycle = self.buildCycle(self.my_type)

        # punchedCard is a vector of NC * rpms /60 * milliseconds/1000 firing events.
        # Each is a time coordinate in ms
        punchedCard = self.spin(cycle, top, self.REV_DURATION)

        # sound is a vector containing sound samples (in [-1,1])
        sound = self.render(punchedCard, self.FS, self.waveform)

        return sound

    def roar(self, rpms, milliseconds):

        # cycle is a vector of NC floats, each in [0 ,720]
        # each float is a firing event, NC = number of cylinders
        cycle = self.buildCycle(self.my_type)

        # punchedCard is a vector of NC * rpms /60 * milliseconds/1000 firing events.
        # Each is a time coordinate in ms
        punchedCard = self.steady(cycle, rpms, milliseconds)

        # sound is a vector containing sound samples (in [-1,1])
        sound = self.render(punchedCard, self.FS, self.waveform)

        return sound

    def getWaveForm(self, firing_waveform):
        return {

            self.WAVEFORM_4STROKE: 0.7*self.getGaussianPulse(80, 0.008, 600, 8) + 0.7*self.getGaussianPulse(250, 0.05, 100, 5) + 0.05*self.getGaussianPulse(560, 0.0, 350, 5),
            self.WAVEFORM_2STROKE: 0.3*self.getGaussianPulse(80, 0.018, 300, 8) + self.getGaussianPulse(450, 0.18, 150, 5)

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
            self.TYPE_BIG_BANG_4: np.array([0, 90, 180, 630]),
            self.TYPE_V4_VFR: np.array([0, 90, 180, 630]),
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

    def steady(self, cycle, rpms, milliseconds):
        nCycles = 1
        duration = 0
        convFactor = 120. / (720. * rpms)
        punchedCard = np.array(())

        ran = 1;
        while duration < milliseconds / 1000.:
            # events = np.vstack((events, cycle + (120. / rpms)))
            punchedCard = np.append(punchedCard, cycle * convFactor + (120. / (rpms * ran)) * nCycles)
            ran = 0.95*ran + 0.05*np.random.uniform(0.9, 1.1, 1)

            nCycles += 1
            duration += 120. / rpms

        return punchedCard

    def spin(self, cycle, top, REV_DURATION):

        duration = 0
        punchedCard = np.array(())
        rpms = self.REVS_IDLE
        ran = 1;
        nCycles = 1

        while duration < top / 1000.:
            convFactor = 120. / (720. * rpms)
            ran = 0.95*ran + 0.05*np.random.uniform(0.9, 1.1, 1)
            punchedCard = np.append(punchedCard, cycle * convFactor + (120. / (rpms * ran)) * nCycles)
            nCycles += 1
            duration += 120. / rpms
            rpms = min(1.012*rpms, top)
            print(rpms)

        return punchedCard

    # todo
    # sound is a vector containing sound samples (in [-1,1])
    def render(self, punchedCard, FS, waveform):
        pulseLength = len(waveform) / FS
        soundSamples = int(sp.ceil(punchedCard[-1] * FS + len(waveform)))
        sound = np.zeros([soundSamples*2, 1])

        rrll = 0
        factor = 1
        ran = 1
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

            ran = 0.5*ran + 0.5*np.random.uniform(0.7, 1.3, 1)

            for sample in waveform:
                if self.my_type == self.TYPE_FLAT_4:
                    sound[initialSample + i] += sample * factor * ran
                else:
                    sound[initialSample + i] += sample * ran
                sound[initialSample + 1] = max(min(sound[initialSample + 1], 2), -2)
                i += 1
        trim = 15000
        return sound[:-trim]

    def getGaussianPulse(self, f, noise_amplitude, gaussian_var, noise_var):
        fs = 44100
        # f = 200
        duration = 0.08  # secs
        t = np.arange(44100 * duration) / fs
        sin1 = np.sin(2 * np.pi * f * t)
        # top = 0.18
        ran = np.random.uniform(0 - noise_amplitude, noise_amplitude, int(sp.floor(44100 * duration)))

        src = sin1  # + ran
        sound = src * self.gaussian(t, 0.05 / fs, 1.0 / fs * gaussian_var) + ran * self.gaussian(t, 0.05 / fs,
                                                                                        1.0 / fs * gaussian_var * noise_var)

        print(sound.shape)
        echos = np.zeros([len(sound) * 2])
        print(echos.shape)
        echosTimes = np.array(
            [0, duration / 5.5637, 3.2 * duration / 5.5847, 2.5 * duration / 5.412, 5 * duration / 5.412])
        echosFactors = [1, 0.3, 0.15, 0.1, 0.1]
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
        # echoed = np.convolve(sound, echos)
        # plt.plot(echos, 'g')
        # plt.plot(sound, 'r')
        # plt.plot(echoed, 'b')
        # plt.show()
        return np.convolve(sound, echos)

    def gaussian(self, x, mu, sig):
        return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

    def smooth(x, window_len=11, window='hanning'):
        """smooth the data using a window with requested size.

        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.

        input:
            x: the input signal
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.

        output:
            the smoothed signal

        example:

        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)

        see also:

        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter

        TODO: the window parameter could be the window itself if an array instead of a string
        NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
        """

        if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
            raise ValueError("Input vector needs to be bigger than window size.")

        if window_len < 3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

        s = np.r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]
        # print(len(s))
        if window == 'flat':  # moving average
            w = np.ones(window_len, 'd')
        else:
            w = eval('numpy.' + window + '(window_len)')

        y = np.convolve(w / w.sum(), s, mode='valid')
        return y



