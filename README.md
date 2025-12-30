# DeFi Risk Curator MVP

A minimal viable product for DeFi risk monitoring and rating system.

## Features

- **Asset Rating System**: Three-layer risk rating based on Steakhouse Financial framework
  - Issuer Risk (Social, Decentralization, Technical)
  - Credit Risk
  - Operational Risk (Lindy, Audit, Transparency)
- **Price Monitoring**: Real-time price tracking via CoinGecko and DeFiLlama
- **Alert System**: Telegram notifications for price deviations and depegs
- **Dashboard**: Visual overview of assets, ratings, and alerts

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic (migrations)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React Query

## Project Structure

```
Risk-Curator-MVP/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── alembic/            # DB migrations
│   └── Dockerfile
├── frontend/               # Next.js Frontend
│   ├── app/                # App Router pages
│   ├── components/         # React components
│   ├── lib/                # Utilities & API client
│   └── types/              # TypeScript types
└── docker-compose.yml      # Local development
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Local Development

1. **Start database with Docker:**
```bash
docker-compose up -d db redis
```

2. **Run backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env      # Edit with your settings
alembic upgrade head      # Run migrations
uvicorn app.main:app --reload
```

3. **Run frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

4. **Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Full Docker Setup
```bash
docker-compose up --build
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/risk_monitor
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_DEFAULT_CHAT_ID=your_chat_id
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## API Endpoints

### Assets
- `GET /api/v1/assets` - List assets
- `POST /api/v1/assets` - Create asset
- `GET /api/v1/assets/{id}` - Get asset
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset

### Ratings
- `GET /api/v1/ratings/assets` - List ratings
- `POST /api/v1/ratings/assets` - Create rating
- `GET /api/v1/ratings/assets/{asset_id}` - Get rating
- `PUT /api/v1/ratings/assets/{asset_id}` - Update rating

### Alerts
- `GET /api/v1/alerts/configs` - List alert configs
- `POST /api/v1/alerts/configs` - Create alert
- `POST /api/v1/alerts/configs/{id}/test` - Test alert
- `GET /api/v1/alerts/history` - Alert history

### Monitor
- `GET /api/v1/monitor/prices/{asset_id}` - Get price
- `GET /api/v1/monitor/tvl/{protocol}` - Get TVL
- `POST /api/v1/monitor/check` - Trigger check

## Rating System

### Score Scale (1-6)
- 1 = AA (Best)
- 2 = A
- 3 = BB
- 4 = B
- 5 = CC
- 6 = C (Worst)

### Vault Eligibility
- **Prime**: AA or A rating
- **High Yield**: BB or B rating
- **Constrained**: CC rating
- **Excluded**: C rating

## Telegram Setup

1. Create bot via [@BotFather](https://t.me/BotFather)
2. Get bot token
3. Add bot to your group
4. Get chat ID via [@userinfobot](https://t.me/userinfobot)
5. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_DEFAULT_CHAT_ID`

## Deployment

### Backend (Railway)
1. Connect GitHub repo
2. Set environment variables
3. Deploy

### Frontend (Vercel)
1. Import project
2. Set `NEXT_PUBLIC_API_URL`
3. Deploy

## License

MIT
