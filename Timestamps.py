"""Importing relevant packages"""
import pandas as pd

"""Determining in- and output paths and loading the CSV""" #since input and output are both CSV-files, the location is the same
csvPath     =   'CSV/'
CSV_ts      =   pd.read_csv(csvPath+'InputTimestamps.csv')
print(CSV_ts)

"""Define the variables for timestamp generation"""
#number of items/timestamps you want to generate per participant recording
no_items = 7

#time between items (including pauses/focus crosshairs/etc.)
interval = '4500ms' #timedelta_range frequency strings you can use as start times/frequency: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
duration = '00:00:06.000' #formatted as hh:mm:ss.msmsms to be readable by ffmpeg in the trim code
#The duration of the clip can be longer than the presentation of the stimulus to catch runover responses

"""Generating the partial InputTrim file"""
dl = []
for t, row in CSV_ts.iterrows():
    timestamps = pd.timedelta_range(start=CSV_ts.at[t,'StartTime'], periods=no_items, freq=interval) #timedelta_range frequency strings you can use as start times/frequency: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    timestamps = timestamps + pd.to_datetime(0)     #converting the timestamp strings to datetime format
    timestamps = timestamps.strftime('%H:%M:%S.%f') #formatting the timestamp to hh:mm:ss.microsecond
    timestamps = timestamps.str[:-3]                #removing the three final digits from the 6 microsecond digits
    ts = pd.DataFrame(timestamps)                   #loading the timestamps in a dataframe
    ts.columns = ['StartTime']                      #adding a column header
    ts.insert(0,'Input',CSV_ts.at[t,'Filename'])    #adding the file name these timestamps apply to in a new column
    dl.append(ts)                                   #writing the dataframe to a list
df = pd.concat(dl, ignore_index=True)               #concatenating the dataframes from the dl-list to a large dataframe
df.insert(2,'Duration',duration)                    #adding the duration you want the trimmed clips to have to each row

df.to_csv(csvPath+'InputTrimPartial.csv',index=False)     #writing the dataframe to a CSV-file