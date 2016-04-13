all:
	echo "Pick a target from the Makefile please."

dp-start:
	# Creates a single vocal section at the start of the input instrumental.
	# Primarily intended for basic functionality testing.
	mkdir -p outputs
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		instrumentals/wav/song-bass+guitar+synth+drums.wav \
		00:00-00:30 \
		outputs/dp-start.wav

dp-start-2:
	# Creates a second, different output like the first `dp-start` target.
	# If the system is working correctly this should have a different vocal section 4/5 times.
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		instrumentals/wav/song-bass+guitar+synth+drums.wav \
		00:00-00:30 \
		outputs/dp-start-2.wav

dp-pair: dp-start dp-start-2
	# A convienence target for both.

dp-same-length-sections:
	# A demo of multiple same length vocal sections All sections here are 6.5s in length.
	# This demonstrates that the exact same sample is not selected each time.
	mkdir -p outputs
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		instrumentals/wav/song-bass+guitar+synth+drums.wav \
		00:08-00:14:500,00:15-00:22:500,00:23-00:31:500,00:32-00:39:500,00:40-00:46:500,00:47-00:56 \
		outputs/dp-same-length-sections.wav

dp-different-length-sections:
	# A demo of multiple different length vocal sections. All sections here are different lengths.
	# This demonstrates that samples of appropriate size are selected.
	mkdir -p outputs
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		instrumentals/wav/song-bass+guitar+synth+drums.wav \
		00:08-00:30,00:15-00:45,00:23-00:26,00:32-00:39:500,00:40-00:46:500,00:47-00:56 \
		outputs/dp-different-length-sections.wav

dp-lots-of-sections:
	# A demo of many vocal sections at the beginning of the track.
	# This demonstrates the diversity of samples selected.
	mkdir -p outputs
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		instrumentals/wav/song-bass+guitar+synth+drums.wav \
		00:00-00:05,00:07-00:10,00:15-00:25,00:27-00:35,00:35-00:46,00:50-00:56,00:56-1:20 \
		outputs/dp-lots-of-sections.wav
