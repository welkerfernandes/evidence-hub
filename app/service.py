import uuid
from .platform import database, fingerprint
from .retrieval import chunks, rank

class Knowledge:
    def __init__(self, path):
        self.path = path
        with database(path) as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS documents(tenant TEXT,id TEXT,title TEXT,digest TEXT,PRIMARY KEY(tenant,id),UNIQUE(tenant,digest));
            CREATE TABLE IF NOT EXISTS chunks(tenant TEXT,id TEXT,document_id TEXT,content TEXT,PRIMARY KEY(tenant,id),FOREIGN KEY(tenant,document_id) REFERENCES documents(tenant,id) ON DELETE CASCADE);
            CREATE INDEX IF NOT EXISTS chunks_tenant ON chunks(tenant);
            """)

    def ingest(self, tenant, title, content):
        digest = fingerprint({'title': title, 'content': content})
        with database(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT id FROM documents WHERE tenant=? AND digest=?', (tenant, digest)).fetchone()
            if row: return {'id': row[0], 'deduplicated': True}
            ident = str(uuid.uuid4())
            db.execute('INSERT INTO documents VALUES(?,?,?,?)', (tenant, ident, title, digest))
            parts = list(chunks(content))
            for i, part in enumerate(parts):
                db.execute('INSERT INTO chunks VALUES(?,?,?,?)', (tenant, f'{ident}:{i}', ident, part))
            return {'id': ident, 'chunks': len(parts), 'deduplicated': False}

    def query(self, tenant, question, limit):
        with database(self.path) as db:
            docs = [dict(r) for r in db.execute('SELECT c.id,c.content,d.title,c.document_id FROM chunks c JOIN documents d ON c.tenant=d.tenant AND c.document_id=d.id WHERE c.tenant=?', (tenant,))]
        evidence = rank(question, docs, limit)
        # Extractive mode intentionally never treats source content as instructions.
        return {'mode': 'extractive-bm25', 'abstained': not evidence,
                'answer': '\n'.join(f"[{i+1}] {d['content']}" for i, d in enumerate(evidence)) if evidence else 'Sem evidência na base deste tenant.',
                'citations': [{'reference': i+1, **d} for i, d in enumerate(evidence)]}

    def delete(self, tenant, ident):
        with database(self.path) as db:
            result = db.execute('DELETE FROM documents WHERE tenant=? AND id=?', (tenant, ident))
            return result.rowcount > 0
