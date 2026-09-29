from fastapi import APIRouter,Request,HTTPException,UploadFile,File,Form
from pydantic import ValidationError
from app.schemas import HomeRequest,PartyRequest,JewelryRequest
from app.services.recommendation_service import recommend
from app.database import save_plan,list_plans,get_plan
from app.config import settings
from app.security import decode_access_token
router=APIRouter(prefix='/api')
def uid_for(request):
    if request.session.get('user_id'): return int(request.session['user_id'])
    auth=request.headers.get('authorization','')
    return decode_access_token(auth.split(' ',1)[1]) if auth.lower().startswith('bearer ') else None
def persist(request,kind,data,result):
    uid=uid_for(request)
    if uid: result['plan_id']=save_plan(uid,kind,data,result)['id']
    return result
@router.post('/generate-home')
async def home(payload:HomeRequest,request:Request):
    data=payload.model_dump(); return persist(request,'home',data,recommend('home',data))
@router.post('/generate-party')
async def party(payload:PartyRequest,request:Request):
    data=payload.model_dump(); return persist(request,'party',data,recommend('party',data))
@router.post('/generate-jewelry')
async def jewelry(request:Request,budget:float=Form(...),currency:str=Form('INR'),occasion:str=Form(...),style:str=Form('Elegant'),outfit_description:str=Form(''),outfit_image:UploadFile|None=File(default=None)):
    image_bytes=mime=None
    if outfit_image and outfit_image.filename:
        mime=outfit_image.content_type or ''
        if mime not in {'image/jpeg','image/png','image/webp'}: raise HTTPException(415,'Upload JPG, PNG, or WebP.')
        image_bytes=await outfit_image.read()
        if len(image_bytes)>settings.max_upload_mb*1024*1024: raise HTTPException(413,f'Image must be {settings.max_upload_mb} MB or smaller.')
    try: payload=JewelryRequest.model_validate({'budget':budget,'currency':currency,'occasion':occasion,'style':style,'outfit_description':outfit_description})
    except ValidationError as e: raise HTTPException(422,detail=e.errors(include_url=False))
    data=payload.model_dump(); return persist(request,'jewelry',data,recommend('jewelry',data,image_bytes,mime))
@router.get('/history')
async def history(request:Request):
    uid=uid_for(request)
    if not uid: raise HTTPException(401,'Log in to view saved history.')
    return {'items':list_plans(uid)}
@router.get('/recommendations-details/{plan_id}')
async def details(plan_id:int,request:Request):
    uid=uid_for(request)
    if not uid: raise HTTPException(401,'Log in to view saved recommendations.')
    plan=get_plan(uid,plan_id)
    if not plan: raise HTTPException(404,'Recommendation not found.')
    return plan
