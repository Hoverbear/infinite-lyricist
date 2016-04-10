# USe as `bpm_of_file("tester.wav")`

import sys
import os

import numpy
import scipy.io.wavfile
import scipy.signal

BPM_MIN = 50
BPM_MAX = 210  # marsyas

OSS_WINDOWSIZE = 1024
OSS_HOPSIZE = 128

OSS_LOWPASS_CUTOFF = 7.0 # Hz
OSS_LOWPASS_N = 15

BH_WINDOWSIZE = 2048
BH_HOPSIZE = 128

BP_WINDOWSIZE = 2048
BP_HOPSIZE = 128

DOUBLE_TYPE = 2


OPTIONS_ONSET = 2
OPTIONS_BH = 2
OPTIONS_BP = 2

extra = []

def detect_bpm(filename):
    """
    Gets the BPM of a given file.
    """
    basename = os.path.splitext(os.path.basename(filename))[0]
    ### handle OSS
    wav_sr, wav_data = load_wavfile(filename)
    oss_sr, oss_data = onset_strength_signal(
        wav_sr, wav_data)

    ### handle Beat Histogram
    tempo_lags = beat_period_detection(
        oss_sr, oss_data)

    if OPTIONS_BP < 0:
        cands = numpy.zeros(4*BPM_MAX)
        for i in range(len(tempo_lags)):
            for j in range(len(tempo_lags[i])):
                bpm = tempo_lags[i][j]
                cands[bpm] += 9-j

        bestbpm = 4*cands.argmax()
        fewcands = []
        for i in range(4):
            bpm = cands.argmax()
            cands[bpm] = 0.0
            fewcands.append(4*bpm)
        return bestbpm, fewcands

    bpm = accumulator_overall(tempo_lags, oss_sr)

    return bpm #, tempo_lags[-1]

def load_wavfile(filename):
    """
    Loads a .wav file.
    """
    sample_rate, data_unnormalized = scipy.io.wavfile.read(filename)
    maxval = numpy.iinfo(data_unnormalized.dtype).max+1
    data_normalized = (numpy.array(data_unnormalized, dtype=numpy.float64)
        / float(maxval))
    return sample_rate, data_normalized



###
# Sliding Window construction.
###
def norm_shape(shape):
    """
    Normalize numpy array shapes so they're always expressed as a tuple,
    even for one-dimensional shapes.

    From http://www.johnvinyard.com/blog/?p=268

    Parameters
        shape - an int, or a tuple of ints

    Returns
        a shape tuple
    """
    try:
        i = int(shape)
        return (i,)
    except TypeError:
        # shape was not a number
        pass

    try:
        t = tuple(shape)
        return t
    except TypeError:
        # shape was not iterable
        pass

    raise TypeError('shape must be an int, or a tuple of ints')

