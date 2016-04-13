#!/bin/bash

mkdir -p wav

find . -name '*.mid' -type f -exec sh -c \
    'fluidsynth -F wav/$(basename ${0} .mid).wav /usr/share/sounds/sf2/TimGM6mb.sf2 ${0};' {} \;

