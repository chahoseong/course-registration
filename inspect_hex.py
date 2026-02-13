
import binascii

file_path = "functions/.env"
try:
    with open(file_path, "rb") as f:
        content = f.read()
        print(f"Hex dump: {binascii.hexlify(content)}")
except Exception as e:
    print(f"Error: {e}")
