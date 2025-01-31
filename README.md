# Stripe Payment Backend

This is a FastAPI backend that handles Stripe payments and updates the Supabase database.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the backend directory with your credentials:
```
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

3. Run the server:
```bash
python main.py
```

## Endpoints

- POST `/api/create-checkout-session`: Creates a Stripe checkout session
- POST `/api/webhook/stripe`: Handles Stripe webhooks

## Features

- Creates Stripe checkout sessions
- Handles webhook events
- Updates Supabase database
- Logs webhook events
- Error handling and monitoring