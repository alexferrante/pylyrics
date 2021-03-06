import numpy as np

def hz_to_mel(freqs):
    return 2595*np.log10(1.0 + freqs/700.0)

def mel_to_hz(mels):
    return 700*(10**(mels/2595) - 1.0)

def bin_fft_to_hz(n_bin, sample_rate, fft_size):
    n_bin = float(n_bin)
    sample_rate = float(sample_rate)
    fft_size = float(fft_size)
    return n_bin*sample_rate/(2.0*fft_size)

def hz_to_fft_bin(freqs, sample_rate, fft_size):
    freqs = float(freqs)
    sample_rate = float(sample_rate)
    fft_size = float(fft_size)
    bin_fft = int(np.round((freqs*2.0*fft_size/sample_rate)))
    if bin_fft >= fft_size:
        bin_fft = fft_size-1
    return bin_fft

def get_m_filterbank(min_freq, max_freq, m_bin_count, lin_bin_count, sample_rate):
    min_mels = hz_to_mel(min_freq)
    max_mels = hz_to_mel(max_freq)

    spaced_lin_mel = np.linspace(min_mels, max_mels, num=m_bin_count)
    lin_freq = np.array([mel_to_hz(n) for n in spaced_lin_mel])
    m_per_bin = float(max_mels - min_mels)/float(m_bin_count - 1)

    mels_start = min_mels - m_per_bin
    freq_start = mel_to_hz(mels_start)
    fft_bin_start = hz_to_fft_bin(freq_start, sample_rate, lin_bin_count)

    mels_end = max_mels + m_per_bin
    freq_stop = mel_to_hz(mels_end)
    fft_bin_stop = hz_to_fft_bin(freq_stop, sample_rate, lin_bin_count)

    lin_bin_indices = np.array([hz_to_fft_bin(freqs, sample_rate, lin_bin_count) for freqs in lin_freq])
    filterbank = np.zeros((m_bin_count, lin_bin_count))

    for m_bin in range(m_bin_count):
        linear_bin_freq = lin_bin_indices[m_bin]
        if linear_bin_freq > 1:
            if m_bin == 0:
                left_bin = max(0, fft_bin_start)
            else:
                left_bin = lin_bin_indices[m_bin - 1]
            for f_bin in range(left_bin, linear_bin_freq+1):
                if (linear_bin_freq - left_bin) > 0:
                    res = float(f_bin - left_bin)/float(linear_bin_freq - left_bin)
                    filterbank[m_bin, f_bin] = res
        if linear_bin_freq < lin_bin_count-2:
            if m_bin == m_bin_count - 1:
                right_bin = min(lin_bin_count - 1, fft_bin_stop)
            else:
                right_bin = lin_bin_indices[mel_bin + 1]
            for f_bin in range(linear_bin_freq , right_bin+1):
                if (right_bin - linear_bin_freq) > 0:
                    res = float(right_bin - f_bin)/float(right_bin - linear_bin_freq)
                    filterbank[m_bin, f_bin] = res
        filterbank[m_bin, linear_bin_freq] = 1.0
    return filterbank

def get_stft(x, fft_size, n_hops_samples):
    window = np.hanning(fft_size)
    fft_size = int(fft_size)
    n_hops_samples = int(n_hops_samples)
    return np.array([np.fft.rfft(window*x[i:i+fft_size])
                    for i in range(0, len(x)-fft_size, n_hops_samples)])

def get_istft(x, fft_size, n_hops_samples):
    fft_size = int(fft_size)
    n_hops_samples = int(n_hops_samples)
    window = np.hanning(fft_size)
    time_slices = x.shape[0]
    size_samples = int(time_slices*n_hops_samples + fft_size)
    res = np.zeros(size_samples)
    for n,i in enumerate(range(0, len(res)-fft_size, n_hops_samples)):
        res[i:i+fft_size] += window*np.real(np.fft.irfft(x[n]))
    return res

def get_signal_griffin_lim(mag_spec, fft_size, n_hops_samples, iter):
    time_slices = mag_spec.shape[0]
    size_samples = int(time_slices*n_hops_samples + fft_size)
    x_restruc = np.random.randn(size_samples)
    n = iter
    while n > 0:
        n -= 1
        restruc_spec = get_stft(x_restruc, fft_size, n_hops_samples)
        restruc_ang = np.angle(restruc_spec)
        prop_spec = mag_spec*np.exp(1.0j*restruc_ang)
        prev_x = x_reconstruct
        x_restruc = get_istft(prop_spec, fft_size, n_hops_samples)
        diff = np.sqrt(sum((x_restruc - prev_x)**2)/x_restruc.size)
    return x_restruc


