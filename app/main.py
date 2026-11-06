import os
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from .platform import tenant
from .service import Knowledge

class Document(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=100000)

class Query(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=3, ge=1, le=10)

def create_app(path=None):
    app = FastAPI(title='Evidence Hub', version='1.0.0')
    knowledge = Knowledge(path or os.getenv('DATABASE_PATH', 'evidence.db'))

    @app.get('/', response_class=HTMLResponse)
    def console(): return Path(__file__).with_name('console.html').read_text(encoding='utf-8')

    @app.get('/health')
    def health(): return {'status': 'ok'}

    @app.post('/documents', status_code=201)
    def ingest(command: Document, identity: str = Depends(tenant)):
        if not command.content.strip(): raise HTTPException(422, 'Empty document')
        return knowledge.ingest(identity, command.title, command.content)

    @app.post('/query')
    def query(command: Query, identity: str = Depends(tenant)):
        return knowledge.query(identity, command.question, command.limit)

    @app.delete('/documents/{ident}')
    def delete(ident: str, identity: str = Depends(tenant)):
        if not knowledge.delete(identity, ident): raise HTTPException(404, 'Document not found')
        return {'deleted': True}

    return app

app = create_app()
