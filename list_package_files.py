
import os
import firebase_functions

package_dir = os.path.dirname(firebase_functions.__file__)
print(f"Package dir: {package_dir}")

for root, dirs, files in os.walk(package_dir):
    for file in files:
        if file.endswith(".py"):
            print(os.path.relpath(os.path.join(root, file), package_dir))
