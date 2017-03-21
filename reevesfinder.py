#!/Users/balysk/Envs/techtalk/bin/python

import os
import cv2
import boto3
import json

rek = boto3.client('rekognition')
polly = boto3.client('polly')

vidcap = cv2.VideoCapture('/Users/balysk/dev/tt/John Wick Chapter 2 (2017 Movie) Official Trailer.mp4')

# Get contents of our canonical image for Keanu Reeves
keanuface = open("keanu.jpg", 'rb').read()

# Video length in microseconds = ( total frames / framerate ) * 1000 
vidlength = vidcap.get(7) / vidcap.get(5) * 1000 
readposition = 1000

while readposition < vidlength:
    
    # Get minutes and seconds into video (for display purposes)
    x = readposition / 1000
    seconds = x % 60
    x /= 60
    minutes = x % 60
    
    vidcap.set(0,readposition)     # cue to position   
    success,image = vidcap.read()
    
    if success:
        framename = "frame"+str(readposition)+".jpg"
        cv2.imwrite("frames/"+framename, image)
        frameblob = open("frames/"+framename, 'rb').read()
        
        # Is Keanu face in the frame?
        try: 
            results = rek.compare_faces(  
            SourceImage={
                'Bytes': keanuface
            },
            TargetImage={
                'Bytes': frameblob
            }
            )
        except Exception as inst:
            inst = None
            
        # Print the result
        if 'FaceMatches' in results and results['FaceMatches']:
            text = "Keanu Reeves FOUND at",str(minutes)+":"+str(seconds).zfill(2)
            print text
            print results['FaceMatches']
            cv2.imshow("frames/"+framename,image)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()
            
            # Say where we found it out loud with Polly
            resp = polly.synthesize_speech(OutputFormat='mp3', Text=str(text), VoiceId='Brian')
            soundfile = open('/tmp/sound.mp3', 'w')
            soundBytes = resp['AudioStream'].read()
            soundfile.write(soundBytes)
            soundfile.close()
            os.system('afplay /tmp/sound.mp3')
            os.remove('/tmp/sound.mp3')           
            
        else:
            print "Keanu Reeves not found at",str(minutes)+":"+str(seconds).zfill(2)
            
            
            
    
    results = [{}]   
    readposition += 1000