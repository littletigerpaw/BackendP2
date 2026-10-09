# Mechanic Shop API - BackendP2

Flask API for a mechanic shop with advanced API features: rate limiting, caching, JWT customer login, token-protected customer routes, advanced ticket/mechanic queries, pagination, and inventory tracking.

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables in `.env`.
4. Run the app.

   ```bash
   gunicorn flask_app:app
   ```

## Deployment Notes

- `flask_app.py` is the production entry point.
- `ProductionConfig` reads `SECRET_KEY` and `DATABASE_URL` from the environment with `os.getenv`.
- Add `SECRET_KEY` and `DATABASE_URL` in Render when creating the web service.
- After deployment, update `swagger.json`:
  - change `host` from `127.0.0.1:5000` to your Render base URL without `https://`
  - change `schemes` from `http` to `https`

## CI/CD

The workflow in `.github/workflows/main.yaml` runs:

1. Build: installs dependencies and compiles the project.
2. Test: runs `pytest`.
3. Deploy: triggers a Render deploy only after the test job passes.

Store these GitHub repository secrets before enabling the deploy job:

- `RENDER_SERVICE_ID`
- `RENDER_API_KEY`

## Assignment Features Implemented

- Rate limiting with Flask-Limiter on `GET /customers/`.
- Caching with Flask-Caching on key read routes (`/customers`, `/mechanics`, `/inventory`, `/service-tickets`).
- Customer JWT login with `python-jose`:
   - `POST /customers/login`
   - `@token_required` wrapper for protected customer routes.
   - `GET /customers/my-tickets` with Bearer token.
- Advanced queries:
   - `PUT /service-tickets/<ticket_id>/edit` with `add_ids` and `remove_ids`.
   - `GET /mechanics/leaderboard` sorted by ticket count.
   - Pagination on `GET /customers/?page=1&per_page=10`.
- Inventory resource:
   - Inventory model with many-to-many relationship to service tickets.
   - CRUD blueprint registered under `/inventory`.
   - `POST /service-tickets/<ticket_id>/parts` to add one part to a ticket.

## API Endpoints

Customers

- `POST /customers/`
- `POST /customers/login`
- `GET /customers/` (pagination + rate limit + cache)
- `GET /customers/<int:customer_id>`
- `GET /customers/my-tickets` (Bearer token required)
- `PUT /customers/<int:customer_id>` (Bearer token required)
- `DELETE /customers/<int:customer_id>` (Bearer token required)

Mechanics

- `POST /mechanics/`
- `GET /mechanics/` (cache)
- `GET /mechanics/leaderboard`
- `PUT /mechanics/<int:id>`
- `DELETE /mechanics/<int:id>`

Service Tickets

- `POST /service-tickets/`
- `GET /service-tickets/` (cache)
- `PUT /service-tickets/<int:ticket_id>/assign-mechanic/<int:mechanic_id>`
- `PUT /service-tickets/<int:ticket_id>/remove-mechanic/<int:mechanic_id>`
- `PUT /service-tickets/<int:ticket_id>/edit`
- `POST /service-tickets/<int:ticket_id>/parts`

Inventory

- `POST /inventory/`
- `GET /inventory/` (cache)
- `GET /inventory/<int:inventory_id>`
- `PUT /inventory/<int:inventory_id>`
- `DELETE /inventory/<int:inventory_id>`

## Postman Collection Export

The verified route test collection has been exported to:

- `mechanic_shop_api.postman_collection.json`

This collection covers the customer auth flow, mechanics, service ticket operations, and inventory CRUD checks using variables for the live local server at `http://127.0.0.1:5000`.

## Testing

Run tests locally:

```bash
python -m pytest -q
```

`pytest.ini` is included so local package imports work consistently.
