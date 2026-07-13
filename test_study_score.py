import requests
import json

BASE = 'http://localhost:8081'

r = requests.post(f'{BASE}/api/auth/login', json={'username': 'testuser_full', 'password': '123456'})
token = r.json()['data']['token']
headers = {'Authorization': f'Bearer {token}'}
print('=== 登录成功 ===\n')

# 测试创建学习记录
print('--- 测试学习记录 ---')
r = requests.post(f'{BASE}/api/study-records', headers=headers, json={
    'study_date': '2026-07-12',
    'study_hours': 3.5,
    'course_id': 1,
    'task_completed': 5,
    'focus_score': 80,
    'notes': '测试学习记录'
})
print(f'创建学习记录: {r.status_code}')
if r.status_code != 200:
    print(r.text)
else:
    print(json.dumps(r.json(), ensure_ascii=False)[:300])

# 查询学习记录
r = requests.get(f'{BASE}/api/study-records', headers=headers)
print(f'\n查询学习记录: {r.status_code}')
data = r.json()
records = data.get('data', [])
print(f'记录数: {len(records)}')
for rec in records[:3]:
    print(f'  - {rec}')

print()
print('--- 测试成绩录入 ---')
# 测试创建/更新成绩
r = requests.post(f'{BASE}/api/scores', headers=headers, json={
    'course_id': 1,
    'usual_score': 85.0,
    'midterm_score': 78.0,
    'final_score': 82.0,
    'has_final_exam': True
})
print(f'创建/更新成绩: {r.status_code}')
if r.status_code != 200:
    print(r.text)
else:
    print(json.dumps(r.json(), ensure_ascii=False)[:300])

# 查询成绩
r = requests.get(f'{BASE}/api/scores', headers=headers)
print(f'\n查询成绩: {r.status_code}')
data = r.json()
scores = data.get('data', [])
print(f'成绩数: {len(scores)}')
for s in scores[:3]:
    usual = s.get('usual_score')
    mid = s.get('midterm_score')
    final = s.get('final_score')
    print(f'  - {s.get("course_name")}: 平时={usual}, 期中={mid}, 期末={final}')
