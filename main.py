import logging
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import pages,auth,recommendations
app=FastAPI(title=settings.app_name,version='1.0.0',description='Budget-aware home, party and jewelry planner.')
app.add_middleware(CORSMiddleware, allow_origins=['http://127.0.0.1:8000','http://localhost:8000'], allow_credentials=True, allow_methods=['GET','POST'], allow_headers=['Authorization','Content-Type'])
app.add_middleware(SessionMiddleware,secret_key=settings.secret_key,same_site='lax',https_only=False)
app.mount('/static',StaticFiles(directory='app/static'),name='static')
app.include_router(pages.router); app.include_router(auth.router); app.include_router(recommendations.router)
@app.on_event('startup')
async def startup(): init_db()
@app.get('/health')
async def health(): return {'status':'ok','app':settings.app_name,'ai_mode':'gemini' if settings.gemini_api_key else 'demo','model':settings.gemini_model if settings.gemini_api_key else None}
@app.get('/session-info')
async def session_info(request:Request):
    return {'authenticated':bool(request.session.get('user_id')),'user_id':request.session.get('user_id'),'username':request.session.get('username')}
@app.get('/session-data')
async def session_data(request:Request):
    uid=request.session.get('user_id')
    if not uid: return {'authenticated':False,'data':{}}
    plans=__import__('app.database',fromlist=['list_plans']).list_plans(uid,10)
    return {'authenticated':True,'username':request.session.get('username'),'recent_plan_count':len(plans),'recent_plans':[{'id':p['id'],'type':p['planner_type'],'created_at':p['created_at']} for p in plans]}
@app.exception_handler(Exception)
async def unexpected_error(request:Request,exc:Exception):
    logging.exception('Unhandled application error')
    return JSONResponse(status_code=500,content={'detail':'Unexpected server error. Check server terminal logs.'})
if __name__=='__main__':
    import uvicorn
    uvicorn.run('app.main:app',host='127.0.0.1',port=8000,reload=True)
