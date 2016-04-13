all:
	echo "Pick a target from the Makefile please."

dp-start:
	mkdir -p outputs
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		song/wav/song-bass+guitar+synth+drums.wav \
		00:00-00:30 \
		outputs/dp-start.wav

dp-start-2:
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		song/wav/song-bass+guitar+synth+drums.wav \
		00:00-00:30 \
		outputs/dp-start-2.wav

dp-pair: dp-start dp-start-2

dp-same-length-sections:
	mkdir -p outputs
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		song/wav/song-bass+guitar+synth+drums.wav \
		00:08-00:14:500,00:15-00:22:500,00:23-00:31:500,00:32-00:39:500,00:40-00:46:500,00:47-00:56 \
		outputs/dp-same-length-sections.wav

dp-different-length-sections:
	mkdir -p outputs
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		song/wav/song-bass+guitar+synth+drums.wav \
		00:08-00:30,00:15-00:45,00:23-00:26,00:32-00:39:500,00:40-00:46:500,00:47-00:56 \
		outputs/dp-different-length-sections.wav
