# FreshBazaar

Fresh meat, delivered fast — an e-commerce platform for ordering meat in Kathmandu.

## Tech Stack

- **Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS, Zustand, Axios
- **Backend:** Django 6, Django REST Framework, JWT (SimpleJWT), PostgreSQL

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL

## Quick Start

### Backend

```bash
cd Backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in `Backend/`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=freshbazaar_db
DB_USER=freshbazaar_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

```bash
python manage.py migrate
python manage.py runserver
```

For production, use gunicorn:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Frontend

```bash
cd FrontEnd/freshbazaar
npm install
```

Create `.env.local` (optional, defaults shown):

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

| Variable | Location | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Backend | Django secret key |
| `DEBUG` | Backend | Set `False` in production |
| `DB_*` | Backend | PostgreSQL connection |
| `ALLOWED_HOSTS` | Backend | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | Backend | Comma-separated CORS origins |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend API base URL |

## User Roles

- **Customer:** Browse shops, add to cart, place orders
- **Shop Owner:** Manage shop, products, and orders via dashboard

## Running Tests

Tests use SQLite in-memory (no PostgreSQL required):

```bash
cd Backend
# Activate venv first, then:
python manage.py test apps.accounts.tests apps.orders.tests apps.shops.tests apps.cart.tests apps.products.tests
```

## Docker

```bash
# From project root
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/api/docs/

## License

© 2026 FreshBazaar. Made in Nepal.
