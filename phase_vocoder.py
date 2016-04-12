import marsyas
from copy import deepcopy


default_options = {
	'music_file': None,
	'N': 1024,
	'Nw': 1024,
	'D': 16,
	'I': 16,
	'P': 1.0,
	'unconvertmode_': 'classic',
	'convertmode_': 'sorted',
	'multires_': False,
	'multiresMode_': "transient_switch",
	'bopt': 320,
	'outfile': None,
	'sopt': (44100 / 2) / 80 # Number of harmonics of F0=80Hz represented by audio at a sample rate of 44100
}

def time_shift(**args):

	options = deepcopy(default_options)

	for arg in args:
		options[arg] = args[arg]

	outfile = options['outfile']


	mng = marsyas.MarSystemManager()
	pvseries = marsyas.system_from_script_file("./marsystems/time-shift.mrs")

	pvseries.updControl("mrs_string/file", options['music_file'])
	pvseries.updControl("mrs_string/outfile", outfile)


	pvseries.updControl("mrs_real/israte", 44100.0)
	pvseries.updControl("mrs_real/osrate", 44100.0)
	pvseries.updControl("mrs_natural/inSamples", options['D'])
	pvseries.updControl("mrs_natural/onSamples", options['I'])



	pvseries.updControl("SoundFileSource/src/mrs_natural/onSamples", options['D'])
	pvseries.updControl("mrs_natural/inObservations", 1)



	pvseries.updControl("ShiftInput/si/mrs_natural/winSize", options['Nw'])

	pvseries.updControl("PvFold/fo/mrs_natural/FFTSize", options['N'])

	pvseries.updControl("PvConvert/conv/mrs_natural/Decimation", options['D'])
	pvseries.updControl("PvConvert/conv/mrs_natural/Sinusoids", options['sopt'])
	pvseries.updControl("PvConvert/conv/mrs_string/mode", options['convertmode_'])

	pvseries.updControl("mrs_natural/onStabilizingDelay", 63)

	pvseries.updControl("SoundFileSource/src/mrs_natural/onObservations", 2)
	pvseries.updControl("SoundFileSource/src/mrs_natural/inSamples", options['D'])
	pvseries.updControl("SoundFileSource/src/mrs_natural/onSamples", options['D'])

	pvseries.updControl("ShiftInput/si/mrs_natural/onSamples", options['Nw'])
	pvseries.updControl("ShiftInput/si/mrs_real/israte", 44100.0)
	pvseries.updControl("ShiftInput/si/mrs_real/osrate", 44100.0)

	pvseries.updControl("ShiftInput/si/mrs_natural/onObservations", 1)

	pvseries.updControl("PvConvert/conv/mrs_natural/inSamples", 1)
	pvseries.updControl("PvConvert/conv/mrs_natural/onSamples", 1)
	pvseries.updControl("PvConvert/conv/mrs_real/osrate", 44100.0)


	pvseries.updControl("PvUnconvert/uconv/mrs_natural/inObservations", options['Nw'])
	pvseries.updControl("PvUnconvert/uconv/mrs_natural/onObservations", options['Nw'])
	pvseries.updControl("PvUnconvert/uconv/mrs_natural/Interpolation", options['I'])
	pvseries.updControl("PvUnconvert/uconv/mrs_natural/Decimation", options['D'])

	pvseries.updControl("PvUnconvert/uconv/mrs_string/mode",options['unconvertmode_'])

	pvseries.updControl("InvSpectrum/ispectrum/mrs_natural/onObservations", 1)
	pvseries.updControl("InvSpectrum/ispectrum/mrs_natural/onSamples", options['N'])

	pvseries.updControl("PvOverlapadd/pover/mrs_natural/FFTSize", options['N'])
	pvseries.updControl("PvOverlapadd/pover/mrs_natural/winSize", options['Nw'])
	pvseries.updControl("PvOverlapadd/pover/mrs_natural/Interpolation", options['I'])
	pvseries.updControl("PvOverlapadd/pover/mrs_natural/Decimation", options['D'])

	pvseries.updControl("ShiftOutput/so/mrs_natural/Interpolation", options['I'])

	pvseries.linkControl("PvConvert/conv/mrs_realvec/phases", "PvUnconvert/uconv/mrs_realvec/analysisphases")
	pvseries.linkControl("PvUnconvert/uconv/mrs_realvec/regions", "PvConvert/conv/mrs_realvec/regions")

	pvseries.updControl("SoundFileSink/last/mrs_natural/bitrate", 320)

	

	ticks = 0

	notempty = pvseries.getControl("SoundFileSource/src/mrs_bool/hasData")

	while (notempty.to_bool()):
		if(ticks == 0):
			pvseries.updControl("PvUnconvert/uconv/mrs_bool/phaselock", marsyas.MarControlPtr.from_bool(True))

		pvseries.tick()
		ticks = ticks + 1
		#print ticks*(options['D']/44100.0)

	return outfile


