import pickle

with open('data/names.pkl', 'rb') as f:
    names = pickle.load(f)

print('Names:', names[:10], '...')
print('Unique names:', set(names))
print('Total:', len(names))

with open('data/faces_data.pkl', 'rb') as f:
    faces = pickle.load(f)

print('Faces shape:', faces.shape)
