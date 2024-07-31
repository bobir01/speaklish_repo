from __future__ import annotations

import logging

import asyncpg
from asyncpg import Connection, Record
from asyncpg.pool import Pool
from schemas import User, Session, Feedback

from config.config import Config
class Database:
    def __init__(self, url: str):
        self.pool: Pool | None = None
        self.url = url

    async def create(self):
        self.pool = await asyncpg.create_pool(
            dsn=self.url,

        )

    async def execute(self, command: str, *args: object,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ) -> object | Record | list[Record] | None:
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result


    async def user_table_migrate(self):
        """check if table exists with column referal text if not add it with default value None"""
        col_check = """SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'referral'"""
        col_check_result = await self.execute(col_check, fetchval=True)
        if col_check_result is None:
            col_add = """ALTER TABLE users ADD COLUMN referral varchar(100) DEFAULT NULL"""
            await self.execute(col_add, execute=True)
            logging.info('referral column added to users table')

    async def insert_user(self, user: User):

        try:
            command = """INSERT INTO users (fullname, username, user_id, referral) VALUES ($1, $2, $3, $4) returning *"""
            result = await self.execute(command, user.fullname, user.username, user.user_id, user.referral,
                                        fetchrow=True)
            user.id = result['id']
            return user
        except asyncpg.exceptions.UniqueViolationError:
            return None

    async def get_user(self, user_id: int) -> User | None:
        command = """SELECT id, fullname, username, user_id, joined_at, is_active, referral FROM users WHERE user_id = $1"""
        result: Record = await self.execute(command, user_id, fetchrow=True)
        if result:
            return User(**result)

    async def update_phone_number(self, user_id: int, phone: str):
        command = """UPDATE users SET phone = $1 WHERE user_id = $2"""
        await self.execute(command, phone, user_id, execute=True)

    async def get_all_users(self) -> list[User]:
        command = """SELECT id, fullname, username, user_id, joined_at, is_active, referral FROM users"""
        result = await self.execute(command, fetch=True)
        return [User(**res) for res in result]

    async def get_all_users(self) -> list[User]:
        command = """SELECT id, fullname, username, user_id, joined_at, is_active, referral FROM users where is_active = true"""
        result = await self.execute(command, fetch=True)
        return [User(**res) for res in result]

    async def delete_user(self, user_id: int):
        command = """DELETE FROM users WHERE user_id = $1"""
        await self.execute(command, user_id, execute=True)

    async def update_user_status(self, user_id: int):
        """toggle user status"""
        command = """UPDATE users SET is_active = not is_active WHERE user_id = $1"""
        await self.execute(command, user_id, execute=True)

    # session functions
    async def insert_session(self, session: Session):
        command = """INSERT INTO sessions 
        (user_id, session_id, total_audio_length, used_tokens, 
        final_prompt, model_answer, stop_reason, finish_state, finished_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"""
        await self.execute(command, session.user_id, session.session_id, session.total_audio_length,
                           session.used_tokens,
                           session.final_prompt, session.model_answer, session.stop_reason,
                           session.finish_state, session.finished_at,
                           execute=True)

    async def update_session(self, session: Session) -> Session:
        command = """UPDATE sessions SET total_audio_length = $1, 
        used_tokens = $2, final_prompt = $3, 
        model_answer = $4, stop_reason = $5, 
        finish_state = $6, finished_at = $7 
        WHERE session_id = $8
        RETURNING *"""
        result: Record = await self.execute(command,
                                            session.total_audio_length,
                                            session.used_tokens, session.final_prompt,
                                            session.model_answer, session.stop_reason,
                                            session.finish_state, session.finished_at,
                                            session.session_id,
                                            fetchrow=True)
        if result:
            return Session(**result)

    async def get_session(self, session_id: str) -> Session | None:
        command = """SELECT * FROM sessions WHERE session_id = $1"""
        result: Record = await self.execute(command, session_id, fetchrow=True)
        if result:
            return Session(**result)

    # feedback functions
    async def insert_feedback(self, feedback: Feedback):
        command = """INSERT INTO feedbacks 
        (user_id, session_id, user_feedback) VALUES ($1, $2, $3) returning id"""
        result = await self.execute(command, feedback.user_id, feedback.session_id,
                                    feedback.user_feedback, fetchval=True)
        feedback.id = result
        return feedback

    async def get_feedback(self, session_id: str) -> Feedback | None:
        command = """SELECT * FROM feedbacks WHERE session_id = $1"""
        result: Record = await self.execute(command, session_id, fetchrow=True)
        if result:
            return Feedback(**result)

    async def update_feedback(self, feedback: Feedback) -> Feedback:
        """Update feedback text by id
        :param feedback: Feedback object
        :return: Feedback
        """
        if not feedback.id:
            raise ValueError("Feedback id is not set")
        command = """UPDATE feedbacks SET user_feedback = $1 WHERE id = $2 RETURNING *"""
        result: Record = await self.execute(command, feedback.user_feedback, feedback.id, fetchrow=True)
        return Feedback(**result)



    async def get_part1_questions(self):
        if Config.mode == 'dev':
            command = """SELECT row_number() over (), t.* FROM part1_questions t where id = 16"""
        else:
            command = """SELECT row_number() over (), t.* FROM part1_questions t where id = (select floor(1+max(id)*random())::int from part1_questions)"""
        result = await self.execute(command, fetch=True)
        return [dict(**res) for res in result]

    async def get_part2_questions(self):
        if Config.mode == 'dev':
            command = """SELECT t.* FROM part2_questions t where id = 3"""
        else:
            command = """SELECT t.* FROM part2_questions t where id = (select floor(1+max(id)*random())::int from part2_questions)"""
        result = await self.execute(command, fetch=True)
        return [dict(**res) for res in result]

    async def get_part3_questions(self, part2_id: int):
        if Config.mode == 'dev':
            command = """SELECT row_number() over (), t.* FROM part3_questions t where part2_id = 3"""
        else:
            command = """SELECT row_number() over (), t.* FROM part3_questions t where part2_id = $1 """
        result = await self.execute(command, part2_id, fetch=True)
        return [dict(**res) for res in result]
