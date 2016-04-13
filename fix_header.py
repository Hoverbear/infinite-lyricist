from pydub import AudioSegment
from struct import pack, unpack
import wave


def fix_header(wav_file):
	"""
	Fixes a bad header from one of the outputs.

	* wav_file: The file name.
	"""
	w = wave.open(wav_file, 'r')

	nframes = w.getnframes()
	nchannels = w.getnchannels()
	samplerate = w.getframerate()

	w.close()

	wav_header = "4si4s4sihhiihh4si"

	f = open(wav_file, 'rb+')
	data = list(unpack(wav_header,f.read(44)))
	assert data[0]=='RIFF'
	assert data[2]=='WAVE'
	assert data[3]=='fmt '
	assert data[4]==16
	assert data[-2]=='data'

	filesize = nframes*nchannels*data[4]
	datasize = filesize - 44

	data[-1] = datasize
	data[1]  = datasize+36

	f.seek(0)
	f.write(pack(wav_header, *data))
	f.close()

	return float(nframes)/samplerate



if __name__ == "__main__":
	test_file = "/tmp/vocal_time-shift0.wav"
	fix_header(test_file)

	vocal_sound = AudioSegment.from_wav(test_file)

	vocal_sound.export("vocal_test0.wav", format="wav")
