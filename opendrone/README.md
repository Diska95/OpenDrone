# OpenDrone Platform

Marketplace per progetti drone open-source: designer creano progetti stampabili, nodi di stampa producono i pezzi, centri di assemblaggio montano i droni, customer comprano.

## Stack

- **Backend**: Django 5 + DRF + PostgreSQL 16 + Redis 7 + Celery 5
- **Frontend**: Vue 3 + Vite + Pinia + Vue Router 4
- **Auth**: JWT (djangorestframework-simplejwt)
- **Pagamenti**: Stripe Connect
- **Storage**: filesystem locale in dev, S3 in prod

## Avvio (prima volta)

```bash
cp backend/.env.example backend/.env
docker-compose up --build
```

In un altro terminale:

```bash
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py loaddata apps/marketplace/fixtures/categories.json
```

## URL

- Backend API: http://localhost:8000/api
- Admin Django: http://localhost:8000/admin
- Frontend: http://localhost:5173
