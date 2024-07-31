import asyncio
import logging
from loader import config
import aiohttp
import traceback


class WithHttp:

    @staticmethod
    async def get_order_link(user_id: int, quantity: int, price: int = 10_000, n_tries=0) -> str:
        auth = aiohttp.BasicAuth(config.api_username, config.api_password)
        order_link: str = config.payme_speaklish_url+'payme/generate_link/'
        if n_tries > 3:
            raise ValueError('Server is not available')
        try:
            async with aiohttp.ClientSession(auth=auth) as session:
                async with session.post(order_link, data={
                                            'user_id': user_id,
                                            'session_quantity': quantity,
                                            'price': price
                }
                                        ) as resp:
                    data = await resp.json()
                    url = data['url']
                    return url
        except Exception as e:
            logging.error(f'Error while getting order link: {e}')
            logging.error(traceback.format_exc())
            await asyncio.sleep(3)
            return await WithHttp.get_order_link(user_id=user_id, quantity=quantity, price=price, n_tries=n_tries + 1)

    @staticmethod
    async def send_message(self, user_id: int, message: str) -> bool:
        """
        Send message to user
        :param user_id: user int
        :param message: message
        :return: None
        """
        send_message_link: str = f'https://api.telegram.org/bot{config.bot_token}/SendMessage'
        async with aiohttp.ClientSession() as session:
            async with session.post(send_message_link, data={
                'chat_id': user_id,
                'text': message
            }) as resp:
                return resp.status == 200
