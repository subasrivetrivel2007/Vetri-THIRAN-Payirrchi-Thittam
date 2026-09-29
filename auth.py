from fastapi import APIRouter, Form, Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.database import create_user,get_user_by_username
from app.security import hash_password,verify_password,create_access_token
router=APIRouter()
@router.post('/register')
async def register(request:Request,username:str=Form(...),email:str=Form(...),password:str=Form(...)):
    username,email=username.strip(),email.strip().lower()
    if len(username)<3 or len(username)>40 or not username.replace('_','').isalnum(): return RedirectResponse('/register?error=Invalid%20username',303)
    if '@' not in email: return RedirectResponse('/register?error=Enter%20a%20valid%20email',303)
    if len(password)<8: return RedirectResponse('/register?error=Password%20must%20be%208%20characters',303)
    try: user=create_user(username,email,hash_password(password))
    except Exception: return RedirectResponse('/register?error=Username%20or%20email%20already%20exists',303)
    request.session['user_id']=user['id']; request.session['username']=username
    return RedirectResponse('/dashboard',303)
@router.post('/login')
async def login(request:Request,username:str=Form(...),password:str=Form(...)):
    user=get_user_by_username(username.strip())
    if not user or not verify_password(password,user['password_hash']): return RedirectResponse('/login?error=Invalid%20username%20or%20password',303)
    request.session.clear(); request.session['user_id']=user['id']; request.session['username']=user['username']
    return RedirectResponse('/dashboard',303)
@router.post('/logout')
async def logout(request:Request):
    request.session.clear(); return RedirectResponse('/',303)
@router.post('/token')
async def token(form_data:OAuth2PasswordRequestForm=Depends()):
    user=get_user_by_username(form_data.username.strip())
    if not user or not verify_password(form_data.password,user['password_hash']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Incorrect username or password',headers={'WWW-Authenticate':'Bearer'})
    return {'access_token':create_access_token(user),'token_type':'bearer','expires_in':3600}
