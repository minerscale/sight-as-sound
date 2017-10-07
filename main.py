#! /usr/bin/env python

# I used python 3.6 with an Anaconda install on Linux to make this.
# If you don't use all of those, your mileage may vary.

# Change these:
# The input file must be grayscale
input_file = 'shrooming.png'
output_wav = 'shrooming.wav'

# Keep this number low.
# It takes ages to generate
num_seconds = 4

lowest_frequency = 220 # In hz!

# A value that directly detirmines the frequency
# Find the highest frequency with this:
# 2**(255/frequency_n)*lowest_frequency
# That puts the max frequency at just under 2562hz
frequency_n = 72 # Not in hz!

# ===========================================================================

# This is a little library I found online so I didn't have to
# Make the hilbert curve stuff myself. A real time saver!
# hilber_curve.py is included in the zip.
import hilbert_curve as hc
from PIL import Image
import math
import wave

# Makes sine waves, this is what I'll be using for
# To make the individual frequencies
# f = frequency
# a = amplitude
# t = time
def generateSine(f,a,t):
	return (math.sin(t/44100*2*math.pi*f)*a)

# Checks if the number is a power of 2.
def checkPowerOf2(num):
	return ((num & (num - 1)) == 0) and num != 0

# Open the image
img = Image.open(input_file).convert("L")
pixels = img.load()

# Get the size of the image
x,y = img.size
# It doesn't fit the criteria. Tish tish tish.
if ((x != y) or (checkPowerOf2(x) == False)):
	exit("The image has to be a power of 2.")


print ("Serialising pixels...")
# Here's where it gets interesting.
# We create the output list
output = []
# Then, we iterate over every pixel.
for i in range(0,x**2):
	# hc.d2xy() Turns a linear integer
	# into the x,y coordinates of a plane.
	hilbert = hc.d2xy(math.log(x*y,2),i)

	# Use those coordinates to get the pixel value
	# And thus serialise a 2d plane.
	output.append(pixels[hilbert])

print ("Generating audio...")
# Generate the Audio output list
outputAudio = [0]*(44100*num_seconds)

pixel_count = 0
# Iterate over every sing pixel in the list
for pixel in output:
	if pixel_count % 10 == 0:
		print (pixel_count,"pixels completed out of", x*y, "          ", end="\r")
	pixel_count += 1

	# I'm mapping the audio exponetially instead of linearly becase that's the way
	# The human ear works. That made the most sence to me.
	# The way I mapped those frequencies is arbitary, except that I tried to make it
	# so the frequencies were within the loudest part of human hearing ~ 220hz to 2561hz
	frequency = 2**(pixel/frequency_n)*lowest_frequency;
	for t in range(0,len(outputAudio)):
		# Constantly layer the audio on top of one another until it's complete
		# We use a really big offset to t becuase if we don't we get a really weird tone that quickly
		# Tapers off. If you can figure out why this is I'll be really happy
		outputAudio[t] += generateSine(frequency,1/(x*y/2),t+524288)

print("Converting...")
# Do some conversion work. At the moment the audio is between -1 and 1
# I need to map -1 and 1 to 0 and 65536
for i in range(0,len(outputAudio)):
	# Add one
	outputAudio[i] += 1
	# Multiply by 16384, the reason why I'm not multiplying by the maximum amount
	# is because python wave uses singed not unsinged and to_bytes uses unsinged
	# so nobody wins and the volume gets slashed in half
	outputAudio[i] = outputAudio[i] * 16384

	# Convert it to an integer so to_bytes doesn't throw a hissy fit
	outputAudio[i] = int(outputAudio[i])


print("Writing file to disk, also converting the sound data to bytes.")
# Open the output file
audio_output = wave.open(output_wav, 'w')
# Set it to one channed 16bit 44100hz no compression
audio_output.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))

# Write the output to the file
for i in outputAudio:
	audio_output.writeframes(i.to_bytes(2,'little'))
