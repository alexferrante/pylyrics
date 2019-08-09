import numpy as np
import wave
import array
import librosa.feature as lib

from scipy.io import wavfile
from scipy.signal import lfilter, hamming, stft, istft, check_COLA
from scipy.fftpack import fft, dct, idct
from scipy.optimize import linprog
from scipy.linalg import lstsq

from .data_constants import *

def read_wav(filename, channel='mixed'):
    assert channel in {'instrumental', 'vocals', 'mixed'}
    wav = wavfile.read(filename)[1]
    if channel == 'instrumental':
        samples = wav[:,0]
    elif channel == 'vocals':
        samples = wav[:,1]
    else:
        samples = np.sum(wav, axis=-1)
    return samples

def wav_to_mfcc(filename, channel='mixed'):
    samples = read_wav(filename)
    mfccs = lib.mfcc(samples.astype(float), n_mfcc=40)
    return mfccs.T

def mfcc_to_wav(mfccs, m_weights):
    mel_cep = np.exp(icepstrum(mfccs))
    pow_spec = l2_norm(mel_cep, m_weights)
    out_spec = np.sqrt(pow_spec)[:, :data_constants.NFFT//2 + 1]
    wav = 
    

def mcep_to_wav(logmcep, m_weights):

def mfcc():

def wav_to_sfft(filename, channel='mixed'):

def sfft_to_wav():

def get_spec():

def write_audio():

def dither(samples, level=1.0):

def hz_to_mel(freqs):

def get_tri_filterbank():

def dyn_time_warp(x, y, dist=euclidean_distance):


