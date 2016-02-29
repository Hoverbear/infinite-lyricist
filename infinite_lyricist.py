#! /bin/env python2.7
import marsyas_helper
import argparse

# First, let's parse the command line options.
parser = argparse.ArgumentParser(description='Mashes a vocal track onto a instrumental track.')
parser.add_argument('vocal_input', metavar='vocal_input', help='The vocal input')
parser.add_argument('instrumental_input', metavar='instrumental_input', help='The instrumental input')

# Now we parse them and pick up the existing files or error out.
args = parser.parse_args()
vocal_track = open(args.vocal_input)
instrumental_track = open(args.instrumental_input)

# Debug
print(args)

