from scipy.signal import butter, lfilter
import csv
import matplotlib.pyplot as plt


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=6):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


def readCSV(fileName):
    data = []
    with open(fileName + '.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(float(row[0]))
    return data


bprawData = readCSV('data')
dataLength = len(bprawData)
t = []
for i in range(dataLength):
    t.append(i)

plt.figure(1)
plt.clf()
plt.plot(t, bprawData, label='Raw data')
bpLowpass = butter_lowpass_filter(bprawData, 5, 100, 5)
plt.plot(t, bpLowpass, label='Lowpass data')
bpBandpass = butter_bandpass_filter(bpLowpass, 0.5, 10, 100, 5)
plt.plot(t, bpBandpass, label='Bandpass data')
aa = bpLowpass * bpBandpass
plt.plot(t, aa, label='aa')

maximum = 0
prior = 0
index = 0
for i in range(dataLength):
    temp = bpBandpass[i]
    if temp > maximum and (prior - temp) < 0.5:
        maximum = temp
        index = i
        print(prior - temp)
    prior = temp

print(bpBandpass[index])

plt.show()
