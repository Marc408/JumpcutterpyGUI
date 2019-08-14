import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import qtmodern
from pytube import YouTube
import os
import argparse
from jumpcutter_functions import downloadFile, getMaxVolume, copyFrame, inputToOutputFilename, createPath, deletePath
from contextlib import closing
from PIL import Image
import subprocess
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from scipy.io import wavfile
import numpy as np
import re
import math
from shutil import copyfile, rmtree
import winsound

frequency = 400  # Set Frequency To 2500 Hertz
duration = 500  # Set Duration To 1000 ms == 1 second





qtCreatorFile = "jumpcutter.ui" 
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):   
    
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        def on_run_button_clicked():
            run_process()

        def on_cancel_button_clicked():
            sys.exit()

        def on_browse_button_clicked(): 
            fileDialog = QtWidgets.QFileDialog()
            fileDialog.setFileMode(QtWidgets.QFileDialog.AnyFile)

            if fileDialog.exec_():
                fileNames = fileDialog.selectedFiles()

            self.fileLineEdit.setText(fileNames[0])

            
        def on_soundedSpeedSlider_valueChanged():
            self.soundedSpeedLineEdit.setText(str(self.soundedSpeedSlider.value()))
        
        def on_silentSpeedSlider_valueChanged():
            self.silentSpeedLineEdit.setText(str(self.silentSpeedSlider.value()))

        def on_frameMarginSlider_valueChanged():
            self.frameMarginLineEdit.setText(str(self.frameMarginSlider.value()))

        def on_sampleRateSlider_valueChanged():
            self.sampleRateLineEdit.setText(str(self.sampleRateSlider.value()))

        def on_frameRateSlider_valueChanged():
            self.frameRateLineEdit.setText(str(self.frameRateSlider.value()))

        def on_frameQualitySlider_valueChanged():
            self.frameQualityLineEdit.setText(str(self.frameQualitySlider.value()))

        def on_thresholdLineEdit_textEdited():
            if (self.thresholdLineEdit.text() == ''):
                self.thresholdSlider.setValue(0)
            else:
                self.thresholdSlider.setValue(float(self.thresholdLineEdit.text()))

        def on_soundedSpeedLineEdit_textEdited():
            if (self.soundedSpeedLineEdit.text() == ''):
                self.soundedSpeedSlider.setValue(0)
            else:
                self.soundedSpeedSlider.setValue(int(self.soundedSpeedLineEdit.text()))

        def on_silentSpeedLineEdit_textEdited():
            if (self.silentSpeedLineEdit.text() == ''):
                self.silentSpeedSlider.setValue(0)
            else:
                self.silentSpeedSlider.setValue(int(self.silentSpeedLineEdit.text()))

        def on_frameMarginLineEdit_textEdited():
            if (self.frameMarginLineEdit.text() == ''):
                self.frameMarginSlider.setValue(0)
            else:
                self.frameMarginSlider.setValue(int(self.frameMarginLineEdit.text()))

        def on_sampleRateLineEdit_textEdited():
            if (self.sampleRateLineEdit.text() == ''):
                self.sampleRateSlider.setValue(0)
            else:
                self.sampleRateSlider.setValue(int(self.sampleRateLineEdit.text()))

        def on_frameRateLineEdit_textEdited():
            if (self.frameRateLineEdit.text() == ''):
                self.frameRateSlider.setValue(0)
            else:
                self.frameRateSlider.setValue(int(self.frameRateLineEdit.text()))

        def on_frameQualityLineEdit_textEdited():
            if (self.frameQualityLineEdit.text() == ''):
                self.frameQualitySlider.setValue(0)
            else:
                self.frameQualitySlider.setValue(int(self.thresholdLineEdit.text()))


        def reset_values():
            self.thresholdLineEdit.setText(str(THRESHOLD_DEFAULT))

            self.soundedSpeedLineEdit.setText(str(SOUNDED_SPEED_DEFAULT))
            self.soundedSpeedSlider.setValue(SOUNDED_SPEED_DEFAULT)

            self.silentSpeedLineEdit.setText(str(SILENT_SPEED_DEFAULT))
            self.silentSpeedSlider.setValue(SILENT_SPEED_DEFAULT)

            self.frameMarginLineEdit.setText(str(FRAME_MARGIN_DEFAULT))
            self.frameMarginSlider.setValue(FRAME_MARGIN_DEFAULT)

            self.sampleRateLineEdit.setText(str(SAMPLE_RATE_DEFAULT))
            self.sampleRateSlider.setValue(SAMPLE_RATE_DEFAULT)

            self.frameRateLineEdit.setText(str(FRAME_RATE_DEFAULT))
            self.frameRateSlider.setValue(FRAME_RATE_DEFAULT)

            self.frameQualityLineEdit.setText(str(FRAME_QUALITY_DEFAULT))
            self.frameMarginSlider.setValue(FRAME_QUALITY_DEFAULT)

            
        def run_process():

            URL = self.URLLineEdit.text()
            if(self.URLRadio.isChecked()):
                INPUT_FILE = downloadFile(URL)
            else:
                INPUT_FILE = self.fileLineEdit.text()
            
            if (INPUT_FILE == ''):
                winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)

            else:
                frameRate = self.frameRateSlider.value()
                SAMPLE_RATE = self.sampleRateSlider.value()
                SILENT_THRESHOLD = float(self.thresholdLineEdit.text())
                FRAME_SPREADAGE = float(self.frameMarginSlider.value())
                SILENT_SPEED = float(self.silentSpeedLineEdit.text())
                SOUNDED_SPEED = float(self.soundedSpeedLineEdit.text())
                NEW_SPEED = [SILENT_SPEED, SOUNDED_SPEED]
                print(NEW_SPEED)
                
                
                FRAME_QUALITY = float(self.frameQualitySlider.value())

                assert INPUT_FILE != None , "why u put no input file, that dum"

                """   
                if len(args.output_file) >= 1:
                    OUTPUT_FILE = args.output_file
                else:
                """

                OUTPUT_FILE = inputToOutputFilename(INPUT_FILE)

                TEMP_FOLDER = "TEMP"
                AUDIO_FADE_ENVELOPE_SIZE = 400 # smooth out transitiion's audio by quickly fading in/out (arbitrary magic number whatever)
                    
                createPath(TEMP_FOLDER)

                command = "ffmpeg -i "+INPUT_FILE+" -qscale:v "+str(FRAME_QUALITY)+" "+TEMP_FOLDER+"/frame%06d.jpg -hide_banner"
                subprocess.call(command, shell=True)

                command = "ffmpeg -i "+INPUT_FILE+" -ab 160k -ac 2 -ar "+str(SAMPLE_RATE)+" -vn "+TEMP_FOLDER+"/audio.wav"

                subprocess.call(command, shell=True)

                command = "ffmpeg -i "+TEMP_FOLDER+"/input.mp4 2>&1"
                f = open(TEMP_FOLDER+"/params.txt", "w")
                subprocess.call(command, shell=True, stdout=f)

                sampleRate, audioData = wavfile.read(TEMP_FOLDER+"/audio.wav")
                audioSampleCount = audioData.shape[0]
                maxAudioVolume = getMaxVolume(audioData)

                f = open(TEMP_FOLDER+"/params.txt", 'r+')
                pre_params = f.read()
                f.close()
                params = pre_params.split('\n')
                for line in params:
                    m = re.search('Stream #.*Video.* ([0-9]*) fps',line)
                    if m is not None:
                        frameRate = float(m.group(1))

                samplesPerFrame = sampleRate/frameRate

                audioFrameCount = int(math.ceil(audioSampleCount/samplesPerFrame))

                hasLoudAudio = np.zeros((audioFrameCount))



                for i in range(audioFrameCount):
                    start = int(i*samplesPerFrame)
                    end = min(int((i+1)*samplesPerFrame),audioSampleCount)
                    audiochunks = audioData[start:end]
                    maxchunksVolume = float(getMaxVolume(audiochunks))/maxAudioVolume
                    if maxchunksVolume >= SILENT_THRESHOLD:
                        hasLoudAudio[i] = 1

                chunks = [[0,0,0]]
                shouldIncludeFrame = np.zeros((audioFrameCount))
                for i in range(audioFrameCount):
                    start = int(max(0,i-FRAME_SPREADAGE))
                    end = int(min(audioFrameCount,i+1+FRAME_SPREADAGE))
                    shouldIncludeFrame[i] = np.max(hasLoudAudio[start:end])
                    if (i >= 1 and shouldIncludeFrame[i] != shouldIncludeFrame[i-1]): # Did we flip?
                        chunks.append([chunks[-1][1],i,shouldIncludeFrame[i-1]])

                chunks.append([chunks[-1][1],audioFrameCount,shouldIncludeFrame[i-1]])
                chunks = chunks[1:]

                outputAudioData = np.zeros((0,audioData.shape[1]))
                outputPointer = 0

                lastExistingFrame = None
                for chunk in chunks:
                    audioChunk = audioData[int(chunk[0]*samplesPerFrame):int(chunk[1]*samplesPerFrame)]
                    
                    sFile = TEMP_FOLDER+"/tempStart.wav"
                    eFile = TEMP_FOLDER+"/tempEnd.wav"
                    wavfile.write(sFile,SAMPLE_RATE,audioChunk)
                    with WavReader(sFile) as reader:
                        with WavWriter(eFile, reader.channels, reader.samplerate) as writer:
                            tsm = phasevocoder(reader.channels, speed=NEW_SPEED[int(chunk[2])])
                            tsm.run(reader, writer)
                    _, alteredAudioData = wavfile.read(eFile)
                    leng = alteredAudioData.shape[0]
                    endPointer = outputPointer+leng
                    outputAudioData = np.concatenate((outputAudioData,alteredAudioData/maxAudioVolume))

                    #outputAudioData[outputPointer:endPointer] = alteredAudioData/maxAudioVolume

                    # smooth out transitiion's audio by quickly fading in/out
                    
                    if leng < AUDIO_FADE_ENVELOPE_SIZE:
                        outputAudioData[outputPointer:endPointer] = 0 # audio is less than 0.01 sec, let's just remove it.
                    else:
                        premask = np.arange(AUDIO_FADE_ENVELOPE_SIZE)/AUDIO_FADE_ENVELOPE_SIZE
                        mask = np.repeat(premask[:, np.newaxis],2,axis=1) # make the fade-envelope mask stereo
                        outputAudioData[outputPointer:outputPointer+AUDIO_FADE_ENVELOPE_SIZE] *= mask
                        outputAudioData[endPointer-AUDIO_FADE_ENVELOPE_SIZE:endPointer] *= 1-mask

                    startOutputFrame = int(math.ceil(outputPointer/samplesPerFrame))
                    endOutputFrame = int(math.ceil(endPointer/samplesPerFrame))
                    for outputFrame in range(startOutputFrame, endOutputFrame):
                        inputFrame = int(chunk[0]+NEW_SPEED[int(chunk[2])]*(outputFrame-startOutputFrame))
                        didItWork = copyFrame(inputFrame,outputFrame,TEMP_FOLDER)
                        if didItWork:
                            lastExistingFrame = inputFrame
                        else:
                            copyFrame(lastExistingFrame,outputFrame,TEMP_FOLDER)

                    outputPointer = endPointer

                wavfile.write(TEMP_FOLDER+"/audioNew.wav",SAMPLE_RATE,outputAudioData)

                '''
                outputFrame = math.ceil(outputPointer/samplesPerFrame)
                for endGap in range(outputFrame,audioFrameCount):
                    copyFrame(int(audioSampleCount/samplesPerFrame)-1,endGap)
                '''

                command = "ffmpeg -framerate "+str(frameRate)+" -i "+TEMP_FOLDER+"/newFrame%06d.jpg -i "+TEMP_FOLDER+"/audioNew.wav -strict -2 "+OUTPUT_FILE
                subprocess.call(command, shell=True)

                deletePath(TEMP_FOLDER)

        def toggleRadio(radio):
            print(radio)
    

        """ 
            Variables

        """

        THRESHOLD_DEFAULT = 0.03
        SOUNDED_SPEED_DEFAULT = 1
        SILENT_SPEED_DEFAULT = 5
        FRAME_MARGIN_DEFAULT = 1
        SAMPLE_RATE_DEFAULT = 44100
        FRAME_RATE_DEFAULT = 30
        FRAME_QUALITY_DEFAULT = 3

        self.defaultButton = self.findChild(QtWidgets.QPushButton, 'defaultButton')
        self.runButton = self.findChild(QtWidgets.QPushButton, 'runButton')
        self.cancelButton = self.findChild(QtWidgets.QPushButton, 'cancelButton')
        self.browseButton = self.findChild(QtWidgets.QPushButton, 'browseButton')
        self.fileLineEdit = self.findChild(QtWidgets.QLineEdit, 'fileLineEdit')
        self.URLLineEdit = self.findChild(QtWidgets.QLineEdit, 'URLLineEdit')
        self.URLRadio = self.findChild(QtWidgets.QRadioButton, 'URLRadio')
        self.fileRadio = self.findChild(QtWidgets.QRadioButton, 'fileRadio')


        self.thresholdSlider = self.findChild(QtWidgets.QSlider, 'thresholdSlider')
        self.thresholdLineEdit = self.findChild(QtWidgets.QLineEdit, 'thresholdLineEdit')
        self.thresholdLineEdit.textEdited.connect(on_thresholdLineEdit_textEdited)
        
        self.soundedSpeedSlider = self.findChild(QtWidgets.QSlider, 'soundedSpeedSlider')
        self.soundedSpeedLineEdit = self.findChild(QtWidgets.QLineEdit, 'soundedSpeedLineEdit')
        self.soundedSpeedLineEdit.setText(str(self.soundedSpeedSlider.value()))
        self.soundedSpeedSlider.valueChanged.connect(on_soundedSpeedSlider_valueChanged)
        self.soundedSpeedLineEdit.textEdited.connect(on_soundedSpeedLineEdit_textEdited)

        self.silentSpeedSlider = self.findChild(QtWidgets.QSlider, 'silentSpeedSlider')
        self.silentSpeedLineEdit = self.findChild(QtWidgets.QLineEdit, 'silentSpeedLineEdit')
        self.silentSpeedLineEdit.setText(str(self.silentSpeedSlider.value()))
        self.silentSpeedSlider.valueChanged.connect(on_silentSpeedSlider_valueChanged)
        self.silentSpeedLineEdit.textEdited.connect(on_silentSpeedLineEdit_textEdited)

        self.frameMarginSlider = self.findChild(QtWidgets.QSlider, 'frameMarginSlider')
        self.frameMarginLineEdit = self.findChild(QtWidgets.QLineEdit, 'frameMarginLineEdit')
        self.frameMarginLineEdit.setText(str(self.frameMarginSlider.value()))
        self.frameMarginSlider.valueChanged.connect(on_frameMarginSlider_valueChanged)
        self.frameMarginLineEdit.textEdited.connect(on_frameMarginLineEdit_textEdited)

        self.sampleRateSlider = self.findChild(QtWidgets.QSlider, 'sampleRateSlider')
        self.sampleRateLineEdit = self.findChild(QtWidgets.QLineEdit, 'sampleRateLineEdit')
        self.sampleRateLineEdit.setText(str(self.sampleRateSlider.value()))
        self.sampleRateSlider.valueChanged.connect(on_sampleRateSlider_valueChanged)
        self.sampleRateLineEdit.textEdited.connect(on_sampleRateLineEdit_textEdited)

        self.frameRateSlider = self.findChild(QtWidgets.QSlider, 'frameRateSlider')
        self.frameRateLineEdit = self.findChild(QtWidgets.QLineEdit, 'frameRateLineEdit')
        self.frameRateLineEdit.setText(str(self.frameRateSlider.value()))
        self.frameRateSlider.valueChanged.connect(on_frameRateSlider_valueChanged)
        self.frameRateLineEdit.textEdited.connect(on_frameRateLineEdit_textEdited)

        self.frameQualitySlider = self.findChild(QtWidgets.QSlider, 'frameQualitySlider')
        self.frameQualityLineEdit = self.findChild(QtWidgets.QLineEdit, 'frameQualityLineEdit')
        self.frameQualityLineEdit.setText(str(self.frameQualitySlider.value()))
        self.frameQualitySlider.valueChanged.connect(on_frameQualitySlider_valueChanged)
        self.frameQualityLineEdit.textEdited.connect(on_frameQualityLineEdit_textEdited)

        self.runButton.clicked.connect(on_run_button_clicked)
        self.cancelButton.clicked.connect(on_cancel_button_clicked)
        self.browseButton.clicked.connect(on_browse_button_clicked)
        self.defaultButton.clicked.connect(reset_values)

        self.URLRadio.clicked.connect(lambda:toggleRadio('URL'))
        self.fileRadio.clicked.connect(lambda:toggleRadio('file'))

        
        
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())