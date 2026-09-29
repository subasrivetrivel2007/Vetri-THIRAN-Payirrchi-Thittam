import json
from app.config import settings
INSTRUCTIONS = '''Return valid JSON only with keys summary, allocations, recommendations, tips. Each recommendation needs name, category, estimated_price, currency, platform, search_url, reason. Respect the total budget. Prices are estimates, not verified live listings. Never claim live availability.'''
def generate_with_gemini(prompt, image_bytes=None, mime_type=None):
    if not settings.gemini_api_key: return None
    try:
        from google import genai
        from google.genai import types
        client=genai.Client(api_key=settings.gemini_api_key)
        contents=[INSTRUCTIONS+'\nUser request: '+prompt]
        if image_bytes: contents.append(types.Part.from_bytes(data=image_bytes,mime_type=mime_type or 'image/jpeg'))
        response=client.models.generate_content(model=settings.gemini_model,contents=contents,config=types.GenerateContentConfig(temperature=0.4,response_mime_type='application/json'))
        text=(response.text or '').strip()
        if text.startswith('```'): text=text.split('\n',1)[-1].rsplit('```',1)[0].strip()
        return json.loads(text)
    except Exception: return None
