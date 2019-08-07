from .data_utils import *
from .data_constants import *
from constants import *

import os as os
import random as rand

from pathlib import Path

def create_datasets(num_files):
  train_set_path = Path('data/Wav/train')

  if not(train_set_path.is_dir()):
    dist_dataset()

  n_train_files = int(num_files * TRAINING_SPLIT)
  n_test_files = int(num_files * (TEST_SPLIT))
  n_dev_files = num_files - (num_train_files + num_test_files)

  create_dataset("train", n_train_files)
  create_dataset("dev", n_dev_files)
  create_dataset("test", n_test_files)

def create_dataset(path, num_files):
  path_dataset = 'data/Wav' + '/' + path
  if not os.path.isfile('coefficients/batch_stft_%s.npz' %path):
    filenames = [os.path.join(path_dataset, f) for f in os.listdir(path_dataset)
    
    if os.path.isfile(os.path.join(path_dataset, f))][:n_files]

    # STFT
    stft_mixed = [wav_to_stft(f, channel='mixed') for f in filenames]
    stft_bg = [wav_to_stft(f, channel='instrumental') for f in filenames]
    stft_vc = [wav_to_stft(f, channel='vocals') for f in filenames]

    # Normalize STFT
    stft_mixed_norm = [np.divide(src_mixed[0],100) for src_mixed in stft_mixed]
    stft_bg_norm = [np.divide(src_bg[0], 100) for src_bg in stft_bg]
    stft_vc_norm = [np.divide(src_vc[0], 100) for src_vc in stft_vc]

    log_stft_mixed_norm = [np.log(src_mx+Preprocessing.eps) for src_mx in stft_mixed_norm]
    log_stft_bg_norm = [np.log(src_bg+Preprocessing.eps) for src_bg in stft_bg_norm]
    log_stft_vc_norm = [np.log(src_vc+Preprocessing.eps) for src_vc in stft_vc_norm]

    # MFCC coefficients
    mfcc_mixed = [wav_to_mfcc(f, channel='mixed') for f in filenames]
    mfcc_bg = [wav_to_mfcc(f, channel='instrumental') for f in filenames]
    mfcc_vc = [wav_to_mfcc(f, channel='vocals') for f in filenames]

    mins_mx, mins_bg, mins_vc = [], [], []
    for mm, mb, mv in zip(mfcc_mixed, mfcc_bg, mfcc_vc):
      mins_mx.append(np.min(mm))
      mins_bg.append(np.min(mb))
      mins_vc.append(np.min(mv))
    absmin_mx, absmin_bg, absmin_vc = abs(np.min(mins_mx)), abs(np.min(mins_bg)), abs(np.min(mins_vc))
    
    log_mfcc_mixed = [np.log(src_mx+absmin_mx+Preprocessing.eps) for src_mx in mfcc_mixed]
    log_mfcc_bg = [np.log(src_bg+absmin_bg+Preprocessing.eps) for src_bg in mfcc_bg]
    log_mfcc_vc = [np.log(src_vc+absmin_vc+Preprocessing.eps) for src_vc in mfcc_vc]	

    # Normalized STFT
    batch_stft_mixed = [coef_to_batch(src_mixed) for src_mixed in log_stft_mixed_norm]
    batch_stft_bg = [coef_to_batch(src_bg) for src_bg in  log_stft_bg_norm]
    batch_stft_vc = [coef_to_batch(src_vc) for src_vc in log_stft_vc_norm]

    # MFCC
    batch_mfcc_mixed = [coef_to_batch(src_mixed) for src_mixed in log_mfcc_mixed]
    batch_mfcc_bg = [coef_to_batch(src_bg) for src_bg in log_mfcc_bg]
    batch_mfcc_vc = [coef_to_batch(src_vc) for src_vc in log_mfcc_vc]

    np.savez_compressed('coefficients/batch_stft_%s.npz' %load_path, mixed=batch_stft_mixed ,bg=batch_stft_bg, vc=batch_stft_vc)
    np.savez_compressed('coefficients/batch_mfcc_%s.npz' %load_path, mixed=batch_mfcc_mixed ,bg=batch_mfcc_bg, vc=batch_mfcc_vc)

def dist_dataset():
  path_dataset = 'data/Wav'
  filenames = os.listdir(path_dataset)
  rand.seed(230)
  rand.shuffle(filenames)
  
  train_lim = int(TRAINING_SPLIT * len(filenames))
  test_lim = int((1 - TEST_SPLIT) * len(filenames))
  
  train_filenames = filenames[: train_lim]
  test_filenames = filenames[test_lim:]
  dev_filenames = filenames[train_lim:test_lim]
  
  train_path = os.path.join(path_dataset, 'train')
  test_path = os.path.join(path_dataset, 'test')
  dev_path = os.path.join(path_dataset, 'dev')

  if not os.path.exists(train_path):
    os.makedirs(train_path)
  if not os.path.exists(test_path):
    os.makedirs(test_path)
  if not os.path.exists(dev_path):
    os.makedirs(dev_path)
  
  for f in train_filenames:
    os.rename(os.path.join(path_dataset, f), os.path.join(train_path, f))
  
  for f in test_filenames:
    os.rename(os.path.join(path_dataset, f), os.path.join(test_path, f))
  
  for f in dev_filenames:
    os.rename(os.path.join(path_dataset, f), os.path.join(dev_path, f))