def sliding_window(a,ws,ss = None,flatten = True):
    '''
    Return a sliding window over a in any number of dimensions

    Parameters:
        a  - an n-dimensional numpy array
        ws - an int (a is 1D) or tuple (a is 2D or greater) representing the
            size of each dimension of the window
        ss - an int (a is 1D) or tuple (a is 2D or greater) representing the
             amount to slide the window in each dimension. If not specified, it
             defaults to ws.
        flatten - if True, all slices are flattened, otherwise, there is an
             extra dimension for each dimension of the inumpyut.

    Returns
        an array containing each n-dimensional window from a
    '''

    if None is ss:
        # ss was not provided. the windows will not overlap in any
        # direction.
        ss = ws
    ws = norm_shape(ws)
    ss = norm_shape(ss)

    # convert ws, ss, and a.shape to numpy arrays so that we can
    # do math in every
    # dimension at once.
    ws = numpy.array(ws)
    ss = numpy.array(ss)
    shape = numpy.array(a.shape)


    # ensure that ws, ss, and a.shape all have the same number of
    # dimenclass Defs:
    """
    Defines some options for the script.
    """
    def __init__(self):sions
    ls = [len(shape),len(ws),len(ss)]
    if 1 != len(set(ls)):
        raise ValueError('a.shape, ws and ss must all have the same length. The were %s' % str(ls))

    # ensure that ws is smaller than a in every dimension
    if numpy.any(ws > shape):
        raise ValueError('ws cannot be larger than a in any dimension. a.shape was %s and ws was %s' % (str(a.shape),str(ws)))

    # how many slices will there be in each dimension?
    newshape = norm_shape(((shape - ws) // ss) + 1)
    # the shape of the strided array will be the number of slices
    # in each dimension
    # plus the shape of the window (tuple addition)
    newshape += norm_shape(ws)
    # the strides tuple will be the array's strides multiplied by
    # step size, plus
    # the array's strides (tuple addition)
    newstrides = norm_shape(numpy.array(a.strides) * ss) + a.strides
    strided = numpy.lib.stride_tricks.as_strided(a,shape = newshape,strides = newstrides)
    if not flatten:
        return strided

    # Collapse strided so that it has one more dimension than the
    # window.  I.e.,
    # the new array is a flat list of slices.
    meat = len(ws) if ws.shape else 0
    firstdim = (numpy.product(newshape[:-meat]),) if ws.shape else ()
    dim = firstdim + (newshape[-meat:])
    # remove any dimensions with size 1
    #dim = filter(lambda i : i != 1,dim)
    return strided.reshape(dim)



###
# Onset Strength
###
def marsyas_hamming(N):
    ns = numpy.arange(N)
    hamming = 0.54 - 0.46 * numpy.cos( 2*numpy.pi*ns / (N-1.0))
    return hamming

def onset_strength_signal(wav_sr, wav_data):
    ### overlapping time data
    # add extra window of zeros at beginning to match marsyas
    overlapped = sliding_window(
        numpy.append(
            numpy.zeros(OSS_WINDOWSIZE - OSS_HOPSIZE),
            wav_data),
        OSS_WINDOWSIZE, OSS_HOPSIZE)
    oss_sr = wav_sr / float(OSS_HOPSIZE)

    if OPTIONS_ONSET == 0:
        rms = numpy.sqrt( numpy.mean(overlapped**2, axis=1))
        return oss_sr, rms


    windowed = overlapped * marsyas_hamming(
        OSS_WINDOWSIZE)

    ### log-magnitude of FFT
    ffts = scipy.fftpack.fft(windowed, OSS_WINDOWSIZE, axis=1)
    ffts_abs = abs(ffts)[:,:ffts.shape[1]/2 + 1]

    # extra scaling to match Marsyas FFT output
    ffts_abs /= OSS_WINDOWSIZE
    logmag = numpy.log(1.0 + 1000.0 * ffts_abs)

    ### flux
    flux = numpy.zeros( ffts_abs.shape[0] ) # output time signal
    prev = numpy.zeros( ffts_abs.shape[1] )
    for i in xrange( 0, ffts_abs.shape[0] ):
        diff = logmag[i] - prev
        diffreduced = diff[1:] # to match Marsyas
        diffclipped = diffreduced.clip(min=0)
        prev = numpy.copy(logmag[i])
        flux[i] = sum(diffclipped)

    if OPTIONS_ONSET == 1:
        return oss_sr, flux

    ### filter
    if OSS_LOWPASS_CUTOFF > 0 and OPTIONS_ONSET < 3:
        b = scipy.signal.firwin(OSS_LOWPASS_N,
            OSS_LOWPASS_CUTOFF / (oss_sr/2.0) )
        filtered_flux = scipy.signal.lfilter(b, 1.0, flux)
    else:
        filtered_flux = flux


    ts = numpy.arange( len(filtered_flux) ) / oss_sr

    num_bh_frames = int(len(filtered_flux) / BH_HOPSIZE)
    filtered_flux = filtered_flux[:num_bh_frames * BH_HOPSIZE]

    return oss_sr, filtered_flux



###
# Beat Period Detection
###
def autocorrelation(signal):
    """ this matches Marsyas exactly. """
    N = signal.shape[1]
    ffts = scipy.fftpack.fft(signal, 2*N, axis=1) / (2*N)
    ffts_abs = abs(ffts)
    ffts_abs_scaled = ffts_abs**0.5
    scratch = (scipy.fftpack.ifft(ffts_abs_scaled, axis=1
        ).real)*(2*N)
    xcorr = scratch[:,:N]
    return xcorr


def find_peaks(signal, number=10, peak_neighbors=1,
        minsample=0, maxsample=None):
    candidates = []
    if maxsample is None:
        maxsample = len(signal)

    for i in xrange(minsample+peak_neighbors,
            maxsample - peak_neighbors-1):
        if signal[i-1] < signal[i] > signal[i+1]:
            ok = True
            for j in xrange(i-peak_neighbors, i):
                if signal[j] >= signal[i]:
                    ok = False
            for j in xrange(i+1, i+peak_neighbors):
                if signal[j] >= signal[i]:
                    ok = False
            if ok:
                candidates.append( (signal[i], i) )
    candidates.sort(reverse=True)

    peaks = []
    for c in candidates[:number]:
        index = c[1]
        peaks.append(index)
    return numpy.array(peaks)

def autocorr_index_to_bpm(index, oss_sr):
    return 60.0*oss_sr / index

def bpm_to_autocorr_index(bpm, oss_sr):
    return 60.0*oss_sr / bpm


def calc_pulse_trains(lag, window, sr):
    period = lag
    num_offsets = period
    samples = len(window)

    bp_mags = numpy.zeros( num_offsets )
    for phase in range(samples-1, samples-1-period, -1):
        mag = 0.0
        for b in range(4):
            ind = int(phase - b*period)
            # this is I_{ P, phi, 1)
            if ind >= 0:
                mag += window[ind]

            # this is I_{ P, phi, 2)
            # slow down by 2
            ind = int(phase - b*period*2)
            if ind >= 0:
                mag += 0.5*window[ind]

            # this is I_{ P, phi, 1.5)
            # slow down by 3
            ind = int(phase - b*period*3/2)
            if ind >= 0:
                mag += 0.5*window[ind]
        bp_mags[samples-1-phase] = mag
    bp_max = max(bp_mags)
    bp_var = numpy.var(bp_mags)
    return bp_max, bp_var


def beat_period_detection(oss_sr, oss_data, plot=False):
    ### 1) Overlap
    overlapped = sliding_window(
        oss_data,
        BH_WINDOWSIZE, BH_HOPSIZE)

    ### 2) Generalized Autocorrelation
    autocorr = autocorrelation(overlapped)

    minlag = int(oss_sr*60.0 / BPM_MAX)
    maxlag = int(oss_sr*60.0 / BPM_MIN) + 1

    num_frames = autocorr.shape[0]

    ### 3) Enhance Harmonics
    harmonic_enhanced = numpy.zeros( autocorr.shape )
    for i in xrange( num_frames ):
        auto = autocorr[i]
        stretched = numpy.zeros( BH_WINDOWSIZE )
        for j in xrange( 512 ):
            stretched[j] = auto[2*j] + auto[4*j]
        harmonic_enhanced[i] = (
            auto + stretched
            )

    ### 4) Pick peaks
    peaks = numpy.zeros( (num_frames, 10) )
    for i in xrange( num_frames ):
        these_peaks = find_peaks(harmonic_enhanced[i],
            number=10, peak_neighbors=1, minsample=minlag,
            maxsample=maxlag)
        peaks[i,:] = these_peaks

    ### 5) Evaluate pulse trains
    tempo_lags = numpy.zeros(num_frames)
    for i in xrange(num_frames):
        cands = peaks[i]
        onset_scores = numpy.zeros(len(cands))
        tempo_scores = numpy.zeros(len(cands))
        for j, cand in enumerate(cands):
            if cand == 0:
                continue
            lag = int(round(cand))
            mag, var = calc_pulse_trains(lag, overlapped[i], oss_sr)
            tempo_scores[j] = mag
            onset_scores[j] = var
        tempo_scores /= tempo_scores.sum()
        onset_scores /= onset_scores.sum()

        combo_scores = tempo_scores + onset_scores
        combo_scores /= combo_scores.sum()

        # find best score
        besti = combo_scores.argmax()
        bestlag = round(cands[besti])

        tempo_lags[i] = bestlag

    return tempo_lags



###
# Accumulator Overall
###
def energy_in_histo_range(histo, low, high):
    index_low = round(low)
    index_high = round(high)
    if high == 1:
        index_high = len(histo)-1
    if high > len(histo)-1:
        high = len(histo)-1
    if low < 0:
        low = 0
    return sum(histo[int(index_low):int(index_high+1)])


def info_histogram(bpm, histo, tolerance):
    energy_total = energy_in_histo_range(histo, 0, 1.0)
    energy_under = energy_in_histo_range(histo,
        0, bpm - tolerance) / energy_total

    str05 = energy_in_histo_range(histo,
        0.5*bpm-tolerance, 0.5*bpm+tolerance) / energy_total

    info = [ energy_under, str05 ]
    return info



def accumulator_overall(tempo_lags, oss_sr):
    pdf = scipy.stats.norm.pdf(numpy.arange(2000)-1000, loc=0,
        scale=10)

    ### 1) convert to Gaussian, and
    ### 2) Accumulator (sum)
    accum = numpy.zeros(414)
    for lag in tempo_lags:
        begin = 1000-lag
        end = 1000-lag+414
        accum += pdf[int(begin):int(end)]

    ### 3) Pick peak
    tempo_lag = numpy.argmax(accum)
    bpm = oss_sr*60 / tempo_lag

    ### Octave Decider
    mult = 1.0
    if DOUBLE_TYPE == 1:
        if bpm <= 71.9:
            mult = 2.0
    elif DOUBLE_TYPE == 2:
        features = info_histogram(tempo_lag, accum, 10)
        features.append(bpm)
        ## hard-coded values trained elsewhere; see tempo.cpp
        mins = [ 0.0321812, 1.68126e-83, 50.1745, ]
        maxs = [ 0.863237, 0.449184, 208.807, ]
        svm_weights51 = numpy.array([
            -1.9551, 0.4348, -4.6442, 3.2896
        ])
        svm_weights52 = numpy.array([
             -3.0408, 2.7591, -6.5367, 3.081
        ])
        svm_weights12 = numpy.array([
            -3.4624, 3.4397, -9.4897, 1.6297
        ])

        # normalize
        features_normalized = numpy.array(features)
        for i in range(len(features)):
            features_normalized[i] = (features[i] - mins[i]) / (maxs[i] - mins[i])

        # svm
        svm_sum51 = svm_weights51[-1] + numpy.dot(
            features_normalized, svm_weights51[:-1])
        svm_sum52 = svm_weights52[-1] + numpy.dot(
            features_normalized, svm_weights52[:-1])
        svm_sum12 = svm_weights12[-1] + numpy.dot(
            features_normalized, svm_weights12[:-1])
        if (svm_sum52 > 0) and (svm_sum12 > 0):
            mult = 2.0
        if (svm_sum51 <= 0) and (svm_sum52 <= 0):
            mult = 0.5

    return mult*bpm
