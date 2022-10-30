from typing import Union
from fastapi import FastAPI
from src.crawler import start_crawl

app = FastAPI()

@app.get("/")
def read_root():
   return {"Hello": "World"}


@app.get("/search/{search_name}")
def read_item(search_name: str, q: Union[str, None] = None):
   news_df = start_crawl(search_name, 1, 1)
   return {"item_id": search_name, "q": q}