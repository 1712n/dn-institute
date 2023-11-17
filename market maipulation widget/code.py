import os
import json
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages

with open("bybit-ava-usdt.json", 'r') as d:
    file = json.load(d)
with open('gateio-ava-usdt.json', 'r') as d1:
    file1 = json.load(d1)
with open('binance-ava-usdt.json', 'r') as d2:
    file2 = json.load(d2)
start = '2023-11-10T10:00:00'
end = '2023-11-16T10:00:00'
period_for_benford = 6
hours = mdates.HourLocator(interval=6)

start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
numhours = (end -start)/timedelta(hours=1)
timestamp_full = [start + timedelta(hours=x) for x in  range(int(numhours))]
timestamp_full_for_bars = [x.strftime('%m-%d %H:%M') for x in  timestamp_full]

timestamp = []
timestamp1 = []
timestamp2 = []
volume_volatility_correlation = []
volume_distribution_kurtosis = []
volume_distribution_mean = []
volume_distribution_median = []
volume_distribution_mode = []
volume_distribution_mode1 = []
volume_distribution_mode2 = []
volume_distribution_skewness = []
volume_distribution_std = []
buy_sell_count_ratio = []
buy_sell_count_ratio1 = []
buy_sell_count_ratio2 = []
vwap = []
vwap1 = []
vwap2 = []
market_id = file['data'][1]['market_id']
market_id1 = file1['data'][1]['market_id']
market_id2 = file2['data'][1]['market_id']
count_time_to_insert = [0]*60
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
significant_digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
minutes = [start]
t = start
while t != end:
    t += timedelta(minutes=1)
    minutes.append(t)
  
for i in file['data']:
    timestamp.append(i['timestamp'])
    volume_volatility_correlation.append(float(i['volume_volatility_correlation']))
    volume_distribution_kurtosis.append(float(i['volume_distribution_kurtosis']))
    volume_distribution_mean.append(float(i['volume_distribution_mean']))
    volume_distribution_median.append(float(i['volume_distribution_median']))
    volume_distribution_mode.append(float(i['volume_distribution_mode']))
    volume_distribution_skewness.append(float(i['volume_distribution_skewness']))
    volume_distribution_std.append(float(i['volume_distribution_std']))
    buy_sell_count_ratio.append(float(i['buy_sell_count_ratio']))
    vwap.append(float(i['vwap']))

timestamp = [datetime.strptime(i, '%Y-%m-%dT%H:%M:%S.%fZ') for i in timestamp]

for i in file1['data']:
    timestamp1.append(i['timestamp'])
for i in file2['data']:
    timestamp2.append(i['timestamp'])
timestamp1 = [datetime.strptime(i, '%Y-%m-%dT%H:%M:%S.%fZ') for i in timestamp1]
timestamp2 = [datetime.strptime(i, '%Y-%m-%dT%H:%M:%S.%fZ') for i in timestamp2]

timestamp_for_plots = list(timestamp)
timestamp_for_plots1 = list(timestamp1)
timestamp_for_plots2 = list(timestamp2)

first_digit_distribution = [[] for n in range(len(timestamp))]
volume = [[] for n in range(len(timestamp))]
count = [[] for n in range(len(timestamp))]
count_time_distribution = [[] for n in range(len(timestamp))]
index = 0
for i in file['data']:
    for j in i['count_time_distribution']:
        count_time_distribution[index].append(j)
    for j in i['first_digit_distribution']:
        first_digit_distribution[index].append(j)
    for j in i['volume_distribution']:
        volume[index].append(j['volume'])
        count[index].append(int(j['count']))
    index += 1
    
volume1 = [[] for n in range(len(timestamp1))]
count1 = [[] for n in range(len(timestamp1))]
count_time_distribution1 = [[] for n in range(len(timestamp1))]         
index1 = 0
for i in file1['data']:
    volume_distribution_mode1.append(float(i['volume_distribution_mode']))
    buy_sell_count_ratio1.append(float(i['buy_sell_count_ratio']))
    vwap1.append(float(i['vwap']))
    for j in i['count_time_distribution']:
        count_time_distribution1[index1].append(j)
    for j in i['volume_distribution']:
        volume1[index1].append(j['volume'])
        count1[index1].append(int(j['count']))
    index1 += 1

