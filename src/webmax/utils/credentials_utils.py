import os
import json

CREDENTIALS_PATH = 'credentials.json'

if not os.path.exists(CREDENTIALS_PATH):
    with open(CREDENTIALS_PATH, 'w') as file:
        file.write('{}')

def read():
    with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as file:
        return json.loads(file.read())

def save(credentials: dict):
    with open(CREDENTIALS_PATH, 'w', encoding='utf-8') as file:
        file.write(json.dumps(credentials, ensure_ascii=False, indent=4))

def clear():
    with open(CREDENTIALS_PATH, 'w', encoding='utf-8') as file:
        file.write(json.dumps({}, ensure_ascii=False, indent=4))