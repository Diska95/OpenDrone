# OpenDrone — Guida al Deploy su AWS

## Architettura

```
[Dominio] → [EC2 t3.micro]
               ├── Nginx (reverse proxy + SSL)
               ├── Django/Gunicorn (backend API)
               ├── Celery worker + beat
               └── Redis (broker)
            → [RDS t3.micro] (PostgreSQL)
            → [S3] (file media + static)
            → [SES] (email)

[Frontend] → Vercel (deploy automatico da GitHub)
```

## 1. Acquista il dominio
- Namecheap, Cloudflare Registrar, o Route 53
- Consiglio: Cloudflare (~€10/anno) per DNS gratuito e CDN

## 2. Crea le risorse AWS

### EC2 (backend)
1. Vai su EC2 → Launch Instance
2. **AMI**: Ubuntu 24.04 LTS
3. **Tipo**: t3.micro (Free Tier)
4. **Storage**: 20GB gp3
5. **Security Group**: apri porte 22 (SSH), 80 (HTTP), 443 (HTTPS)
6. Crea e scarica la chiave `.pem`

### RDS (database)
1. Vai su RDS → Create Database
2. **Engine**: PostgreSQL 16
3. **Template**: Free Tier
4. **Tipo**: db.t3.micro
5. **DB name**: opendrone
6. **Username**: opendrone_user
7. **Password**: scegli una password sicura
8. **VPC**: stessa dell'EC2
9. **Public access**: No (solo accesso da EC2)

### S3 (file)
1. Crea bucket: `opendrone-files`
2. **Regione**: eu-south-1 (Milano)
3. Blocca accesso pubblico (i file saranno serviti con URL firmati)
4. Crea un utente IAM con policy `AmazonS3FullAccess` + `AmazonSESFullAccess`
5. Genera Access Key per quell'utente

## 3. Configura il server EC2

```bash
# Connettiti
ssh -i tuachiave.pem ubuntu@IP_EC2

# Installa dipendenze
sudo apt update && sudo apt install -y docker.io docker-compose git

# Clona il repo
git clone git@github.com:Diska95/OpenDrone.git
cd OpenDrone

# Copia e compila il file env
cp backend/.env.production backend/.env
nano backend/.env   # compila tutti i valori

# Avvia
docker-compose -f docker-compose.prod.yml up -d --build
```

## 4. SSL con Let's Encrypt

```bash
# Prima volta: ottieni i certificati
docker-compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot --webroot-path /var/www/certbot \
  -d tuodominio.it -d www.tuodominio.it -d api.tuodominio.it \
  --email tua@email.it --agree-tos --no-eff-email

# Poi riavvia nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

## 5. Deploy frontend su Vercel

1. Vai su https://vercel.com → New Project → importa da GitHub
2. **Framework**: Vue.js / Vite
3. **Root Directory**: `frontend`
4. **Environment Variables**:
   - `VITE_API_URL` = `https://api.tuodominio.it/api`
5. Collega il dominio custom nelle impostazioni Vercel

## 6. Crea il superuser Django

```bash
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py createsuperuser
```

## Aggiornamenti futuri

```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```
