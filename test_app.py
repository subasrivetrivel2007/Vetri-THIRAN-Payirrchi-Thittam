import pytest
from fastapi.testclient import TestClient
@pytest.fixture
def client(tmp_path,monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings,'database_path',str(tmp_path/'test.db'))
    from app.main import app
    from app.database import init_db
    init_db()
    with TestClient(app) as c: yield c
def test_health(client): assert client.get('/health').json()['status']=='ok'
def test_home_recommendations(client,monkeypatch):
    from app.services import ai_service
    monkeypatch.setattr(ai_service,'generate_with_gemini',lambda *a,**k:None)
    r=client.post('/api/generate-home',json={'budget':12000,'rooms':['Living room'],'items':[{'name':'Lamp','quantity':2}]})
    assert r.status_code==200 and r.json()['mode']=='demo'
    assert r.json()['recommendations'][0]['search_url'].startswith('https://')
def test_validation(client):
    r=client.post('/api/generate-party',json={'budget':0,'guests':10,'event_type':'Birthday'})
    assert r.status_code==422
def test_register_plan_history(client,monkeypatch):
    from app.services import ai_service
    monkeypatch.setattr(ai_service,'generate_with_gemini',lambda *a,**k:None)
    r=client.post('/register',data={'username':'tester_1','email':'test@example.com','password':'password-123'},follow_redirects=False)
    assert r.status_code==303
    r=client.post('/api/generate-party',json={'budget':10000,'guests':12,'event_type':'Birthday'})
    assert r.status_code==200 and 'plan_id' in r.json()
    assert len(client.get('/api/history').json()['items'])==1
