import requests

BASE = 'http://localhost:5000'

# Проверка главной страницы
r = requests.get(f'{BASE}/')
print('Главная:', r.status_code)

# Проверка /info/version/
r = requests.get(f'{BASE}/info/version/')
print('/info/version/:', r.status_code, r.json())

# Проверка /sitepart/colors/rgb/
r = requests.get(f'{BASE}/sitepart/colors/rgb/')
print('/sitepart/colors/rgb/:', r.status_code, r.json())

# Проверка /tours
r = requests.get(f'{BASE}/tours')
print('/tours:', r.status_code, 'записей:', len(r.json()))

# Проверка /tours/stats
r = requests.get(f'{BASE}/tours/stats')
print('/tours/stats:', r.status_code, r.json())

# Проверка сортировки по цене (по убыванию)
r = requests.get(f'{BASE}/tours/sorted?field=price&order=desc')
print('/tours/sorted:', r.status_code)
prices = [t['price'] for t in r.json()]
print('Цены по убыванию:', prices)

# Проверка добавления
new_tour = {
    'name': 'Тур в Тибет',
    'country': 'Китай',
    'duration_days': 14,
    'price': 5000.0,
    'rating': 5.0
}
r = requests.post(f'{BASE}/tours', json=new_tour)
print('POST /tours:', r.status_code, r.json())

# Проверка удаления только что добавленного
if r.status_code == 201:
    new_id = r.json()['id']
    r = requests.delete(f'{BASE}/tours/{new_id}')
    print(f'DELETE /tours/{new_id}:', r.status_code, r.json())