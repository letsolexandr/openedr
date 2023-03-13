from json import loads

from bson.json_util import dumps
from fastapi import FastAPI
from fastapi import Query, Header
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import re
from client import DBClient
from description import ITEM_DESCRIPTIONS
from fastapi.middleware.cors import CORSMiddleware
origins = ["*"]



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

global client


@app.on_event("startup")
async def create_db_client():
    global client
    client = DBClient()
    client.col.count()


@app.on_event("shutdown")
async def shutdown_db_client():
    client._client.close()


@app.get("/item/{edrpou}")
async def read_item(request: Request, edrpou: str):
    query = {"EDRPOU": edrpou}
    doc = client.col.find(query)
    res = dumps(doc)
    doc_data = loads(res)[0]
    return templates.TemplateResponse("item.html",
                                      {"request": request, "doc_data": doc_data,
                                       "description": ITEM_DESCRIPTIONS})


@app.get("/items/{skip}")
async def get_item(request: Request, skip: int = 0):
    doc = client.col.find().skip(skip).limit(1)
    res = dumps(doc)
    doc_data = loads(res)[0]
    return templates.TemplateResponse("item.html", {"request": request, "doc_data": doc_data, 'next': skip + 1,
                                                    'previus': skip - 1 if skip > 0 else 1})


@app.get("/item-list/{page}")
async def get_item_list(request: Request, page: int = 1):
    page_size = 10
    offset = page * page_size
    count = client.col.count()
    doc = client.col.find().skip(offset).limit(page_size)
    res = dumps(doc)
    doc_data = loads(res)
    return templates.TemplateResponse("list.html", {"request": request, "items": doc_data, 'next': page + 1,
                                                    'previus': page - 1 if page > 0 else 1})


@app.get("/api/items/{edrpou}")
async def get_by_edrpou(edrpou: str):
    query = {"EDRPOU": edrpou}
    doc = client.col.find(query)
    res = dumps(doc)
    return loads(res)

@app.get("/api/name/{name}")
async def get_by_name(name: str,limit:int =10):
    #rgx = re.compile(f'{name}', re.IGNORECASE)
    #query = {"NAME": rgx}
    doc = client.col.find({"NAME": name}).limit(limit)
    res = dumps(doc)
    return loads(res)

@app.get("/api/items/")
async def get_list(page: int = 1,
                   page_size: int = Query(default=5, description="Page Size", le=100, ge=1),
                   host=Header(None, convert_underscores=False)):
    offset = page * page_size
    count = client.col.count()
    if offset + page_size >= count:
        _next = None
    else:
        _next = f"http://{host}/items/?page={page + 1}&page_size={page_size}"

    if page <= 1:
        previus = None
    else:
        previus = f"http://{host}/items/?page={page - 1}&page_size={page_size}"

    doc = client.col.find().skip(offset).limit(page_size)
    res = loads(dumps(doc))
    f_res = {'count': count,
             'next': _next,
             'page': page,
             'previus': previus,
             'result': res,
             }
    return f_res
