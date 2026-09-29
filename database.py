import json, sqlite3
from pathlib import Path
from contextlib import contextmanager
from app.config import settings

@contextmanager
def connection():
    path = settings.database_path
    if path != ":memory:": Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally: conn.close()

def init_db():
    with connection() as c:
        c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, planner_type TEXT NOT NULL, request_json TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL)')

def create_user(username, email, password_hash):
    with connection() as c:
        cur = c.execute('INSERT INTO users(username,email,password_hash) VALUES(?,?,?)', (username,email.lower(),password_hash))
        return dict(c.execute('SELECT id,username,email,created_at FROM users WHERE id=?',(cur.lastrowid,)).fetchone())

def get_user_by_username(username):
    with connection() as c:
        r=c.execute('SELECT * FROM users WHERE username=?',(username,)).fetchone()
        return dict(r) if r else None

def get_user_by_id(uid):
    with connection() as c:
        r=c.execute('SELECT id,username,email,created_at FROM users WHERE id=?',(uid,)).fetchone()
        return dict(r) if r else None

def save_plan(uid, kind, req, result):
    with connection() as c:
        cur=c.execute('INSERT INTO plans(user_id,planner_type,request_json,result_json) VALUES(?,?,?,?)',(uid,kind,json.dumps(req),json.dumps(result)))
        r=dict(c.execute('SELECT id,planner_type,request_json,result_json,created_at FROM plans WHERE id=?',(cur.lastrowid,)).fetchone())
    r['request']=json.loads(r.pop('request_json')); r['result']=json.loads(r.pop('result_json'))
    return r

def list_plans(uid, limit=50):
    with connection() as c: rows=c.execute('SELECT id,planner_type,request_json,result_json,created_at FROM plans WHERE user_id=? ORDER BY id DESC LIMIT ?',(uid,limit)).fetchall()
    out=[]
    for row in rows:
        r=dict(row); r['request']=json.loads(r.pop('request_json')); r['result']=json.loads(r.pop('result_json')); out.append(r)
    return out

def get_plan(uid, pid):
    return next((p for p in list_plans(uid, 1000) if p['id']==pid), None)
