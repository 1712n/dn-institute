import os
import json
from datetime import timedelta, datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, LogLocator
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages

with open("bybit-ava-usdt_2.json", 'r') as d:
    file = json.load(d)
with open('gateio-ava-usdt.json', 'r') as d1:
    file1 = json.load(d1)
with open('binance-ava-usdt.json', 'r') as d2:
    file2 = json.load(d2)

start = datetime.strptime('2023-11-10T10:00:00', '%Y-%m-%dT%H:%M:%S')
end = datetime.strptime('2023-11-16T10:00:00', '%Y-%m-%dT%H:%M:%S')
numhours = (end -start)/timedelta(hours=1)
period_for_benford = 6        #there is 28 graphs in the figure, the interval should be no less than numhours/28
hours = mdates.HourLocator(interval=6)

timestamp_full = [start + timedelta(hours=x) for x in  range(int(numhours))]
timestamp_full_for_bars = [x.strftime('%Y-%m-%d %H:%M') for x in  timestamp_full]
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
     
volume_distribution_median = [float(i['volume_distribution_median']) for i in file['data']]
volume_distribution_mean = [float(i['volume_distribution_mean']) for i in file['data']]
volume_distribution_kurtosis = [float(i['volume_distribution_kurtosis']) for i in file['data']]
volume_distribution_skewness = [float(i['volume_distribution_skewness']) for i in file['data']]
volume_distribution_std = [float(i['volume_distribution_std']) for i in file['data']]
volume_volatility_correlation = [float(i['volume_volatility_correlation']) for i in file['data']]
volume_distribution_mode = [float(i['volume_distribution_mode']) for i in file['data']]
volume_distribution_mode1 = [float(i['volume_distribution_mode']) for i in file1['data']]
volume_distribution_mode2 = [float(i['volume_distribution_mode']) for i in file2['data']]
buy_sell_count_ratio = [float(i['buy_sell_count_ratio']) for i in file['data']]
buy_sell_count_ratio1 = [float(i['buy_sell_count_ratio']) for i in file1['data']]
buy_sell_count_ratio2 = [float(i['buy_sell_count_ratio']) for i in file2['data']]
vwap = [float(i['vwap']) for i in file['data']]
vwap1 = [float(i['vwap']) for i in file1['data']]
vwap2 = [float(i['vwap']) for i in file2['data']]

timestamp = [i['timestamp'] for i in file['data']]
timestamp = [datetime.strptime(i, '%Y-%m-%dT%H:%M:%S.%fZ') for i in timestamp]
timestamp1 = [i['timestamp'] for i in file1['data']]
timestamp1 = [datetime.strptime(i, '%Y-%m-%dT%H:%M:%S.%fZ') for i in timestamp1]
timestamp2 = [i['timestamp'] for i in file2['data']]
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
        count_time_distribution[index].append(int(j))
    for j in i['first_digit_distribution']:
        first_digit_distribution[index].append(int(j))
    for j in i['volume_distribution']:
        volume[index].append(float(j['volume']))
        count[index].append(int(j['count']))
    index += 1
    
count_time_distribution1 = [[] for n in range(len(timestamp1))]         
index1 = 0
for i in file1['data']:
    for j in i['count_time_distribution']:
        count_time_distribution1[index1].append(int(j))
    index1 += 1

count_time_distribution2 = [[] for n in range(len(timestamp2))]
index2 = 0
for i in file2['data']:
    for j in i['count_time_distribution']:
        count_time_distribution2[index2].append(int(j))
    index2 += 1

for hour_full, hour in zip(timestamp_full, timestamp):
    if (hour_full - hour).days != 0:
        day = timestamp_full.index(hour_full)
        volume_distribution_mean.insert(day, 0)
        volume_distribution_median.insert(day, 0)
        volume_distribution_kurtosis.insert(day, 0)
        volume_distribution_skewness.insert(day, 0)
        volume_distribution_std.insert(day, 0)
        timestamp.insert(day, 0)
        volume_volatility_correlation.insert(day, 0)
        volume_distribution_mode.insert(day, 0)
        first_digit_distribution.insert(day, [0]*10)
        count_time_distribution.insert(day, count_time_to_insert)
        volume.insert(day, [])
        count.insert(day, [])
    elif (hour_full - hour).seconds != 0:
        a = timestamp_full.index(hour_full)
        volume_distribution_mean.insert(a, 0)
        volume_distribution_median.insert(a, 0)
        volume_distribution_kurtosis.insert(a, 0)
        volume_distribution_skewness.insert(a, 0)
        volume_distribution_std.insert(a, 0)
        timestamp.insert(a, 0)
        volume_volatility_correlation.insert(a, 0)
        volume_distribution_mode.insert(a, 0)
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
plt.xticks(timestamp_full_for_bars[::6], rotation=90, fontsize=5)
#plt.savefig('volume_volatility.png')

