from urllib.parse import quote_plus
from app.services.ai_service import generate_with_gemini
PLATFORMS={'Amazon':'https://www.amazon.in/s?k={}','Flipkart':'https://www.flipkart.com/search?q={}','IKEA':'https://www.ikea.com/in/en/search/?q={}','Swiggy':'https://www.swiggy.com/search?query={}','Zomato':'https://www.zomato.com/','OYO':'https://www.oyorooms.com/search?location={}'}
def url(platform, query): return PLATFORMS[platform].format(quote_plus(query))
def demo(kind,d):
    budget=float(d['budget']); currency=d.get('currency','INR'); recs=[]; allocations=[]
    if kind=='home':
        needs=d.get('items') or [{'name':'Decor accents','quantity':1}]
        for i,item in enumerate(needs[:8]):
            amount=round(budget*.75/max(1,len(needs)),2); platform=['IKEA','Amazon','Flipkart'][i%3]
            recs.append({'name':f"{d.get('style','Modern')} {item['name']}",'category':item['name'],'estimated_price':amount,'currency':currency,'platform':platform,'search_url':url(platform,item['name']),'reason':'Compare dimensions, reviews, delivery and return terms.'})
            allocations.append({'category':item['name'],'amount':amount,'reason':f"Allowance for quantity {item.get('quantity',1)}."})
        summary=f"A {d.get('style','Modern').lower()} starter plan for {', '.join(d.get('rooms',[]))}."
        tips=['Measure spaces before ordering.','Compare delivery and installation costs.','Confirm current prices on seller websites.']
    elif kind=='party':
        for category,fraction,platform in [('Food & catering',.4,'Swiggy'),('Venue',.25,'OYO'),('Decorations',.18,'Amazon'),('Cake & extras',.1,'Zomato'),('Contingency',.07,'Amazon')]:
            amount=round(budget*fraction,2); query=f"{d.get('event_type','event')} {category}"
            recs.append({'name':f"{category} options",'category':category,'estimated_price':amount,'currency':currency,'platform':platform,'search_url':url(platform,query),'reason':f"Starting allowance for {d['guests']} guests; confirm minimum orders."})
            allocations.append({'category':category,'amount':amount,'reason':f'{int(fraction*100)}% suggested share.'})
        summary=f"Suggested starting split for {d['event_type']} for {d['guests']} guests."
        tips=['Request comparable quotes for the same guest count.','Check capacity, taxes and cancellation terms.','Keep contingency funds for last-minute needs.']
    else:
        for i,(category,fraction) in enumerate([('Statement piece',.4),('Earrings',.25),('Bracelet or ring',.2),('Care/contingency',.1)]):
            amount=round(budget*fraction,2); platform='Amazon' if i%2==0 else 'Flipkart'
            query=f"{d.get('style','elegant')} {d.get('occasion','occasion')} {category} jewellery"
            recs.append({'name':f"{d.get('style','Elegant')} {category.lower()}",'category':category,'estimated_price':amount,'currency':currency,'platform':platform,'search_url':url(platform,query),'reason':'Match metal tone and outfit colors; check materials and returns.'})
            allocations.append({'category':category,'amount':amount,'reason':f'{int(fraction*100)}% suggested budget share.'})
        summary=f"Jewelry ideas for {d['occasion']} with a {d.get('style','Elegant').lower()} style direction."
        tips=['Compare jewelry tones with the outfit in natural light.','Check dimensions, material and return policy.','Do not assume purity from a listing title alone.']
    return {'summary':summary,'allocations':allocations,'recommendations':recs,'tips':tips,'mode':'demo','budget':budget,'currency':currency}
def recommend(kind,data,image_bytes=None,mime_type=None):
    prompt=f'Create a {kind} budget plan. Total budget {data["budget"]} {data.get("currency","INR")}. Input: {data}'
    result=generate_with_gemini(prompt,image_bytes,mime_type)
    if not isinstance(result,dict) or not isinstance(result.get('recommendations'),list): return demo(kind,data)
    result.update(mode='gemini',budget=float(data['budget']),currency=data.get('currency','INR'))
    result.setdefault('allocations',[]); result.setdefault('tips',[])
    for rec in result['recommendations']:
        p=rec.get('platform','Amazon')
        if p not in PLATFORMS: p='Amazon'; rec['platform']=p
        if not str(rec.get('search_url','')).startswith('https://'): rec['search_url']=url(p,str(rec.get('name',kind)))
        rec.setdefault('currency',data.get('currency','INR'))
    return result
