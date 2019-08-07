class data_constants:
  BATCH_SIZE = 8
  MAX_TIME = 4
  NCEPS = 40
  NMELS = 40
  PREEMPCOEFF = 0.97
  FS = 16000
  WINDOW = 'hann'
  WINLEN = 512
  WINSHIFT = WINLEN//2
  NFFT = 512
  DETREND = False
  ONESIDED = True
  BOUNDARY = None
  PADDED = False
  eps = 0.001

class data_constants:
  DENOISE_FACTOR = 5  
  GRIFFIN_LIM_ITE = 277