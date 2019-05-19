# -*- coding: utf-8 -*-
"""
Created on Sat May 18 10:11:12 2019

@author: 薄冰
"""
from collections import deque
from enum import Enum
import numpy as np
import pyaudio 
import wave 




CHUNK = 1024
SYMBOL = {'C4':261.1, 'E': 311.1, 'F':349.2, 'G':392.0, 'B':466.2}

class Aconst(Enum):
    amplitude = 2 ** 15 - 1
    channels = 1
    sample_width = 2
    frame_rate = 44100
    frames = 44100
    


def write_sine(path:str, freq:float, rate:int=44100, duration:int=5):
    samples = rate * duration
    x = np.linspace(0, duration, samples)
    vals = np.sin(2 * np.pi * freq * x)
    data = np.array(vals * Aconst.amplitude.value, 'int16').tostring()
    write_wave(path, data)
  
def white_noise(length:int):
    return np.random.randn(length)
      

def generate_wave(freq:float, rate:int=44100, sample_rate:int=44100, duration:float=1,alpha=0.996):
    length = int(sample_rate / freq)
    #buf = deque(random.random() - .5 for _ in range(length))
    buf = deque(white_noise(length))
    points = int(sample_rate * duration) 
    samples = np.zeros(points, 'float32')
    for i in range(points):
        samples[i] = buf[0]
        avg = alpha * 0.5 * (buf.popleft() + buf[-1])
        buf.append(avg)
        
    samples = np.array(samples * Aconst.amplitude.value, 'int16')
    return samples

def write_wave(path:str, data:bytes, frame_rate:int=44100, frames:int=44100):
    with wave.open(path, 'wb') as w:
        w.setparams((Aconst.channels.value, \
                     Aconst.sample_width.value, \
                     frame_rate, \
                     frames, \
                     'NONE', 'uncompressed'))
        w.writeframes(data)
    

    



def play(path):
    wf = wave.open(path, 'rb')
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), \
                    channels=wf.getnchannels(), \
                    rate=wf.getframerate(), \
                    output=True)
    
    data = wf.readframes(CHUNK)
    
    while data != b'':
        stream.write(data)
        data = wf.readframes(CHUNK)
        
    stream.stop_stream()
    stream.close()
    
    p.terminate()
    
    wf.close()
    
    
