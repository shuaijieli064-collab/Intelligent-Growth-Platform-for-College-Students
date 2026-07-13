import requests

token = requests.post('http://localhost:8081/api/auth/login', json={'username': 'testuser_full', 'password': '123456'}).json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}
r = requests.get('http://localhost:8081/api/study-records', headers=headers)
data = r.json()
records = data.get('data', [])
print(f'学习记录数量: {len(records)}')
for rec in records:
    date = rec.get('study_date')
    hours = rec.get('study_hours')
    cid = rec.get('course_id')
    print(f'  - {date}: {hours}小时, course_id={cid}')
