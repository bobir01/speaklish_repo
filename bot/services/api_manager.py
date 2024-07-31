import asyncio

import aiohttp

import logging


from config.config import Config

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)


class SpeaklishAPI:

    def __init__(self):
        self.base_url = "https://api.speaklish.uz"
        self._session = aiohttp.ClientSession()
        self.auth = aiohttp.BasicAuth(Config.api_username, Config.api_password)

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = await self.get_new_session()

        if not self._session.loop.is_running():  # NOQA
            # Hate `aiohttp` devs because it juggles event-loops and breaks already opened session
            # So... when we detect a broken session need to fix it by re-creating it
            # @asvetlov, if you read this, please no more juggle event-loop inside aiohttp, it breaks the brain.
            await self._session.close()
            self._session = await self.get_new_session()

        return self._session

    async def get_new_session(self):
        return aiohttp.ClientSession()

    async def close(self):
        await self._session.close()

    @property
    async def session(self):
        return await self._get_session()

    async def create_session(self, user_id: int, is_test=False, referral_code=None):
        url = f'{self.base_url}/school/session-create?user_id={user_id}'
        if referral_code:
            url += f'&referral_code={referral_code}'
        if Config.mode == 'dev' or is_test:
            url += '&is_test=true'
        session = await self._get_session()
        async with session.get(url, auth=self.auth) as res:
            logger.info(f"resp : {await res.text()}")
            data = await res.json()
            logger.info(f"Session created for user {user_id}, id: {data.get('session_id')}")
            return data

    async def part1_create(self, session_id: int, question_id: int, voice: bytes):
        url = f'{self.base_url}/school/part-1-create/'
        data = aiohttp.FormData()
        data.add_field('session_id', value=str(session_id))
        data.add_field('question_id', value=str(question_id))
        file_session_name = f'voice_{session_id}_{question_id}.ogg'
        data.add_field('voice_audio', value=voice, filename=file_session_name, content_type='audio/ogg')
        session = await self._get_session()
        async with session.post(url, data=data, auth=self.auth) as res:
            data = await res.json()
            logger.info(f"Part 1 created for session {session_id}, question {question_id}")
            return data

    async def part2_create(self, session_id: int, question_id: int, voice: bytes):
        url = f'{self.base_url}/school/part-2-create/'
        data = aiohttp.FormData()
        data.add_field('session_id', value=str(session_id))
        data.add_field('question_id', value=str(question_id))
        file_session_name = f'voice_{session_id}_{question_id}.ogg'
        data.add_field('voice_audio', value=voice, filename=file_session_name, content_type='audio/ogg')
        session = await self._get_session()

        async with session.post(url, data=data, auth=self.auth) as res:
            data = await res.json()
            logger.info(f"Part 2 created for session {session_id}, question {question_id}")
            return data

    async def part3_create(self, session_id: int, question_id: int, voice: bytes):
        url = f'{self.base_url}/school/part-3-create/'
        data = aiohttp.FormData()
        data.add_field('session_id', value=str(session_id))
        data.add_field('question_id', value=str(question_id))
        file_session_name = f'voice_{session_id}_{question_id}.ogg'
        data.add_field('voice_audio', value=voice, filename=file_session_name, content_type='audio/ogg')
        session = await self._get_session()

        async with session.post(url, data=data, auth=self.auth) as res:
            data = await res.json()
            logger.info(
                f"Part 3 created for session {session_id}, question {question_id}, id: {data.get('part_id')}")
            return data

    async def session_feedback(self, session_id: int):
        url = f'{self.base_url}/school/session-feedback/{session_id}'
        session = await self._get_session()
        async with session.get(url, auth=self.auth) as res:
            data = await res.json()
            logger.info(f"Got session {session_id}")
            return data

    async def wait_for_session(self, session_id: int):
        finished = False
        cycle_cnt = 0
        data = None
        while not finished and cycle_cnt < 10:
            data = await self.session_feedback(session_id)
            print(data)
            if data.get('result') is not None:
                finished = True
                break
            await asyncio.sleep(30)
            cycle_cnt += 1
        if not finished:
            logger.error(f"Session {session_id} not finished, some error happened, pls try again")
            raise Exception(f"Session {session_id} not finished, some error happened, pls try again")
        return data
