# TODO List for Face Recognition Attendance System

## Completed Tasks
- [x] Fixed attendance saving to record all detected faces instead of just the last one.
- [x] Updated window title to generic "Face Recognition Attendance System".
- [x] Fixed haarcascade filename.
- [x] Added logic to save multiple attendances when 'o' is pressed.
- [x] Added sample faces for 'alice' and 'bob' to the training data.
- [x] Added real face data for 'charlie' and 'david' using add_faces.py.
- [x] Updated add_faces.py to display the name on each face during collection.
- [x] Verified training data now contains multiple unique names.

## Pending Tasks
- [ ] Test the system with multiple people present to verify correct recognition and saving.
- [ ] If needed, train on real faces for more people using `python add_faces.py [name]`.
- [ ] Check attendance CSVs to ensure correct saving.

## Notes
- Training data now has 162 entries: soumya (20), alice (20), bob (20), charlie (30), david (52).
- The system should now recognize different faces as different names.
- All detected faces in a frame will have their attendance recorded when 'o' is pressed.
- add_faces.py now displays the person's name on each detected face.
