
import os

file_path = "functions/.env"
try:
    with open(file_path, "rb") as f:
        content = f.read()
        print(f"Content bytes: {content}")
        try:
            decoded = content.decode("utf-8")
            print("Successfully decoded as UTF-8")
        except UnicodeDecodeError:
            print("Failed to decode as UTF-8")
            
        if b'\r\n' in content:
            print("Newlines are CRLF")
        elif b'\n' in content:
            print("Newlines are LF")
except Exception as e:
    print(f"Error reading file: {e}")
