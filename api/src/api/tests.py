import requests
from pathlib import Path
import time
import os
from dotenv import load_dotenv
import base64

BASE_DIR = Path(__file__).resolve().parent.parent

# only development

load_dotenv(BASE_DIR.parent / '.env')

# base_url = 'https://api.speaklish.uz'
base_url = 'http://localhost:8000'

url = base_url + "/school/session-create?is_test=true&user_id=6616"

payload = {}
username = os.getenv('DJANGO_SUPERUSER_USERNAME')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
pass_hash = str(base64.b64encode(f'{username}:{password}'.encode('utf-8')), 'utf-8')

headers = {
    'Authorization': 'Basic ' + pass_hash
}

response = requests.request("GET", url, headers=headers, )

if response.status_code == 401:
    print('unauthorized')
    exit(1)

elif response.status_code == 400:
    print(response.json())
    exit(1)

test_session = response.json()

print(test_session['session_id'], 'session_id')
# send part1 answers
url = f"{base_url}/school/part-1-create/"

session_id = test_session.get('session_id')
part1_questions = test_session.get('part1_questions')
base_dir = Path(__file__).resolve().parent.parent.parent / 'media'

for question in part1_questions:
    qs_id = question.get('id')
    audio_file = base_dir / 'tests' / f'audio_part1_{qs_id}.ogg'
    assert audio_file.exists(), audio_file
    files = {'voice_audio': open(audio_file, 'rb')}
    payload = {'question_id': qs_id, 'session_id': session_id}
    response = requests.request("POST", url, headers=headers,
                                data=payload, files=files)
    print('qs_id', qs_id, response.json())

# send part2 answers
url = f"{base_url}/school/part-2-create/"
part2_question = test_session.get('part2_question')
qs_id = part2_question.get('id')

# base_dir = Path(__file__).resolve().parent.parent.parent
audio_file = base_dir / 'tests' / f'part_2_test.ogg'

assert audio_file.exists()
files = {'voice_audio': open(audio_file, 'rb')}
payload = {'question_id': qs_id, 'session_id': session_id}
response = requests.request("POST", url, headers=headers,
                            data=payload, files=files)
print('qs_id', qs_id, response.json())

print('waiting for part3 for 20 seconds...')
time.sleep(20)

print('sending part3 answers...')
# send part3 answers
url = f"{base_url}/school/part-3-create/"
part3_questions = test_session.get('part3_questions')
for question in part3_questions:
    qs_id = question.get('id')
    audio_file = base_dir / 'tests' / f'audio_part3_{qs_id}.ogg'
    assert audio_file.exists()

    files = {'voice_audio': open(audio_file, 'rb')}
    payload = {'question_id': qs_id, 'session_id': session_id}
    response = requests.request("POST", url, headers=headers,
                                data=payload, files=files)
    print('qs_id', qs_id, response.json())
    time.sleep(5)

# get feedback
print('waiting for feedback for 30 seconds...')
time.sleep(30)

url = f"{base_url}/school/session-feedback"
url = url + f'/{session_id}'
response = requests.request("GET", url, headers=headers)
n = 0
while response.status_code != 200:
    time.sleep(5)
    response = requests.request("GET", url, headers=headers)
    print(response.status_code, 'try', n)
    n += 1

print(response.json())
