import requests
BASE = 'http://localhost:8081'
r = requests.post(f'{BASE}/api/auth/login', json={'username': 'testuser_full', 'password': '123456'})
token = r.json()['data']['token']
h = {'Authorization': f'Bearer {token}'}

r1 = requests.get(f'{BASE}/api/courses', headers=h)
courses = r1.json()['data']
print(f'courses: {len(courses)}')
for c in courses[:5]:
    print(f'  {c["course_id"]}: {c["course_name"]}')

r2 = requests.get(f'{BASE}/api/scores', headers=h)
scores = r2.json()['data']
print(f'\nscores: {len(scores)}')
for s in scores[:5]:
    usual = s.get('usual_score')
    mid = s.get('midterm_score')
    final = s.get('final_score')
    print(f'  {s["course_name"]}: 平时={usual}, 期中={mid}, 期末={final}')
