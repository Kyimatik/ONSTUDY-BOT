import aiosqlite


# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect('users.db') as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица челленджей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                full_name TEXT,
                contacts TEXT,
                school TEXT,
                username TEXT,
                insta TEXT,
                age INTEGER,
                startdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
            )
        ''')

        await db.commit()



# Функция для получения всех user_id
async def get_all_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT DISTINCT user_id FROM users') as cursor:
            users = await cursor.fetchall()
            return [user[0] for user in users]

# Добавление пользователя
async def add_user(user_id):
    async with aiosqlite.connect('users.db') as db:
        try:
            await db.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False



# Функция для получения всех user_id, участвующих в челлендже
async def get_all_challenge_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT user_id FROM challenges') as cursor:
            users = await cursor.fetchall()
            return [user[0] for user in users]

# Добавление пользователя в челлендж
async def add_challenge_user(user_id, full_name, contacts, school, username ,insta, age):
    async with aiosqlite.connect('users.db') as db:
        try:
            # Проверяем, существует ли уже такой user_id
            cursor = await db.execute('''SELECT user_id FROM challenges WHERE user_id = ?''', (user_id,))
            existing_user = await cursor.fetchone()

            if existing_user:
                # Если такой user_id уже есть, возвращаем False, что значит, что пользователь не был добавлен
                return False

            # Если user_id не найден, добавляем нового пользователя
            await db.execute(''' 
                INSERT INTO challenges (user_id, full_name, contacts, school, username, insta ,age) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                (user_id, full_name, contacts, school, username,insta ,age))
            await db.commit()
            return True
        
        except aiosqlite.IntegrityError:
            # В случае других ошибок, например, если нарушение целостности данных
            return False


# Зареган ли человек ? 
async def is_user_registered(user_id: int) -> bool:
    """ Проверяет, зарегистрирован ли пользователь в базе данных """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT 1 FROM challenges WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone() is not None
    