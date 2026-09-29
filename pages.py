from fastapi import APIRouter,Request,HTTPException
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_user_by_id,list_plans
router=APIRouter(); templates=Jinja2Templates(directory='app/templates')
def ctx(request,**extra):
    uid=request.session.get('user_id')
    return {'request':request,'user':get_user_by_id(uid) if uid else None,**extra}
@router.get('/',response_class=HTMLResponse)
async def home(request:Request): return templates.TemplateResponse('index.html',ctx(request))
@router.get('/planner/{kind}',response_class=HTMLResponse)
async def planner(request:Request,kind:str):
    if kind not in {'home','party','jewelry'}: raise HTTPException(404,'Planner not found')
    return templates.TemplateResponse('planner.html',ctx(request,kind=kind))
@router.get('/login',response_class=HTMLResponse)
async def login_page(request:Request): return templates.TemplateResponse('login.html',ctx(request,error=request.query_params.get('error')))
@router.get('/register',response_class=HTMLResponse)
async def register_page(request:Request): return templates.TemplateResponse('register.html',ctx(request,error=request.query_params.get('error')))
@router.get('/dashboard',response_class=HTMLResponse)
async def dashboard(request:Request):
    uid=request.session.get('user_id')
    if not uid: return RedirectResponse('/login',303)
    return templates.TemplateResponse('dashboard.html',ctx(request,plans=list_plans(uid,5)))
@router.get('/history',response_class=HTMLResponse)
async def history(request:Request):
    uid=request.session.get('user_id')
    if not uid: return RedirectResponse('/login',303)
    return templates.TemplateResponse('history.html',ctx(request,plans=list_plans(uid)))

@router.get('/testimonials',response_class=HTMLResponse)
async def testimonials(request:Request): return templates.TemplateResponse('testimonials.html',ctx(request))
