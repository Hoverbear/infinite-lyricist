all:
	echo "Pick a task from the file please."

daftpunk-start:
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		song/wav/song-bass+guitar+synth+drums.wav \
		00:00-00:30

daftpunk-same-length-sections:
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		song/wav/song-bass+guitar+synth+drums.wav \
		00:08-00:14:500,00:15-00:22:500,00:23-00:31:500,00:32-00:39:500,00:40-00:46:500,00:47-00:56

daftpunk-different-length-sections:
	python2 infinite_lyricist.py \
		vocals/dp-hbfs.wav \
		song/wav/song-bass+guitar+synth+drums.wav \
		00:08-00:30,00:15-00:45,00:23-00:26,00:32-00:39:500,00:40-00:46:500,00:47-00:56