fig, ax = plt.subplots()
ax.set_ylabel('Volume_distribution_skewness')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.bar(timestamp_full_for_bars, volume_distribution_skewness, width=0.7)
plt.xticks(timestamp_full_for_bars[::6], rotation=90, fontsize=5)
#plt.savefig('skewness.png')

fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(16,18))
axs[0].bar(timestamp_full_for_bars, volume_distribution_mode, width=0.7, color='blue')
axs[0].set_title(market_id)
axs[1].bar(timestamp_full_for_bars, volume_distribution_mode1, width=0.7, color='red')
axs[1].set_title(market_id1)
axs[2].bar(timestamp_full_for_bars, volume_distribution_mode2, width=0.7, color='green')
axs[2].set_title(market_id2)
for x in axs:
    x.spines['right'].set_visible(False)
    x.spines['top'].set_visible(False)
    x.set_ylabel('Volume_distribution_mode')
plt.xticks(timestamp_full_for_bars[::6], rotation=90, fontsize=6)
#plt.savefig('mode.png')

fmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
fig, ax = plt.subplots(nrows=1, ncols=1)
ax.plot(timestamp_for_plots, buy_sell_count_ratio, color='blue', label=market_id)
ax.plot(timestamp_for_plots1, buy_sell_count_ratio1, color='red', label=market_id1)
ax.plot(timestamp_for_plots2, buy_sell_count_ratio2, color='green', label=market_id2)
ax.legend(loc='upper right')
ax.xaxis.set_major_formatter(fmt)
ax.xaxis.set_major_locator(hours)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_ylim(-1, 1)
ax.set_xlim(start, end)
ax.set_ylabel('Buy-sell_ratio')
ax.grid()
ax.tick_params(axis='x', which='major', labelsize=6)
fig.autofmt_xdate()
#plt.savefig('buy_sell.png')

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16,14))
ax.xaxis.set_major_formatter(fmt)
ax.xaxis.set_major_locator(hours)
ax.plot(timestamp_for_plots, vwap, color='blue', label=market_id, linewidth=0.5)
ax.plot(timestamp_for_plots1, vwap1, color='red', label=market_id1, linewidth=0.5)
ax.plot(timestamp_for_plots2, vwap2, color='green', label=market_id2, linewidth=0.5)
ax.legend(loc='upper right')
ax.set_ylabel('VWAP')
ax.grid()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
fig.autofmt_xdate()
#plt.savefig('vwap.png')

fig, axes = plt.subplots(nrows=4, ncols=7, figsize=(24,10))
plt.subplots_adjust(wspace=0.2, hspace=0.2)
hour = start
axes = axes.ravel()
for i in range(chunks_quantity):
    axes[i].spines['right'].set_visible(False)
    axes[i].spines['top'].set_visible(False)
    if max(first_digit_list[i]) > 0:
        axes[i].bar(digits, first_digit_list[i], color='blue')
        axes[i].tick_params(axis='both', which='major', labelsize=5)    
        benford_expectation = [0.301*total[i], 0.176*total[i], 0.125*total[i], 0.097*total[i], 0.079*total[i], 0.067*total[i], 0.058*total[i], 0.051*total[i], 0.046*total[i]]
        axes[i].plot(significant_digits, benford_expectation, color='red', label="Benford's expectation")
        axes[i].legend(title=hour.strftime('%m-%d %H:%M')+' - '+(hour+timedelta(hours=period_for_benford)).strftime('%m-%d %H:%M'), fontsize=4, title_fontsize= 5, loc='upper right')
    else:
        axes[i].tick_params(left=False, bottom=False, labelleft=False ,labelbottom=False)
    hour += timedelta(hours=period_for_benford)
#plt.savefig('1st_digit_vs_benford.png')

