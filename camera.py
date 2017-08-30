#!/usr/bin/python
#
# camera.py
#
# Author : Trey Thompson treythompson@gmail.com
# Date   : 29 Aug 2017

# Import required Python libraries
import time
import datetime
import subprocess
import os
import sys
import ftplib
import ftputil

# Define GPIO to use on Pi
UploadToDropBox = 0
BasePicPath = "/home/pi/camera/pics/"
MonthSubFolder = datetime.datetime.now().strftime('%Y%m') + "/"
###############################################################################
# Variables/settings for still images
RaspiStill = "/usr/bin/raspistill"
NumPics = int(sys.argv[1])
CameraTimeDelay = "100"
#StillWidth = "2592" #Full 5MP
#StillHeight = "1944" #Full 5MP
StillWidth = "1296"
StillHeight = "972"

###############################################################################
# Variables/settings for videos
RaspiVid = "/usr/bin/raspivid"
VideoWidth = "1920"
VideoHeight = "1080"
VideoTime = int(sys.argv[2]) * 1000 # in ms
VideoBitRate = "8000000" # in bits/second
###############################################################################
#FTP Variables
FTPFiles = int(sys.argv[3])
FTPHostNameFile = "/home/pi/camera/FTPHostName"
with open(FTPHostNameFile, 'r') as myfile:
	FTPHostName = myfile.read().replace('\n','')
FTPUserNameFile = "/home/pi/camera/FTPUserName"
with open(FTPUserNameFile, 'r') as myfile:
	FTPUserName = myfile.read().replace('\n','')
FTPPasswordFile = "/home/pi/camera/FTPPassword"
with open(FTPPasswordFile, 'r') as myfile:
	FTPPassword = myfile.read().replace('\n','')
FTPBaseDir = "/www/ds/pics/"
###############################################################################
#Youtube Variables
UploadToYoutube = int(sys.argv[4])


# If the local Month directory doesn't exist, create it.
if not os.path.exists(BasePicPath + MonthSubFolder):
	os.makedirs(BasePicPath + MonthSubFolder)

#Open FTP if necessary, create Month directory if necessary.
if FTPFiles == 1:
	ftp = ftputil.FTPHost(FTPHostName,FTPUserName,FTPPassword)
	if not ftp.path.isdir(FTPBaseDir + MonthSubFolder):
		ftp.makedirs(FTPBaseDir + MonthSubFolder)
		
#	ftp.cwd(FTPBaseDir)
#	ftp.mkdir(MonthSubFolder)

PicsTaken = {}
if NumPics > 0:
	for x in range (0, NumPics):
		TimeStamp = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
		PictureFileName = BasePicPath + MonthSubFolder + TimeStamp + ".jpg"
		RaspiStillCommand = RaspiStill + " -t " + CameraTimeDelay + " -w " + StillWidth + " -h " + StillHeight + " -o " + PictureFileName
		print "Executing -> " + RaspiStillCommand
		subprocess.call (RaspiStillCommand, shell=True)
		PicsTaken[x] = PictureFileName
		if FTPFiles == 1:
			ftp.upload(PictureFileName, FTPBaseDir + MonthSubFolder + "/" + TimeStamp + ".jpg")
		time.sleep(1)

if VideoTime > 0:
	VideoTime = str(VideoTime)
	TimeStamp = datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')
	VideoFileName = BasePicPath + MonthSubFolder + TimeStamp + ".264"
	VideoFileNameMP4 = BasePicPath + MonthSubFolder + TimeStamp + ".mp4"
	RaspiVidCommand = RaspiVid + " -w " + VideoWidth + " -h " + VideoHeight + " -b " + VideoBitRate + " -t " + VideoTime + " -o " + VideoFileName
	subprocess.call (RaspiVidCommand, shell=True)
	MP4BoxCommand = "/usr/bin/MP4Box -fps 30 -add " + VideoFileName + " " + VideoFileNameMP4
	subprocess.call (MP4BoxCommand, shell=True)
	os.remove(VideoFileName)
	if FTPFiles == 1:
#		ftp.upload(PictureFileName, FTPBaseDir + MonthSubFolder + "/" + TimeStamp + ".jpg")
		ftp.upload(VideoFileNameMP4, FTPBaseDir + MonthSubFolder + "/" + TimeStamp + ".mp4",)
	time.sleep(1)
	if UploadToYoutube == 1:
		YoutubeCommand = "/usr/local/bin/youtube-upload --title=\"" + TimeStamp + "\" --description=\"Dripping Springs Video\" " + VideoFileNameMP4
		subprocess.call (YoutubeCommand, shell=True)

if FTPFiles == 1:
	ftp.close()