volume2 = [[] for n in range(len(timestamp2))]
count2 = [[] for n in range(len(timestamp2))]
count_time_distribution2 = [[] for n in range(len(timestamp2))]
index2 = 0
for i in file2['data']:
    volume_distribution_mode2.append(float(i['volume_distribution_mode']))
    buy_sell_count_ratio2.append(float(i['buy_sell_count_ratio']))
    vwap2.append(float(i['vwap']))
    for j in i['count_time_distribution']:
        count_time_distribution2[index2].append(j)
    for j in i['volume_distribution']:
        volume2[index2].append(j['volume'])
        count2[index2].append(int(j['count']))
    index2 += 1

for hour_full, hour in zip(timestamp_full, timestamp):
    if (hour_full - hour).days != 0:
        day = timestamp_full.index(hour_full)
        timestamp.insert(day, 0)
        volume_volatility_correlation.insert(day, 0)
        volume_distribution_kurtosis.insert(day, 0)
        volume_distribution_mean.insert(day, 0)
        volume_distribution_median.insert(day, 0)
        volume_distribution_mode.insert(day, 0)
        volume_distribution_skewness.insert(day, 0)
        volume_distribution_std.insert(day, 0)
        first_digit_distribution.insert(day, [0]*10)
        count_time_distribution.insert(day, count_time_to_insert)
        volume.insert(day, [])
        count.insert(day, [])
    elif (hour_full - hour).seconds != 0:
        a = timestamp_full.index(hour_full)
        timestamp.insert(a, 0)
        volume_volatility_correlation.insert(a, 0)
        volume_distribution_kurtosis.insert(a, 0)
        volume_distribution_mean.insert(a, 0)
        volume_distribution_median.insert(a, 0)
        volume_distribution_mode.insert(a, 0)
        volume_distribution_skewness.insert(a, 0)
        volume_distribution_std.insert(a, 0)
        first_digit_distribution.insert(a, [0]*10)
        count_time_distribution.insert(a, count_time_to_insert)
        volume.insert(a, [])
        count.insert(a, [])        
    else:
        continue

while len(timestamp) != len(timestamp_full):
    timestamp.append(0)
    volume_volatility_correlation.append(0)
    volume_distribution_kurtosis.append(0)
    volume_distribution_mean.append(0)
    volume_distribution_median.append(0)
    volume_distribution_mode.append(0)
    volume_distribution_skewness.append(0)
    volume_distribution_std.append(0)
    first_digit_distribution.append([0]*10)
    count_time_distribution.append(count_time_to_insert)
    volume.append([])
    count.append([])
    
for hour_full, hour in zip(timestamp_full, timestamp1):
    if (hour_full - hour).days != 0:
        day = timestamp_full.index(hour_full)
        timestamp1.insert(day, 0)
        volume_distribution_mode1.insert(day, 0)
        count_time_distribution1.insert(day, count_time_to_insert)
    elif (hour_full - hour).seconds != 0:
        a = timestamp_full.index(hour_full)
        timestamp1.insert(a, 0)
        volume_distribution_mode1.insert(a, 0)
        count_time_distribution1.insert(a, count_time_to_insert)
    else:
        continue

while len(timestamp1) != len(timestamp_full):
    timestamp1.append(0)
    volume_distribution_mode1.append(0)
    count_time_distribution1.append(count_time_to_insert)

for hour_full, hour in zip(timestamp_full, timestamp2):
    if (hour_full - hour).days != 0:
        day = timestamp_full.index(hour_full)
        timestamp2.insert(day, 0)
        volume_distribution_mode2.insert(day, 0)
        count_time_distribution2.insert(day, count_time_to_insert)
    elif (hour_full - hour).seconds != 0:
        a = timestamp_full.index(hour_full)
        timestamp2.insert(a, 0)
        volume_distribution_mode2.insert(a, 0)
        count_time_distribution2.insert(a, count_time_to_insert)
    else:
        continue

