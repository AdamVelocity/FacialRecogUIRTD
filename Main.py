import os
import pickle
import face_recognition
import numpy as np
from datetime import datetime

import cv2

from firebase_admin import storage
from firebase_admin import db


bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/Background.png')

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))

file = open('EncodeFile.p', 'rb')
encodeListKnownWithIDs = pickle.load(file)
file.close()
encodeListKnown, IDs = encodeListKnownWithIDs
print(IDs)
counter = 0
modetype = 0
i = -1
imgattn = []
while True:
    success, img = cap.read()

    imgsmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgsmall = cv2.cvtColor(imgsmall, cv2.COLOR_BGR2RGB)

    currentframe = face_recognition.face_locations(imgsmall)
    encodecurrentframe = face_recognition.face_encodings(imgsmall, currentframe)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

    for encodeFace, faceLoc in zip(encodecurrentframe, currentframe):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)
        print(faceDis)

        if matches[matchIndex]:
            print(IDs[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            # cv2.rectangle(img, (x1, y1 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, IDs[matchIndex], (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
            name = IDs[matchIndex]
            if counter == 0:
                counter = 1
                modetype = 1
        else:
            counter = 0
            modetype = 4
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]
            while counter < 50:
                modetype = 0
                counter += 1
            counter = 0
    if counter != 0:
        if counter == 1:
            Info = db.reference(f'Attendees/{name}').get()
            print(Info)
            blob = bucket.get_blob(f'Faces/{name}.jpg')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgattn = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
            datetimeObject = datetime.strptime(Info['Last_attendance'], "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
            print(secondsElapsed)
            if secondsElapsed > 30:
                ref = db.reference(f'Attendees/{name}')
                Info['Attended'] += 1
                ref.child('Attended').set(Info['Attended'])
                ref.child('Last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                modetype = 3
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]
                modetype = 0
                counter = 0

        if modetype != 3 or 4:
            if 0 < counter < 151:
                modetype = 1
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]
                cv2.putText(imgBackground, str(Info["Name"]), (808, 600), cv2.FONT_HERSHEY_DUPLEX, 0.8, (100, 100, 100),
                            1)
                cv2.putText(imgBackground, str(Info["ID"]), (808, 650), cv2.FONT_HERSHEY_DUPLEX, 0.8, (100, 100, 100),
                            1)
                imgBackground[175:175 + 300, 909:909 + 300] = imgattn
                counter += 1
                print(counter)
            if 100 < counter < 150:
                modetype = 2
                imgBackground[162:162 + 480, 55:55 + 640] = img
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]

            if counter >= 150:
                counter = 0
                modetype = 0
                Info = []
                imgattn = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]
                imgBackground[162:162 + 480, 55:55 + 640] = img
        else:
            count = 0
            modetype = 0
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modetype]
    cv2.imshow("facerecog", imgBackground)
    cv2.waitKey(1)
