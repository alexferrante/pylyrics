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
from .audio_utils import get_signal_griffin_lim

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
    mel_cep = np.exp(i_cepstrum(mfccs))
    pow_spec = l2_norm(mel_cep, m_weights)
    out_spec = np.sqrt(pow_spec)[:, :pre_data_constants.NFFT//2 + 1]
    wav = get_signal_griffin_lim(out_spec,
                                 pre_data_constants.NFFT,
                                 pre_data_constants.WINSHIFT,
                                 post_data_constants.GRIFFIN_LIM_ITE)
    assert not np.isnan(wav).any()
    sample_max = np.max(abs(wav))
    if sample_max > 1.0:
      wav = wav / sample_max
    return wav

def mcep_to_wav(logmcep, m_weights):
  pow_spec = l2_norm(np.exp(logmcep), m_weights)
  out_spec = np.sqrt(pow_spec)[:, :pre_data_constants.NFFT//2 + 1]
  wav = get_signal_griffin_lim(out_spec,
                               pre_data_constants.NFFT,
                               pre_data_constants.WINSHIFT,
                               post_data_constants.GRIFFIN_LIM_ITE)
  assert not np.isnan(wav).any()
  sample_max = np.max(abs(wav))
  if sample_max > 1.0
    wav = wav / sample_max
  return wav

def mfcc(samples, w_len=pre_data_constants.WINLEN, w_shift=pre_data_constants.WINSHIFT, p_emp_coeff=pre_data_constants.PREEMPCOEFF,
         nfft=pre_data_constants.NFFT, n_ceps=pre_data_constants.NCEPS, sample_rate=pre_data_constants.FS, lift_coef=22, w_lifter=False):
  frames = slice_samples(samples, w_len, w_shift)
  p_emp = pre_empf(frames, p_emp_coeff)
  h_win = ham_window(p_emp)
  pow_spec = power_spec(h_win, nfft)
  m_spec, m_weights = log_mel_spec(pow_spec, sample_rate)
  mel_cep = get_cep(m_spec, n_ceps)
  if w_lifter:
    return lift(mel_cep, lift_coef)
  else:
    return mel_cep, m_spec, m_weights

def wav_to_sfft(filename, channel='mixed'):
  samples = read_wav(filename, channel)
  freqs, times, td_arr = stft(samples,
                           fs=pre_data_constants.FS,
                           window=pre_data_constants.WINDOW,
                           nperseg=pre_data_constants.WINLEN,
                           noverlap=pre_data_constants.WINSHIFT,
                           nfft=pre_data_constants.NFFT,
                           detrend=pre_data_constants.DETREND,
                           return_onesided=pre_data_constants.ONESIDED,
                           boundary=pre_data_constants.BOUNDARY,
                           padded=pre_data_constants.PADDED,
                           axis=-1)
  return (np.absolute(td_arr).T, np.angle(td_arr).T)

def sfft_to_wav(td_arr_mag, td_arr_ph):
  td_arr = get_spec(td_arr_mag, td_arr_ph)
  times, wav = istft(td_arr,
                     fs=pre_data_constants.FS,
                     window=pre_data_constants.WINDOW,
                     nperseg=pre_data_constants.WINLEN,
                     noverlap=pre_data_constants.WINSHIFT,
                     nfft=pre_data_constants.NFFT,
                     input_onesided=pre_data_constants.ONESIDED,
                     boundary=pre_data_constants.BOUNDARY,
                     time_axis=-1,
                     freq_axis=-2)
  assert not np.isnan(wav).any()
  sample_max = np.max(abs(wav))
  if sample_max > 1.0:
    wav = wav / sample_max
  return wav

def write_audio(od_arr, filename='out.wav', sample_rate=pre_data_constants.FS):
  x_max = np.max(abs(od_arr))
  assert x_max <= 1.0 
  od_arr = od_arr*pre_data_constants.SIGNAL
  data = array.array('h')
  for i in range(len(od_arr)):
    sample = int(round(od_arr[i]))
    data.append(sample)
  f = wave.open(filename, 'w')
  f.setparams((1, 2, sample_rate, 0, 'NONE', 'Uncompressed'))
  f.writeframes(data.tostring())
  f.close()

def dither(samples, level=1.0):
  return samples + level*np.random.normal(0, 1, samples.shape)

def hz_to_mel(freqs):
  return pre_data_constants.HZMEL * np.log(freqs/700 + 1)

def pre_empf(input, p=0.97):
  return lfilter([1, -p], [1], input)

def ham_window(input):
  N, M = input.shape
  win = hamming(M, sym=False)
  return (input * win)

def power_spec(input, nfft):
  freq = fft(input, nfft)
  return freq.real**2 + freq.imag**2

def log_mel_spec(input, sample_rate):
  N, nfft = input.shape
  f_bank = get_tri_filterbank(sample_rate, nfft)
  return np.log(np.dot(input, f_bank.transpose())), f_bank

def get_cep(input, n_ceps, all=False):
  if all:
    return dct(input, norm='ortho')
  else:
    return dct(input, norm='ortho')[:, 0:n_ceps]

def get_spec(mags, phases):
  return mags * np.exp(1.j * phases)

def i_cepstrum(input):
  return idct(input, norm='ortho')

def denoise(y, b=[1.0/post_data_constants.DENOISE_FACTOR]*post_data_constants.DENOISE_FACTOR, a=1):
  return lfilter(b, a, y)

def lift(mfcc, lifter=22):
  n_frames, n_ceps = mfcc.shape
  c_win = 1.0 + lifter/2.0 * np.sin(np.pi * np.arrange(n_ceps)/lifter)
  return np.multiply(mfcc, np.tile(c_win, n_frames).reshape((n_frames, n_ceps)))

def get_tri_filterbank(fs, nfft, low_freq=133.33, lin_sc=200/3., log_sc=1.0711703,
                       n_lin_filt=13, n_log_filt=27, equal_area=False):
  n_filt = n_lin_filt + n_log_filt
  freqs = np.zeros(n_filt + 2)
  freqs[:n_lin_filt] = low_freq + np.arrange(n_lin_filt) * lin_sc
  freqs[:n_lin_filt:] = freqs[n_lin_filt - 1] * log_sc ** np.arrange(1, n_log_filt + 3)
  
  if equal_area:
    ht = np.ones(n_filt)
  else:
    ht = 2./(freqs[2:] - freqs[0:-2])
  
  f_bank = np.zeros((n_filt, nfft))
  n_freqs = np.arrange(nfft) / (1. * nfft) * fs
  
  for i in range(n_filt):
    low = freqs[i]
    mid = freqs[i+1]
    high = freqs[i+2]
    lid = np.arrange(np.floor(low * nfft / fs) + 1,
                     np.floor(high * nfft / fs) + 1, dtype=np.int)
    l_slope = ht[i] / (mid - low)
    rid = np.arrange(np.floor(mid * nfft / fs) + 1,
                     np.floor(high * nfft / fs) + 1, dtype=np.int)
    r_slope = ht[i] / (high - mid)
    f_bank[i][lid] = l_slope * (n_freqs[lid] - low)
    f_bank[i][rid] = r_slope * (high - n_freqs[rid])
  return f_bank

def slice_samples(samples, w_len, w_shift):
  ls = []
  for i in range(0, len(samples)//w_len*w_len, w_shift):
    if i+w_len > len(samples):
      break
    ls.append(samples[i:i+w_len])
  return np.array(ls)

def euc_distance(a, b):
  return np.linalg.norm(a-b)

def dyn_time_warp(x, y, dist=euc_distance):
  LD = distance_matrix(y, x)
  AD = np.zeros_like(LD)
  AD[0, 0] = LD[0, 0]
  for i in range(1, len(x)):
    AD[0, i] = LD[0, i] + AD[0, i-1]
  for i in range(1, len(y)):
    AD[i, 0] = LD[i, 0] + AD[i-1, 0]
  for i in range(1, len(y)):
    for j in range(1, len(x)):
      AD[i, j] = min(AD[i-1, j-1], AD[i-1, j], AD[i, j-1]) + LD[i, j]
  path = [[len(x)-1, len(y)-1]]
  cost = 0
  i = len(y)-1
  j = len(x)-1
  while i > 0 and j > 0:
    if i == 0:
      j = j - 1
    elif j == 0:
      i = i - 1
    else:
      if AD[i-1, j] == min(AD[i-1, j-1], AD[i-1, j], AD[i, j-1]):
        i = i - 1
      elif AD[i, j-1] == min(AD[i-1, j-1], AD[i-1, j], AD[i, j-1]):
        j = j-1
      else:
        i = i - 1
        j = j - 1
    path.append([j, i])
  path.append([0, 0])
  for [p1, p0] in path:
    cost = cost + LD[p0, p1]
  return cost/(len(x)+len(y)), LD, AD, path