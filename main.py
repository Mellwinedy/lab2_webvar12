# ============================================================
# Импорт библиотек
# ============================================================
from flask import Flask, jsonify, Blueprint, request
from flasgger import Swagger

# Импорт Blueprint из отдельного модуля
from sitepart.sitepart import sitepart

# ============================================================
# Создание приложения Flask
# ============================================================
app = Flask(__name__)

# Инициализация Swagger для автоматической документации
# template_file можно не указывать — Flasgger использует шаблон по умолчанию
swagger = Swagger(app)

# ============================================================
# Основной Blueprint сайта
# ============================================================
main = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static'
)


# ============================================================
# Маршрут /info/<about>/
# ============================================================
@main.route('/info/<about>/')
def info(about):
    """
    Example endpoint returning about info
    This is using docstrings for specifications.
    ---
    parameters:
      - name: about
        in: path
        type: string
        enum: ['all', 'version', 'author', 'year']
        required: true
        default: all
    definitions:
      About:
        type: string
    responses:
      200:
        description: A string
        schema:
          $ref: '#/definitions/About'
        examples:
          version: '1.0'
    """
    all_info = {
        'all': 'main_author 1.0 2020',
        'version': '1.0',
        'author': 'main_author',
        'year': '2020'
    }
    if about not in all_info:
        return jsonify({'error': f'Неизвестный параметр: {about}'}), 404
    return jsonify({about: all_info[about]}), 200


# ============================================================
# Swagger-модель для туристической поездки
# ============================================================
tour_model = {
    'type': 'object',
    'properties': {
        'id': {'type': 'integer', 'description': 'Идентификатор'},
        'name': {'type': 'string', 'description': 'Название тура'},
        'country': {'type': 'string', 'description': 'Страна'},
        'duration_days': {'type': 'integer', 'description': 'Длительность (дней)'},
        'price': {'type': 'number', 'format': 'float', 'description': 'Стоимость'},
        'rating': {'type': 'number', 'format': 'float', 'description': 'Рейтинг'}
    },
    'required': ['name', 'country', 'duration_days', 'price', 'rating']
}


# ============================================================
# Модель данных: Туристические поездки
# ============================================================
tours = [
    {'id': 1, 'name': 'Экскурсия по Парижу', 'country': 'Франция',
     'duration_days': 5, 'price': 1200.0, 'rating': 4.8},
    {'id': 2, 'name': 'Отдых на Бали', 'country': 'Индонезия',
     'duration_days': 12, 'price': 2500.0, 'rating': 4.9},
    {'id': 3, 'name': 'Тур по Золотому кольцу', 'country': 'Россия',
     'duration_days': 3, 'price': 450.0, 'rating': 4.5},
    {'id': 4, 'name': 'Сафари в Кении', 'country': 'Кения',
     'duration_days': 8, 'price': 3200.0, 'rating': 4.7},
    {'id': 5, 'name': 'Отдых в Сочи', 'country': 'Россия',
     'duration_days': 7, 'price': 600.0, 'rating': 4.2},
]

next_id = 6


# ============================================================
# API: Туристические поездки
# ============================================================

# ---------- GET /tours — все записи ----------
@app.route('/tours', methods=['GET'])
def get_tours():
    """
    Получить список всех туров
    ---
    tags:
      - Туры
    responses:
      200:
        description: Список туров
        schema:
          type: array
          items:
            $ref: '#/definitions/Tour'
    definitions:
      Tour:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          country:
            type: string
          duration_days:
            type: integer
          price:
            type: number
          rating:
            type: number
    """
    return jsonify(tours), 200


# ---------- GET /tours/stats — статистика ----------
# ВАЖНО: этот маршрут объявлен ДО /tours/<id>, иначе Flask попытается
# интерпретировать "stats" как integer ID.
@app.route('/tours/stats', methods=['GET'])
def tours_stats():
    """
    Статистика по числовым полям туров
    ---
    tags:
      - Туры
    responses:
      200:
        description: Среднее, максимальное и минимальное значения
    """
    if not tours:
        return jsonify({'error': 'Нет данных'}), 404

    prices = [t['price'] for t in tours]
    durations = [t['duration_days'] for t in tours]
    ratings = [t['rating'] for t in tours]

    stats = {
        'price': {
            'min': min(prices),
            'max': max(prices),
            'avg': round(sum(prices) / len(prices), 2)
        },
        'duration_days': {
            'min': min(durations),
            'max': max(durations),
            'avg': round(sum(durations) / len(durations), 2)
        },
        'rating': {
            'min': min(ratings),
            'max': max(ratings),
            'avg': round(sum(ratings) / len(ratings), 2)
        }
    }
    return jsonify(stats), 200


