import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate("")
firebase_admin.initialize_app(cred, {
    'databaseURL': "",
    'storageBucket': ""

})

folderPath = 'Faces'
PathList = os.listdir(folderPath)
imgList = []
IDs = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    IDs.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(IDs)


def encoder(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


# encoder generation
encodeListKnown = encoder(imgList)
encodeListKnownWithIDs = [encodeListKnown, IDs]
print("Encoding Completed")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIDs, file)
file.close()
