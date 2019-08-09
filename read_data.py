import numpy as np

def read_batch(feature):
  if feature == 'stft':
    tmp_train = np.load('coefficients/batch_stft_train.npz')
    tmp_val = np.load('coefficients/batch_stft_dev.npz')
  elif feature == 'mfcc':
    tmp_train = np.load('coefficients/batch_mfcc_train.npz')
    tmp_val = np.load('coefficients/batch_mfcc_dev.npz')
  else:
    return -1
  
  return tmp_train['mixed'].tolist(), tmp_train['vc'].tolist(), tmp_val['mixed'].tolist(), tmp_val['vc'].tolist()