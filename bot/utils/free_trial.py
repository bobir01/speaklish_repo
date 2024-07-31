from loader import cache, db, config


async def check_free_trial(user_id: int):
    """
    Check if user has free trial
    :param user_id: user id
    :return: True if user has free trial, False otherwise
    """
    if config.mode == 'dev':
        return True
    return await cache.get(f'free_trial:{user_id}') is not None
