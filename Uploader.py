import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("")
firebase_admin.initialize_app(cred, {
    'databaseURL': ""
})

ref = db.reference('Attendees')

data = {
    "Adam":
        {
            "ID": "85434343",
            "Attended": 0,
            "Name": "Adam Valli",
            "Age": 21,
            "Last_attendance": "2010-1-12 00:50:20"
        },
    "Kat":
        {
            "ID": "423423432",
            "Attended": 0,
            "Name": "Kat",
            "Age": 53,
            "Last_attendance": "2010-1-12 00:50:20"
        }
}

for key, value in data.items():
    ref.child(key).set(value)
