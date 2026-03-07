import wave
import struct
import math

def generate_music(features):

    filename = "music.wav"

    sample_rate = 44100
    duration = 3
    frequency = 440

    wav_file = wave.open(filename, "w")
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)

    for i in range(sample_rate * duration):
        value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        data = struct.pack('<h', value)
        wav_file.writeframesraw(data)

    wav_file.close()

    return filename