# ---------- GET /tours/sorted — сортировка ----------
@app.route('/tours/sorted', methods=['GET'])
def sorted_tours():
    """
    Сортировка туров по полю
    ---
    tags:
      - Туры
    parameters:
      - name: field
        in: query
        type: string
        enum: ['id', 'name', 'country', 'duration_days', 'price', 'rating']
        required: false
        default: id
        description: Поле для сортировки
      - name: order
        in: query
        type: string
        enum: ['asc', 'desc']
        required: false
        default: asc
        description: Направление сортировки
    responses:
      200:
        description: Отсортированный список
    """
    field = request.args.get('field', 'id')
    order = request.args.get('order', 'asc')

    valid_fields = ['id', 'name', 'country', 'duration_days', 'price', 'rating']
    if field not in valid_fields:
        return jsonify({'error': f'Поле {field} не поддерживается'}), 400
    if order not in ('asc', 'desc'):
        return jsonify({'error': 'order должен быть asc или desc'}), 400

    reverse = (order == 'desc')
    sorted_list = sorted(tours, key=lambda t: t[field], reverse=reverse)
    return jsonify(sorted_list), 200


# ---------- GET /tours/<id> — одна запись ----------
@app.route('/tours/<int:tour_id>', methods=['GET'])
def get_tour(tour_id):
    """
    Получить тур по ID
    ---
    tags:
      - Туры
    parameters:
      - name: tour_id
        in: path
        type: integer
        required: true
        description: Идентификатор тура
    responses:
      200:
        description: Данные тура
      404:
        description: Тур не найден
    """
    tour = next((t for t in tours if t['id'] == tour_id), None)
    if tour is None:
        return jsonify({'error': 'Тур не найден'}), 404
    return jsonify(tour), 200


# ---------- POST /tours — добавить запись ----------
@app.route('/tours', methods=['POST'])
def add_tour():
    """
    Добавить новый тур
    ---
    tags:
      - Туры
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/Tour'
    responses:
      201:
        description: Тур создан
      400:
        description: Ошибка валидации
    """
    global next_id
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Нет данных или неверный JSON'}), 400

    required = ['name', 'country', 'duration_days', 'price', 'rating']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Поле {field} обязательно'}), 400

    try:
        new_tour = {
            'id': next_id,
            'name': str(data['name']),
            'country': str(data['country']),
            'duration_days': int(data['duration_days']),
            'price': float(data['price']),
            'rating': float(data['rating'])
        }
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Ошибка типов: {e}'}), 400

    tours.append(new_tour)
    next_id += 1
    return jsonify(new_tour), 201


# ---------- PUT /tours/<id> — обновить запись ----------
@app.route('/tours/<int:tour_id>', methods=['PUT'])
def update_tour(tour_id):
    """
    Обновить тур по ID
    ---
    tags:
      - Туры
    parameters:
      - name: tour_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/Tour'
    responses:
      200:
        description: Тур обновлён
      404:
        description: Тур не найден
    """
    tour = next((t for t in tours if t['id'] == tour_id), None)
    if tour is None:
        return jsonify({'error': 'Тур не найден'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Нет данных'}), 400

    for field in ['name', 'country', 'duration_days', 'price', 'rating']:
        if field in data:
            tour[field] = data[field]
    return jsonify(tour), 200


# ---------- DELETE /tours/<id> — удалить запись ----------
@app.route('/tours/<int:tour_id>', methods=['DELETE'])
def delete_tour(tour_id):
    """
    Удалить тур по ID
    ---
    tags:
      - Туры
    parameters:
      - name: tour_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Тур удалён
      404:
        description: Тур не найден
    """
    global tours
    tour = next((t for t in tours if t['id'] == tour_id), None)
    if tour is None:
        return jsonify({'error': 'Тур не найден'}), 404
    tours = [t for t in tours if t['id'] != tour_id]
    return jsonify({'message': 'Тур удалён'}), 200


# ============================================================
# Регистрация Blueprint
# ============================================================
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(sitepart, url_prefix='/sitepart')


# ============================================================
# Запуск
# ============================================================
if __name__ == "__main__":
    app.run(debug=True)