import pickle

# Load and check the names from the pickle file
with open('data/names.pkl', 'rb') as f:
    names = pickle.load(f)
    
print("Names found in names.pkl:")
print(f"Total entries: {len(names)}")
print(f"Unique names: {set(names)}")
print("\nFirst 10 entries:")
for i, name in enumerate(names[:10]):
    print(f"{i}: {name}")