while len(timestamp2) != len(timestamp_full):
    timestamp2.append(0)
    volume_distribution_mode2.append(0)
    count_time_distribution2.append(count_time_to_insert)

count_time_distr = []
count_time_distr1 = []
count_time_distr2 = []
for i in count_time_distribution:
    for j in i:
        count_time_distr.append(j)
        
for i in count_time_distribution1:
    for j in i:
        count_time_distr1.append(j)
        
for i in count_time_distribution2:
    for j in i:
        count_time_distr2.append(j)

first_digit_chunks = [first_digit_distribution[i:i + period_for_benford] for i in range(0, len(first_digit_distribution), period_for_benford)]
chunks_quantity = int(len(timestamp_full)/period_for_benford)
first_digit_list = [[] for n in range(chunks_quantity)]
total = [[] for n in range(chunks_quantity)]
ind = 0
for i in first_digit_chunks:
    summ0 = 0
    summ1 = 0
    summ2 = 0
    summ3 = 0
    summ4 = 0
    summ5 = 0
    summ6 = 0
    summ7 = 0
    summ8 = 0
    summ9 = 0
    for j in i:
        summ0 += j[0]
        summ1 += j[1]
        summ2 += j[2]
        summ3 += j[3]
        summ4 += j[4]
        summ5 += j[5]
        summ6 += j[6]
        summ7 += j[7]
        summ8 += j[8]
        summ9 += j[9]
    first_digit_list[ind] = first_digit_list[ind] + [summ0, summ1, summ2, summ3, summ4, summ5, summ6, summ7, summ8, summ9]
    total[ind] = summ0 + summ1 + summ2 + summ3 + summ4 + summ5 + summ6 + summ7 + summ8 + summ9
    ind += 1

fig, ax = plt.subplots()
ax.set_ylabel('Volume-volatility correlation')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.bar(timestamp_full_for_bars, volume_volatility_correlation, width=0.7)
plt.xticks(timestamp_full_for_bars[::6], rotation=90, fontsize=4)
#plt.savefig('volume_volatility.png')

fig, ax = plt.subplots()
ax.set_ylabel('Volume_distribution_skewness')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.bar(timestamp_full_for_bars, volume_distribution_skewness, width=0.7)
plt.xticks(timestamp_full_for_bars[::6], rotation=90, fontsize=4)
#plt.savefig('skewness.png')

fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(16,18))
for x in axs:
    x.spines['right'].set_visible(False)
    x.spines['top'].set_visible(False)
    x.set_ylabel('Volume_distribution_mode')
axs[0].bar(timestamp_full_for_bars, volume_distribution_mode, width=0.7, color='blue')
axs[0].set_title(market_id)
axs[1].bar(timestamp_full_for_bars, volume_distribution_mode1, width=0.7, color='red')
axs[1].set_title(market_id1)
axs[2].bar(timestamp_full_for_bars, volume_distribution_mode2, width=0.7, color='green')
axs[2].set_title(market_id2)
plt.xticks(timestamp_full_for_bars[::6], rotation=90, fontsize=6)
#plt.savefig('mode.png')

fmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
lims = (start, end)
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(16,18))
for x in axs:
    x.xaxis.set_major_formatter(fmt)
    x.xaxis.set_major_locator(hours)
    x.spines['right'].set_visible(False)
    x.spines['top'].set_visible(False)
    x.set_ylim(-1, 1)
    x.set_xlim(lims)
    x.set_ylabel('Buy-sell_ratio')
    x.grid()
    x.tick_params(axis='x', which='major', labelsize=6)
axs[0].plot(timestamp_for_plots, buy_sell_count_ratio, color='blue')
axs[0].set_title(market_id)
axs[1].plot(timestamp_for_plots1, buy_sell_count_ratio1, color='red')
axs[1].set_title(market_id1)
axs[2].plot(timestamp_for_plots2, buy_sell_count_ratio2, color='green')
axs[2].set_title(market_id2)
fig.autofmt_xdate()
#plt.savefig('buy_sell.png')

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16,14))
ax.xaxis.set_major_formatter(fmt)
ax.xaxis.set_major_locator(hours)
ax.plot(timestamp_for_plots, vwap, color='blue', label=market_id)
ax.plot(timestamp_for_plots1, vwap1, color='red', label=market_id1)
ax.plot(timestamp_for_plots2, vwap2, color='green', label=market_id2)
ax.legend(loc='upper right')
ax.set_ylabel('VWAP')
ax.grid()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
fig.autofmt_xdate()
#plt.savefig('vwap.png')