def pitch_shift(**args):

	options = deepcopy(default_options)
	for arg in args:
		options[arg] = args[arg]

	outfile = options['outfile']

	mng = marsyas.MarSystemManager()
	pvseries = marsyas.system_from_script_file("./marsystems/pitch-shift.mrs")

	pvseries.updControl("mrs_string/file", options['music_file'])
	pvseries.updControl("mrs_string/outfile", outfile)


  	pvseries.updControl("mrs_real/israte", 44100.0)
	pvseries.updControl("mrs_real/osrate", 44100.0)
	pvseries.updControl("mrs_natural/inSamples", options['D'])
	pvseries.updControl("mrs_natural/onSamples", options['I'])
	pvseries.updControl("mrs_natural/onStabilizingDelay", 7)

	pvseries.updControl("SoundFileSource/src/mrs_natural/onObservations", 2)

	pvseries.updControl("ShiftInput/si/mrs_natural/winSize", options['Nw'])
	pvseries.updControl("ShiftInput/si/mrs_natural/onSamples", options['N'])



	pvseries.updControl("PvFold/fo/mrs_natural/FFTSize", options['N'])
	pvseries.updControl("PvFold/fo/mrs_natural/onObservations", 1)

	pvseries.updControl("Spectrum/spk/mrs_natural/onObservations", options['N'])
	pvseries.updControl("Spectrum/spk/mrs_natural/onSamples", 1)

	pvseries.updControl("PvConvert/conv/mrs_natural/Sinusoids", options['sopt'])
	pvseries.updControl("PvConvert/conv/mrs_natural/Decimation", options['D'])

	pvseries.updControl("PvOscBank/osc/mrs_real/PitchShift", options['P'])
	pvseries.updControl("PvOscBank/osc/mrs_natural/winSize", options['Nw'])
	pvseries.updControl("PvOscBank/osc/mrs_natural/Interpolation", options['I'])
	pvseries.updControl("PvOscBank/osc/mrs_natural/onSamples", options['N'])

	pvseries.linkControl("PvConvert/conv/mrs_realvec/phases", "PvOscBank/osc/mrs_realvec/analysisphases")

	pvseries.updControl("ShiftOutput/so/mrs_natural/Interpolation", options['I'])

	pvseries.updControl("SoundFileSink/last/mrs_natural/bitrate", 320)



	ticks = 0

	notempty = pvseries.getControl("SoundFileSource/src/mrs_bool/hasData")

	while (notempty.to_bool()):
		if(ticks == 0):
			pass
			#pvseries.updControl("PvOscBank/osc/mrs_bool/phaselock", marsyas.MarControlPtr.from_bool(True))

		pvseries.tick()
		ticks = ticks + 1
		#print ticks*(options['D']/44100.0)


	return outfile

if __name__ == "__main__":

	tempochange = 1/2
	ipol = int(16/tempochange)
	infile = "./pv/nolove.wav"
	print "Output file will be at", tempochange, "original speed."
	outputfile = time_shift(I=ipol, music_file=infile, outfile="./pv/time_shift1.wav")
	print("Done!")

	pitch = 1.5
	print "Output file will be at", pitch, "times original pitch."
	outputfile = pitch_shift(P=pitch, music_file=infile, outfile="./pv/pitch_shift1.wav")
	print outputfile
	print("Done!")
