'''
ADX convertver + volume changer (Just a fancy batch script with some logging) by agilly1989
Inspiration: A fellow called Kuiriel on discord
Requires: no external libraries BUT needs
-- ffmpeg.exe 3.2.2 (or similar version - supplied)
-- radx_encode.exe and radx_decode.exe from https://github.com/Isaac-Lozano/radx (supplied)
'''
import subprocess
from multiprocessing import Pool, Manager, freeze_support, TimeoutError
from queue import Queue, Full, Empty
import os
import sys
import shutil
import time
import traceback
    
def Jack(fileQueue: Queue, index:int,messageQueue:Queue,folders:dict,folderLock,compatibleFormats):
    try:
        IN_MOVIE = ['x11_00']
        ToPad = [['x62_00',30]]
        ToLimit = [['x49_04','1:28']]
        NO_LOOP = ['x62_00']
        messageQueue.put(f'Jack {index} is punching on')
        looping = True
        while looping:
            try:
                data = fileQueue.get(True,5)

                if not data["converted"][0]:
                    infile = data["original"]
                    outfile = data["converted"][1]
                    messageQueue.put(f'Jack {index} is converting {infile} to {outfile}')
                    if not os.path.exists(os.path.split(outfile)[0]):
                        folderLock.acquire()
                        os.makedirs(os.path.split(outfile)[0],exist_ok=True)
                        folderLock.release()
                    if data["extension"].upper() == "ADX":
                        command = 'radx_decode "{0}" "{1}"'.format(infile,outfile)
                    if data["extension"].upper() in compatibleFormats:
                        command = 'ffmpeg -y -loglevel fatal -i "{0}" -b:a 1536k -ac 2 -r:a 48k -c:a pcm_s16le "{1}"'.format(infile,outfile)
                    subprocess.call(command,stdout=subprocess.PIPE)
                    if os.path.exists(data['converted'][1]):
                        data.update({"converted":[True,os.path.join(folders['wav'],infile.split(os.sep)[-2],f'{os.path.splitext(os.path.split(infile)[1])[0]}.wav')]})
                        data.update({"retryCount":0})
                        fileQueue.put(data)
                    else:
                        with open(data['converted'][1] + ".failed", 'w') as filey:
                            filey.write("Error stuff here")
                            if data["retryCount"] < 10:
                                x = data["retryCount"] + 1
                                data.update({"retryCount":x})
                                fileQueue.put(data)
                            else:
                                filey.write("\nErrored too many times")
                    continue
                
                if not data["adjusted"][0]:
                    infile = data["converted"][1]
                    outfile = data["adjusted"][1]
                    messageQueue.put(f'Jack {index} is adjusting the volume of {infile}')
                    if not os.path.exists(os.path.split(outfile)[0]):
                        folderLock.acquire()
                        os.makedirs(os.path.split(outfile)[0],exist_ok=True)
                        folderLock.release()
                    base_ffmpeg = 'ffmpeg -y -loglevel fatal -i "{0}" -b:a 1536k -ac 2 -r:a 48k -c:a pcm_s16le -filter volume={1}'.format(infile,data["multiplier"])
                    
                    for x in ToPad:
                        if data["name"].upper() == x[0].upper():
                            base_ffmpeg += ' -af apad -t {0}'.format(x[1])
                            break
                    if data["name"].upper() == x[0].upper():
                        if name.upper() == x[0].upper():
                            base_ffmpeg += ' -t {0}'.format(x[1])
                            break
                    base_ffmpeg += ' "{0}"'.format(outfile)
                    subprocess.call(base_ffmpeg,stdout=subprocess.PIPE)

                    if os.path.exists(data['adjusted'][1]):
                        data.update({"adjusted":[True,os.path.join(folders['adjusted'],infile.split(os.sep)[-2],f'{os.path.splitext(os.path.split(infile)[1])[0]}.wav')]})
                        data.update({"retryCount":0})
                        fileQueue.put(data)
                    else:
                        with open(data['adjusted'][1] + ".failed", 'w') as filey:
                            filey.write("Error stuff here")
                            if data["retryCount"] < 10:
                                x = data["retryCount"] + 1
                                data.update({"retryCount":x})
                                fileQueue.put(data)
                            else:
                                filey.write("\nErrored too many times")
                    continue

                if not data["finished"][0]:
                    infile = data["adjusted"][1]
                    outfile = data["finished"][1]
                    messageQueue.put(f'Jack {index} is converting {infile} to {outfile}')
                    if not os.path.exists(os.path.split(outfile)[0]):
                        folderLock.acquire()
                        os.makedirs(os.path.split(outfile)[0],exist_ok=True)
                        folderLock.release()
                    command = 'ffmpeg -y -loglevel fatal -i "{0}" -b:a 1536k -ac 2 -r:a 48k -c:a pcm_s16le -filter volume={1}'.format(infile,data["multiplier"])
                    
                    if data['name'] in NO_LOOP:
                        command = 'radx_encode -n "{0}" "{1}"'.format(infile,outfile)
                    else:
                        command = 'radx_encode "{0}" "{1}"'.format(infile,outfile)
                    messageQueue.put(command)
                    subprocess.call(command,stdout=subprocess.PIPE)

                    if os.path.exists(data['finished'][1]):
                        data.update({"finished":[True,os.path.join(folders['output'],infile.split(os.sep)[-2],f'{os.path.splitext(os.path.split(infile)[1])[0]}.wav')]})
                        data.update({"retryCount":0})
                    else:
                        with open(data['finished'][1] + ".failed", 'w') as filey:
                            filey.write("Error stuff here")
                            if data["retryCount"] < 10:
                                x = data["retryCount"] + 1
                                data.update({"retryCount":x})
                                fileQueue.put(data)
                            else:
                                filey.write("\nErrored too many times")

            except Empty:
                messageQueue.put(f'Jack {index} is clocking off')
                looping = False
    except Exception:
        messageQueue.put(f'Jack {index} Errored -- \n {traceback.print_exc()}')