fig = plt.figure()
plt.bar(timestamp_full_for_bars, volume_distribution_mean, width=0.9, color='red', alpha=0.6, label='Volume_distribution_mean')
plt.bar(timestamp_full_for_bars, volume_distribution_median, width=0.9, color='blue', alpha=0.4, label='Volume_distribution_median')
plt.legend(fontsize=6, loc='upper right')
plt.xticks(timestamp_full_for_bars[::6], rotation=50, fontsize=5)
x.spines['right'].set_visible(False)
x.spines['top'].set_visible(False)
#plt.savefig('mean and median.png')

fig, axes = plt.subplots(nrows=4, ncols=7, figsize=(24,10))
hour = start
axes = axes.ravel()
for i in range(chunks_quantity):
    benford_expectation = [0.301*total[i], 0.176*total[i], 0.125*total[i], 0.097*total[i], 0.079*total[i], 0.067*total[i], 0.058*total[i], 0.051*total[i], 0.046*total[i]]
    axes[i].bar(digits, first_digit_list[i], color='blue')
    axes[i].plot(significant_digits, benford_expectation, color='red')
    axes[i].spines['right'].set_visible(False)
    axes[i].spines['top'].set_visible(False)
    axes[i].tick_params(axis='both', which='major', labelsize=5)
    axes[i].text(2.5, max(first_digit_list[i]), s=hour.strftime('%Y-%m-%d %H:%M'), fontsize=5, color='green', fontweight='bold')
    axes[i].text(6.3, max(first_digit_list[i]), s='-', fontsize=5, color='green', fontweight='bold')
    axes[i].text(6.5, max(first_digit_list[i]), s=(hour+timedelta(hours=period_for_benford)).strftime('%Y-%m-%d %H:%M'), fontsize=5, color='green', fontweight='bold')
    hour += timedelta(hours=period_for_benford)
#plt.savefig('1st_digit_vs_benford.png')

locator = matplotlib.ticker.LinearLocator(6)
figures_volume_distr = []
figures_time_distr = []
b=0
while b != len(timestamp_full)/24:
    figure = plt.figure()
    axes = figure.subplots(nrows=8, ncols=3)
    axes = axes.ravel()
    for i in range(24):
        axes[i].bar(volume[b*24+i], count[b*24+i], alpha=0.7, color='blue')
        axes[i].grid()
        axes[i].xaxis.set_major_locator(locator)
        axes[i].spines['right'].set_visible(False)
        axes[i].spines['top'].set_visible(False)
        axes[i].tick_params(axis='both', which='major', labelsize=6)
    figures_volume_distr.append(figure)
    pdf = PdfPages("Volume_distribution.pdf")
    b += 1
#for figure in figures_volume_distr:
#    pdf.savefig(figure)

fig, axes = plt.subplots(nrows=7, ncols=1, figsize=(24,18))
c = 0
for i in range(int(len(timestamp_full)/24)):
    axes[i].plot(minutes[c*1440:(c+1)*1440], count_time_distr[c*1440:(c+1)*1440], color='blue', alpha=0.5, label=market_id)
    axes[i].plot(minutes[c*1440:(c+1)*1440], count_time_distr1[c*1440:(c+1)*1440], color='red', alpha=0.5, label=market_id1)
    axes[i].plot(minutes[c*1440:(c+1)*1440], count_time_distr2[c*1440:(c+1)*1440], color='black', alpha=0.5, label=market_id2)
    axes[i].legend(fontsize=6, loc='upper right')
    axes[i].spines['right'].set_visible(False)
    axes[i].spines['top'].set_visible(False)
    axes[i].tick_params(axis='both', which='major', labelsize=6)
    axes[i].xaxis.set_major_formatter(fmt)
    c += 1
#plt.savefig('time_distr.png')    


plt.show()

