# PocketSmart AI

Complete FastAPI + Jinja2 application based on the supplied project document. Includes Home, Party and Jewelry planners; optional Gemini text/image integration; demo fallback; account registration/login/logout; JWT token endpoint; session information; saved history; responsive frontend and tests.

## Notes
- Works without a Gemini key in demo mode.
- Gemini model is configurable (`GEMINI_MODEL`, default `gemini-2.5-flash`) because model availability changes from the document's Gemini 1.5 reference.
- Search links are generated for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO. No live catalog/price API is called; sample prices are estimates, not live offers.
- For production, use HTTPS, a strong secret, rate limiting, managed database, secure cookie settings, and a full account recovery flow. The included CORS policy is intentionally restricted to local development origins.

## VS Code setup
1. Extract the ZIP and open the `pocketsmart-ai` folder in VS Code.
2. Open Terminal → New Terminal.
3. Create/activate a virtual environment:
   - Windows PowerShell: `py -m venv .venv` then `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install: `python -m pip install --upgrade pip` then `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`; set `APP_SECRET_KEY`. Add a Google AI API key to `GEMINI_API_KEY` to enable Gemini, or leave blank for demo mode.
6. Run: `uvicorn app.main:app --reload`
7. Visit `http://127.0.0.1:8000`; API docs: `http://127.0.0.1:8000/docs`.

## Tests
`pytest -q` (verified locally: 4 tests passed).

## API
- `GET /health`
- `GET /testimonials` (project information; no fabricated customer reviews)
- `POST /api/generate-home` JSON: budget, rooms, style, items, preferences, currency
- `POST /api/generate-party` JSON: budget, guests, event_type, venue, preferences, currency
- `POST /api/generate-jewelry` multipart: budget, occasion, style, outfit_description, optional outfit_image
- `POST /register`, `POST /login`, `POST /logout`, `POST /token`
- `GET /session-info`, `GET /session-data`, `GET /api/history`
- `GET /api/recommendations-details/{plan_id}`

Example:
```bash
curl -X POST http://127.0.0.1:8000/api/generate-home -H "Content-Type: application/json" -d '{"budget":30000,"rooms":["Living room"],"items":[{"name":"Lighting","quantity":2}],"style":"Minimal"}'
```
