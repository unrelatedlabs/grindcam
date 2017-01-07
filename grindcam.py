import numpy as np
import cv2
import datetime
import sys
import os
import Queue
import threading
import subprocess as sp

 # Find OpenCV version
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

def capture(cam=0,folder='.'):

    cap = cv2.VideoCapture(cam)
    width, height = int(cap.get(3)),int(cap.get(4))
    print width,height

    cap.set(3,width)
    cap.set(4,height)
    cap.set(cv2.cv.CV_CAP_PROP_FPS,24)




    if not os.path.exists(folder):
        print "Folder {} does not exist. Creating...".format(folder)
        os.makedirs(folder)

    filename = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S.mov")
    filename = os.path.join(folder,filename)

    print "Camera:{} > '{}'".format(cam,filename)

    # Define the codec and create VideoWriter object
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fourcc = cv2.cv.CV_FOURCC(*'mp4v')
    #fourcc = cv2.cv.CV_FOURCC('8','B','P','S')

    


    font = cv2.FONT_HERSHEY_SIMPLEX
    timestamp_format = "%Y-%m-%d %H:%M:%S.%f"
    
    rawFrameQueue = Queue.Queue()
    saveFrameQueue = Queue.Queue()
    displayFrameQueue = Queue.Queue()

    class State(object):
        def __init__(self):
            self.running = True
            self.rawFrames = 0
            self.processedFrames = 0
            self.shownFrames = 0
            self.savedFrames = 0
        def __str__(self):
            sb = []
            for key in self.__dict__:
                sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
         
            return ', '.join(sb)
         
        def __repr__(self):
            return self.__str__() 

    state = State()

 

    def processFrame(state):
        while state.running:
            try:
                frame = rawFrameQueue.get(True,1)
                now = datetime.datetime.now()
                cv2.putText(frame,now.strftime(timestamp_format),(10,height-10), font, 1,(255,255,255),2)

                saveFrameQueue.put(frame.copy())
                displayFrameQueue.put(frame.copy())
                state.processedFrames += 1

            except Queue.Empty, e:
                continue

        print "Exiting p"

    def saveFrame(state):
        out = cv2.VideoWriter(filename,fourcc, 20.0, (width,height))

        while state.running:
            try:
                frame = saveFrameQueue.get(True,1)     
                #print frame.shape,len(frame.tostring())
            
                out.write(frame)
                state.savedFrames += 1

            except Queue.Empty:
                continue

            except BaseException, e:
                print e
                print "code",   pipe.returncode
        
    
        out.release()
        print "Exiting s"
        

    def readFrame(state):
        try:
            while state.running and cap.isOpened():
                ret, frame = cap.read()
                if ret==True:
                    rawFrameQueue.put(frame.copy())
                    state.rawFrames +=1 
                    #frame = cv2.flip(frame,0)
                    # write the flipped frame
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                else:
                    break
        except BaseException,e:
            print e

        state.running = False
        print "exiting read"

    readFrameThread = threading.Thread(target=readFrame,args=(state,))
    processFrameThread = threading.Thread(target=processFrame,args=(state,))
    saveFrameThread = threading.Thread(target=saveFrame,args=(state,))


    readFrameThread.start()
    processFrameThread.start()
    saveFrameThread.start()


    cv2.namedWindow("GrindCam",flags=cv2.WINDOW_OPENGL)

    while state.running:
        try:
            frame = displayFrameQueue.get(True,1) 
            
            #clean remaining frames
            while not displayFrameQueue.empty():
                displayFrameQueue.get()

            cv2.imshow('GrindCam',frame)

            state.shownFrames += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                state.running = False
                
        except Queue.Empty, e:
            print "e"
        except KeyboardInterrupt:
            print "Ctrl + C"
            state.running = False
            print state

    readFrameThread.join()
    processFrameThread.join()
    saveFrameThread.join()

    # processFrameThread.stop()
    # saveFrameThread.stop()

    # Release everything if job is finished
    cap.release()
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', nargs='?', default='.', help='output folder')
    parser.add_argument('--camera', nargs=1,  default=[0], type=int, help='camera index 0|1|2')

    args = parser.parse_args()

    capture(args.camera[0],args.folder)

