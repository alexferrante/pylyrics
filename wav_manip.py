import librosa 
import librosa.display
from pydub import AudioSegment 

def make_spectrogram(path):
    wav = AudioSegment.from_wav(path)
    wav = np.array(wav.get_array_of_samples()).astype(np.float32)
    S = librosa.feature.melspectrogram(wav, sr=16000, n_mels=128)
    log_S = librosa.power_to_db(S, ref=np.max)
    plt.figure(figsize=(12,4))
    librosa.display.specshow(log_S, sr=16000, x_axis='time', y_axis='mel')
    plt.colorbar(format='%+02.0f dB')
    plt.tight_layout()