def Jill(messageQueue:Queue):
    print("Jill is punching on")
    looping = True
    with open('log.txt','w') as log:
        while looping:
            try:
                message = messageQueue.get(True)
                if message == "STOP":
                    print('Jill is clocking off')
                    looping = False
                    continue
                print(message)
                log.write(f'{message}\n')
            except Empty:
                looping = False

def main():
    folders = {
        'input':os.path.realpath('1 - input'),
        'wav':os.path.realpath('2 - wav'),
        'adjusted':os.path.realpath('3 - adjusted'),
        'output':os.path.realpath('4 - output')
    }

    compatibleFormats = ['MP3','WAV','FLAC','OGG']

    foldersMade = False
    for x in folders:
        if not os.path.exists(folders[x]):
            foldersMade = True
            os.makedirs(folders[x],exist_ok=True)
    
    if foldersMade:

        megaString = f'''
This appears to be the first time you have ran this program (or you deleted one of the folders). I have made 4 folders for you

* {folders['input']} << This is your input folder, you put folders in here with the name being the volume multiplier you want (see below)
* {folders['wav']} << This is a wav conversion of the file
* {folders['adjusted']} << This contains the altered (or un-altered files)
* {folders['output']} << This contains the new adx files

What I need you to do, is to put either .adx, {", .".join(compatibleFormats[:-1]).lower()} or .{compatibleFormats[-1].lower()} files into
   folders you want as the increase (or decrease) of volume.... for example
 {' '*len(folders['input'])}vvv
{os.path.join(folders['input'],'2.0','file.adx')} < this file will have its volume doubled
{os.path.join(folders['input'],'0.5','file.mp3')} < this file will have its volume halved
{os.path.join(folders['input'],'1.0','file.ogg')} < this file will have its volume unchanged
 {' '*len(folders['input'])}^^^
Please note this folder, This is the multiplier for the volume of the output file, whole numbers or decimals are fine
'''
        with open('readme - part 2.md', 'w') as readme:
            readme.write(megaString)
        print(megaString)
        input('Press enter to quit, this info has also been logged to "readme - part 2.md"')
        exit(0)
 
    with Manager() as manager:
        messageQueue = manager.Queue()
        fileQueue = manager.Queue()
        folderLock = manager.Lock()
        threads = os.cpu_count()
        with Pool(threads) as pool:
            jillThread = pool.apply_async(func=Jill,args=(messageQueue,))
            jackThreads = [pool.apply_async(func=Jack,args=(fileQueue,x,messageQueue,folders,folderLock,compatibleFormats)) for x in range(0,threads-1)] # fix this up later
            for root,_,files in os.walk(folders['input']):
                for file in files:
                    wholePath = os.path.join(root,file)
                    y = {
                "name":os.path.splitext(os.path.split(wholePath)[1])[0],
                "extension":os.path.splitext(os.path.split(wholePath)[1])[1][1:],
                "multiplier": wholePath.split(os.sep)[-2],
                "original":wholePath,
                "converted":[False,os.path.join(folders['wav'],wholePath.split(os.sep)[-2],f'{os.path.splitext(os.path.split(wholePath)[1])[0]}.wav')],
                "adjusted":[False,os.path.join(folders['adjusted'],wholePath.split(os.sep)[-2],f'{os.path.splitext(os.path.split(wholePath)[1])[0]}.wav')],
                "finished":[False,os.path.join(folders['output'],wholePath.split(os.sep)[-2],f'{os.path.splitext(os.path.split(wholePath)[1])[0]}.adx')],
                "retryCount": 0
            }
                    fileQueue.put(y)
            for x in jackThreads:
                x.wait()

            messageQueue.put("STOP")
            jillThread.wait()
                   

if __name__ == "__main__":
    freeze_support()
    main()