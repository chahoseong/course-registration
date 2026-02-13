
import os
from google.cloud import firestore

# Configuration
os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
project_id = "course-registration-711a4"
target_uid = "u0gP01p3SGmL6cocdN1ROoadH6th"
db_name = "course-registration"

print(f"Connecting to Emulator: {os.environ['FIRESTORE_EMULATOR_HOST']}")
print(f"Project: {project_id}, Database: {db_name}")

db = firestore.Client(project=project_id, database=db_name)

doc_ref = db.collection("users").document(target_uid)
doc = doc_ref.get()

if doc.exists:
    data = doc.to_dict()
    print(f"\n[Before Update] User {target_uid}:")
    print(f"  Role: {data.get('role')}")
    print(f"  Full Data: {data}")
    
    if data.get('role') != 'admin':
        print("\nUpdating role to 'admin'...")
        doc_ref.update({"role": "admin"})
        
        updated_doc = doc_ref.get()
        print(f"[After Update] Role: {updated_doc.to_dict().get('role')}")
    else:
        print("\nUser is already admin.")
else:
    print(f"\nUser {target_uid} NOT FOUND in database '{db_name}'")
    
    # Check default database just in case
    print("\nChecking (default) database...")
    db_default = firestore.Client(project=project_id)
    doc_default = db_default.collection("users").document(target_uid).get()
    
    if doc_default.exists:
        print(f"Found in (default) DB! Role: {doc_default.to_dict().get('role')}")
    else:
        print("Not found in (default) DB either.")
