import adi
import csv
import numpy as np
import matplotlib.pyplot as plt
import time

samp_rate = 2e6
NumSamples = 2**12
rx_lo = 2.3e9
rx_mode = "manual"
rx_gain0 = 40
rx_gain1 = 40
tx_lo = rx_lo
tx_gain = -3
fc0 = int(200e3)
phase_cal = 0
num_scans = 5

def pluto():
    sdr = adi.Pluto(uri='ip:192.168.2.1')
    sdr.rx_enabled_channels = [0]
    sdr.sample_rate = int(samp_rate)
    sdr.rx_rf_bandwidth = int(fc0 * 3)
    sdr.rx_lo = int(rx_lo)
    sdr.gain_control_mode = rx_mode
    sdr.rx_hardwaregain_chan0 = int(rx_gain0)
    sdr.rx_buffer_size = int(NumSamples)
    sdr._rxadc.set_kernel_buffers_count(1)
    sdr.tx_enabled_channels = [0]
    sdr.tx_rf_bandwidth = int(fc0 * 3)
    sdr.tx_lo = int(rx_lo)
    sdr.tx_cyclic_buffer = True
    sdr.tx_hardwaregain_chan0 = int(tx_gain)
    #sdr.tx_hardwaregain_chan1 = int(-88)
    sdr.tx_buffer_size = int(2**18)
    return sdr  # ← fixed indentation

def dbfs(raw_data):
    NumSamples = len(raw_data)
    win = np.hamming(NumSamples)
    y = raw_data * win
    s_fft = np.fft.fft(y) / np.sum(win)
    s_shift = np.fft.fftshift(s_fft)
    s_dbfs = 20 * np.log10(np.abs(s_shift) / (2**11))
    return s_shift, s_dbfs  # ← fixed indentation

def plot_spectrum(xf, rx_dbfs):
    plt.figure()
    plt.plot(xf, rx_dbfs)
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("Amplitude [dBFS]")
    plt.title("Received spectrum")
    plt.ylim(bottom=-80, top=5)
    plt.grid(True)
    plt.show()

def siggy(sdr):
    fs = int(sdr.sample_rate)
    N = 2**16
    ts = 1 / float(fs)
    t = np.arange(0, N * ts, ts)
    i0 = np.cos(2 * np.pi * t * fc0) * 2**14
    q0 = np.sin(2 * np.pi * t * fc0) * 2**14
    iq0 = i0 + 1j * q0
    sdr.tx(iq0)

def toCsv(name, data, pos):
    pass  # implement as needed

def main():
    sdr = pluto()
    siggy(sdr)
    for i in range(20):
        sdr.rx()
    data = sdr.rx()
    _, rx_dbfs = dbfs(data)
    ts = 1 / samp_rate
    xf = np.fft.fftshift(np.fft.fftfreq(NumSamples, ts)) / 1e6
    plot_spectrum(xf, rx_dbfs)
    sdr.tx_destroy_buffer()
    print(data)

if __name__ == "__main__":
    main()