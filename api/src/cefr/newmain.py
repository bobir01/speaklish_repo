"""
CEFR Level API Service Documentation

This service provides an API to determine the CEFR level of English words.
It fetches the CEFR levels from the Cambridge Dictionary and stores them in a SQLite database for quick retrieval.
The service includes rate limiting and caching to ensure efficient operation.

Dependencies:
- FastAPI
- aiosqlite
- requests
- BeautifulSoup
- nltk
- uvicorn
- ratelimit
- asyncio
- json
-async_lru


Authors: Firdavs Yakubov
Version: July 17, 2024
"""
import fastapi
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import aiosqlite
import httpx
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import asyncio
# from ratelimit import limits
import json
from async_lru import alru_cache

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

app = FastAPI()
lemmatizer = WordNetLemmatizer()

DATABASE = 'word_list_cefr.db'
rateLimit = 10
IRREGULAR_VERBS_FILE = 'irregular.verbs.build.json'
irregular_verbs = {}


class WordRequest(BaseModel):
    """
    Represents a request containing a word to fetch or add its CEFR level.

    Attribute word: The word to process.
    Invariant: word is a non-empty string.     
    """
    word: str

class BatchRequest(BaseModel):
    """
    Represents a request containing a text to fetch or add its CEFR level.

    Attribute txt: The text to process.
    Invariant: txt is a non-empty string.
    """
    txt: str



async def init_db():
    """
    Initializes the SQLite database and creates the `words` table if it does not exist.
    """
    async with aiosqlite.connect(DATABASE) as conn:
        await conn.execute('''CREATE TABLE IF NOT EXISTS words (
                                word TEXT PRIMARY KEY, level TEXT)''')
        await conn.commit()


async def load_irregular_verbs():
    """
    Loads the irregular verbs from a JSON file into a dictionary.
    """
    global irregular_verbs
    with open(IRREGULAR_VERBS_FILE, 'r') as file:
        irregular_verbs = json.load(file)


async def save_cefr_level_to_db(word, cefr_level):
    """
    Saves a word and its CEFR level to the database.

    Parameter word: The word to save.
    Invariant: word is a non-empty string.

    Parameter cefr_level: The CEFR level of the word.
    Invariant: cefr_level is a valid CEFR level string.
    """
    async with aiosqlite.connect(DATABASE) as conn:
        await conn.execute('INSERT OR REPLACE INTO words (word, cefr_level) VALUES (?, ?)', (word, cefr_level))
        await conn.commit()

@alru_cache(maxsize=1000)
async def get_cefr_level_from_db(word: str):
    async with aiosqlite.connect(DATABASE) as conn:
        cursor = await conn.execute('SELECT level FROM words WHERE word = ?', (word,))
        result = await cursor.fetchone()
        return result[0] if result else None


# @limits(calls=rateLimit, period=1)
@alru_cache(maxsize=1000)
async def parse_cefr_level(word, retries=3):
    """
    Fetches the CEFR level of a word from the Cambridge Dictionary. Applies rate limiting and caching.

    Parameter word: The word to fetch the CEFR level for.
    Invariant: word is a non-empty string.

    Parameter retries: Number of retries in case of a request failure (default is 3).
    Invariant: retries is a non-negative integer.

    Returns: The CEFR level if found, otherwise None.
    """

    url = f"https://dictionary.cambridge.org/dictionary/english/{word}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                response = await client.get(url, headers=headers, timeout=10, follow_redirects=True)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'lxml')

                span = soup.find('span', class_="epp-xref")
                if span:
                    cefr_level = span.get_text().strip()
                    if cefr_level:
                        return cefr_level.upper()
                print(f"No CEFR level found for word: {word}")
                return None
            except httpx.RequestError as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)
    return None



async def lemmatize_word(word: str):
    """
    Lemmatizes a given word using the NLTK library, including handling irregular verbs.

    Parameter word: The word to lemmatize.
    Invariant: word is a non-empty string.

    Returns: The lemmatized form of the word.
    """
    tokens = nltk.word_tokenize(word)
    pos_tags = nltk.pos_tag(tokens)
    lemmatized_words = []
    for token, tag in pos_tags:
        pos = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(token, pos)
        # for infinitive, forms in irregular_verbs.items():
        #     if lemma in forms[0]["2"] or lemma in forms[0]["3"]:
        #         lemma = infinitive
        #         break
        lemmatized_words.append(lemma)
    return ' '.join(lemmatized_words)


def get_wordnet_pos(tag: str):
    """
    Maps Part of Speach tags to the format accepted by the WordNet lemmatizer.

    Parameter tag: The POS tag.
    Invariant: tag is a string.

    Returns:
        The mapped POS tag.
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN





async def get_word_level(word:str):
    word = word.lower()
    lemmatized_word = await lemmatize_word(word)

    cefr_level = await get_cefr_level_from_db(lemmatized_word)
    if cefr_level:
        return {"word": word, "cefr_level": cefr_level}






@app.post("/api/cefr-level")
async def get_cefr_level(word_request: WordRequest):
    """
    Fetches the CEFR level of a given word. If the word is not present in the
    database, it fetches the CEFR level from the Cambridge Dictionary, saves it to
    the database, and then returns it.
    """
    word = word_request.word.lower()
    lemmatized_word = await lemmatize_word(word)

    cefr_level = await get_cefr_level_from_db(lemmatized_word)
    if not cefr_level:
        cefr_level = await parse_cefr_level(lemmatized_word)
        if cefr_level:
            await save_cefr_level_to_db(lemmatized_word, cefr_level)
        else:
            raise HTTPException(status_code=404, detail="CEFR level not found")

    return {"word": word, "cefr_level": cefr_level}


@app.post("/api/batch-process")
async def batch_process(batch_request: BatchRequest):

    data = batch_request.txt
    txt_list = set(data.split())
    levels = []
    for word in txt_list:
        word = word.strip('.').strip(',').strip('!').strip('?')
        res = await get_word_level(word)
        if res:
            levels.append(res)

    return fastapi.Response(content=json.dumps(levels), media_type='application/json')





@app.on_event("startup")
async def startup_event():
    '''
    Initializes and populates the SQLite database and creates the necessary table if it does not exist
    '''
    await init_db()
    # await load_irregular_verbs()
    # background_tasks = BackgroundTasks()
    # background_tasks.add_task(populate_db)
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8001)


# asyncio.run(populate_db())