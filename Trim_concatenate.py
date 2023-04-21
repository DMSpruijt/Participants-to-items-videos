"""Importing relevant packages"""
import pandas as pd
import os
import subprocess
import glob

"""Determining in- and output paths"""
#csv
csvPath     =   'CSV/'      #location of the csv files
#trim
triminPath  =   'Videos/Raw/'       #location of the original participant recordings
trimoutPath =   'Videos/PP_Item/'   #location you want to store the individual item videos
#concatenate
concinPath  =   trimoutPath         #location of the individual item videos, in this case the same as the output folder of the trim
concoutPath =   'Videos/Item/'      #location you want to store the concatenated item videos
tempPath    =   'temp/'             #location you want to store the temp files needed to create the concatenated item videos

"""Loading Trim CSV"""
CSV_trim = pd.read_csv(csvPath+'InputTrim.csv')
#Contains a row for each desired clip, with the columns Input (the input file name), StartTime (of the desired clip), Duration (of the desired clip) and Output (the name the output file should have).
#The Timestamps.py script can provide the first three columns, but the Output column should be added separately, based on your experiment's randomization, so each output name matches the item number in that clip.
#Instead of Duration you can also use an EndTime, but you will need to change '-t' to '-to' in line 27.
#The example Output filenames are formatted as [participant number]_[item number].mp4 (e.g. 15_191.mp4). For proper concatenation, the itemnumber should be unique in the name.

"""FFMpeg - Trim"""
#Cuts up the original participant files by the timestamps you have provided in the InputTrim CSV.
def trim_video(video,output):
    ffcommand = f"ffmpeg -ss '{CSV_trim.at[i,'StartTime']}' -i '{triminPath+CSV_trim.at[i,'Input']}' -t '{CSV_trim.at[i,'Duration']}' -f mp4 -c:v h264_videotoolbox -b:v 6000k '{trimoutPath+CSV_trim.at[i,'Output']}'"
    #Having '-ss' before '-i' makes the script enormously faster than the other way around, but it may result in some quality/frame loss.
    #Change '-t' to '-to' to use end times instead of duration.
    #If your input is not .mp4, the reencoding may take some extra time.
    subprocess.call(ffcommand,shell=True)

for i, row in CSV_trim.iterrows():          #running the trim function on every row of the input file
    trim_video(CSV_trim.at[i,'Input'],CSV_trim.at[i,'Output'])
    print(CSV_trim.at[i,'Output'],"was created.")

"""Loading Concatenate CSV"""
CSV_conc = pd.read_csv(csvPath+'InputConcatenate.csv')
#Contains a row for each desired concatenated item video, with the columns Input and Output.
#The example Input is formatted as *[item number].* (e.g. *191.*) to search for all files with a name ending in the item number.
#The example Output is formatted as [production type]_[language]_[concept]_[category code]_[itemnumber].mp4 (e.g. GG_DE_SPOON_C14_191.mp4).

"""FFMpeg - Concatenate by item""" ### Code copied and adapted from https://www.youtube.com/watch?v=ch14IFfPtDI
#Concatenates the trimmed clips of an item, sorted by participant number.
def concatenate(input,output):
    tc_stringa = "ffmpeg -i \"concat:"
    tc_video = sorted(glob.glob(concinPath+CSV_conc.at[k,'Input'])) #sorts all files found in the specified directory that match the item number in a string
    tc_file_temp = []
    for v in tc_video:  #create a temp file for each of the videos
        file = "temp" + str(tc_video.index(v) + 1) + ".ts"
        os.system(f"ffmpeg -y -i " + v + " -c copy -f mpegts " + tempPath + file)      # "-y" automatically answers 'yes' when prompted to overwrite (in this case temp files)
        tc_file_temp.append(tempPath+file)
    print(tc_file_temp)
    for q in tc_file_temp:  #creating the ffmpeg code to include all temp files
        tc_stringa += q
        if tc_file_temp.index(q) != len(tc_file_temp)-1:
            tc_stringa += "|"
        else:
            tc_stringa += f"\" -c copy '{concoutPath+CSV_conc.at[k,'Output']}'"
    print(tc_stringa)
    os.system(tc_stringa)

for k, row in CSV_conc.iterrows():          #running the concatenate function on every row of the input file
    concatenate(concinPath+CSV_conc.at[k,'Input'],concoutPath+CSV_conc.at[k,'Output'])
    print(CSV_conc.at[k,'Output'],"was created.")