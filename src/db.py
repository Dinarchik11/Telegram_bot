import aiosqlite
from datetime import date


class Database:
    def __init__(self, db_path) -> None:
        self._db_path = db_path

    async def _get_connection(self):
        return await aiosqlite.connect(self._db_path)

    async def _execute_command(self, command, fetch=False, commit=False):
        db_conn = await self._get_connection()
        cursor = await db_conn.execute(command)
        rows = None

        if fetch:
            rows = await cursor.fetchall()
            await cursor.close()

        if commit:
            await db_conn.commit()

        return rows

    async def init_tables(self):
        await self._execute_command(
            """
            CREATE TABLE IF NOT EXISTS words (
                word TEXT,
                translation TEXT,
                user_id INTEGER
            )
            """
        )

        await self._execute_command(
            """
            CREATE TABLE IF NOT EXISTS lessons (
                date TEXT,
                topics TEXT,
                difficulty INTEGER,
                user_id INTEGER
            )
            """
        )

        await self._execute_command(
            """
            CREATE TABLE IF NOT EXISTS materials (
                name TEXT,
                link TEXT,
                mark INTEGER,
                user_id INTEGER
            )
            """
        )

    async def insert_word(self, word: str, translation: str, user_id: int):
        await self._execute_command(f"INSERT INTO words (word, translation, user_id) VALUES ('{word}', '{translation}', {user_id})",
                                    commit=True)

    async def insert_lesson(self, lesson_date: date, topics: str, difficulty: str, user_id: int):
        await self._execute_command(f"""
                            INSERT INTO lessons (date, topics, difficulty, user_id) 
                            VALUES ('{lesson_date.strftime("%d.%m.%Y")}', '{topics}', {difficulty}, {user_id})""",
                                    commit=True)

    async def insert_material(self, name: str, link: str | None, mark: int, user_id: int):
        await self._execute_command(f"""
                            INSERT INTO materials (name, link, mark, user_id) 
                            VALUES ('{name}', '{link}', {mark}, {user_id})""",
                                    commit=True)

    async def get_words(self, user_id: int):
        return await self._execute_command(f"SELECT word, translation FROM words WHERE user_id = {user_id}", fetch=True)

    async def get_lessons(self, user_id: int):
        return await self._execute_command(f"SELECT date, topics, difficulty FROM lessons WHERE user_id = {user_id}", fetch=True)

    async def get_materials(self, user_id: int):
        return await self._execute_command(f"SELECT name, link, mark FROM materials WHERE user_id = {user_id}", fetch=True)

    async def delete_words(self, user_id: int):
        await self._execute_command(f"""
                            DELETE FROM words 
                            WHERE user_id='{user_id}'""",
                                    commit=True)

    async def delete_lessons(self, user_id: int):
        await self._execute_command(f"""
                            DELETE FROM lessons 
                            WHERE user_id='{user_id}'""",
                                    commit=True)

    async def delete_materials(self, user_id: int):
        await self._execute_command(f"""
                            DELETE FROM materials 
                            WHERE 
                                user_id='{user_id}'""",
                                    commit=True)