figures_volume_distr = []
figures_time_distr = []
b=0
day_ = start
while b != int((end -start)/timedelta(days=1)):
    figure = plt.figure()
    axes = figure.subplots(nrows=8, ncols=3)
    plt.subplots_adjust(wspace=0.2, hspace=0.3)
    plt.suptitle(day_.strftime('%Y-%m-%d %H:%M')+' - '+(day_+timedelta(hours=24)).strftime('%Y-%m-%d %H:%M'))
    hour_ = start
    axes = axes.ravel()
    for i in range(24):
        axes[i].spines['right'].set_visible(False)
        axes[i].spines['top'].set_visible(False)
        if len(count[b*24+i]) > 0:
            axes[i].plot(volume[b*24+i], count[b*24+i], alpha=0.5, color='blue', linewidth=0.5)
            axes[i].tick_params(axis='both', which='major', labelsize=6)
            line1 = axes[i].axvline(volume_distribution_mean[b*24+i], color='red', linewidth=1, label='mean')
            line2 = axes[i].axvline(volume_distribution_median[b*24+i], color='yellow', linewidth=1, label='median')
            line3 = axes[i].axvline(volume_distribution_mode[b*24+i], color='black', linewidth=1, label='mode')
            axes[i].legend([line1, line2, line3], ['mean', 'median', 'mode'], title=hour.strftime('%m-%d %H:%M')+' - '+(hour+timedelta(hours=1)).strftime('%m-%d %H:%M'), fontsize=4, title_fontsize= 5, loc='upper right')
            axes[i].text(max(volume[b*24+i]), max(count[b*24+i]), s='kurtosis=(%s)'%volume_distribution_kurtosis[b*24+i], fontsize=6, fontweight='bold', style='italic')
            axes[i].text(min(volume[b*24+i]), max(count[b*24+i]), s='skewness=(%s)'%volume_distribution_skewness[b*24+i], fontsize=6, fontweight='bold', style='italic')
            axes[i].text(max(volume[b*24+i]), 0, 'std=(%s)'%volume_distribution_std[b*24+i], fontsize=6, fontweight='bold', style='italic') 
            axes[i].grid()
            axes[i].tick_params(axis='both', which='major', labelsize=6)
            axes[i].yaxis.set_ticks([min(count[b*24+i]), max(count[b*24+i])])
            if max(volume[b*24+i]) < 200*min(volume[b*24+i]):
                axes[i].xaxis.set_major_locator(MaxNLocator())
            else:
                axes[i].semilogx()  
        else:
            axes[i].tick_params(left=False, bottom=False, labelleft=False ,labelbottom=False)            
        hour_ += timedelta(hours=1)
    figures_volume_distr.append(figure)
    pdf = PdfPages("Volume_distribution.pdf")
    b += 1
    day_ += timedelta(hours=24) 
#for figure in figures_volume_distr:
#    pdf.savefig(figure)

fig, axes = plt.subplots(nrows=int((end -start)/timedelta(days=1)), ncols=1, figsize=(24,18))
c = 0
for i in range(int(len(timestamp_full)/24)):
    axes[i].spines['right'].set_visible(False)
    axes[i].spines['top'].set_visible(False)
    if max(count_time_distr[c*1440:(c+1)*1440]) != 0:
        axes[i].set_ylim(min(count_time_distr[c*1440:(c+1)*1440]), max(count_time_distr[c*1440:(c+1)*1440]))
        axes[i].plot(minutes[c*1440:(c+1)*1440], count_time_distr[c*1440:(c+1)*1440], color='blue', alpha=0.9, label=market_id, linewidth=0.5)
        axes[i].plot(minutes[c*1440:(c+1)*1440], count_time_distr1[c*1440:(c+1)*1440], color='red', alpha=0.9, label=market_id1, linewidth=0.5)
        axes[i].plot(minutes[c*1440:(c+1)*1440], count_time_distr2[c*1440:(c+1)*1440], color='green', alpha=0.9, label=market_id2, linewidth=0.5)
        axes[i].legend(fontsize=6, loc='upper right')        
        axes[i].tick_params(axis='both', which='major', labelsize=6)
        axes[i].xaxis.set_major_formatter(fmt)
    else:
        axes[i].tick_params(left=False, bottom=False, labelleft=False ,labelbottom=False)
    c += 1
#plt.savefig('time_distr.png')    

plt.show()