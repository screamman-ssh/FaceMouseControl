import cv2
import mediapipe as mp
import numpy as np
import autopy
from os import system,name
import time
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# def clear():
#     if name == 'nt':
#         _ = system('cls')

w_cam, h_cam = 640,440
frame_reduc_x, frame_reduc_y = 150,100
w_screen, h_screen = autopy.screen.size()
cap = cv2.VideoCapture(0)
cap.set(3, w_cam)
cap.set(4, h_cam)

prevX, prevY = 0,0
curX, curY = 0,0

activate = 1

with mp_face_mesh.FaceMesh(min_detection_confidence=0.5,min_tracking_confidence=0.5) as face_mesh:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = face_mesh.process(image)

    # Draw the face mesh annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_face_landmarks:
      mouth_coord = []
      for face_landmarks in results.multi_face_landmarks:
        for id,lm in enumerate(face_landmarks.landmark):
          h,w,c = image.shape
          x,y = int(lm.x*w), int(lm.y*h)
          if id == 1:
            cv2.circle(image,(x,y),2,(0,0,100),-1)
            #convert coordinate and draw reducing frame
            cv2.rectangle(image, (frame_reduc_x,frame_reduc_y+100),(w_cam - frame_reduc_x, h_cam - frame_reduc_y+50), (255,0,0),1)
            x_scr = np.interp(x ,(frame_reduc_x ,w_cam - frame_reduc_x),(0 ,w_screen))
            y_scr = np.interp(y ,(frame_reduc_y+100,h_cam - frame_reduc_y+50),(0, h_screen))
            if activate == 1:
              status = "Activate"
              #reduce shaking mouse
              smooth = 8 #increase th value more smooth but decrease speed
              curX = prevX + (x_scr - prevX) / smooth
              curY = prevY + (y_scr - prevY) / smooth
              #move mouse
              autopy.mouse.move(curX, curY)
              prevX, prevY = curX, curY

          # get mouth (upper and lower lib) position
          if id == 13 or id == 15:
            mouth_coord.append(y)
        # mouth clicked when mouth is open
        if activate == 1:                
          if (mouth_coord[1] - mouth_coord[0]) >= 15:
            cv2.putText(image,"Clicked",(250,150),cv2.FONT_HERSHEY_PLAIN,2,(255,0,0),5)
            autopy.mouse.click(delay = 0.5)
          
      cv2.putText(image,F"Mode : {status} (spacebar to switch)",(10,25),cv2.FONT_HERSHEY_COMPLEX,1,(0,200,20),3)
      if activate == 1:
        cv2.putText(image,"Open your mouth to clicked.",(10,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,20,200),3)
      cv2.imshow('Nose Control', image)
      # clear()
      if cv2.waitKey(5) & 0xFF == 27:
        break
      elif cv2.waitKey(1) & 0xFF == 32:
        # switch between 1 and -1
        activate *= -1
        status = "Deactivate"
      
cap.release()
