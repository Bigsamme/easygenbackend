import os
import json
import stripe
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# Initialize Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Ensure Supabase credentials are loaded correctly
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ Missing Supabase URL or Key. Check your .env file!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Stripe API Keys
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.route("/")
def home():
    return "Stripe Webhook Receiver is running!"

@app.route("/api/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    if not sig_header:
        return jsonify({"error": "Missing Stripe signature"}), 400  # Return 400 (Bad Request)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400  # Return 400 for invalid signature
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return 500 for internal errors

    # Handle specific Stripe events
    if event["type"] == "checkout.session.completed":
        session = event["data"]
        handle_successful_checkout(session)
        return jsonify({"message": "Session completed successfully"}), 200
    elif event["type"] == "invoice.paid":
        return jsonify({"message": "Invoice processed"}), 200
    elif event["type"] == "customer.subscription.deleted":
        session = event["data"]
        handle_customer_subscription_deleted(session)
        return jsonify({"message": "Subscription cancelled"}), 200
    else:
        return jsonify({"message": "Event received but not handled"}), 200
    

def handle_customer_subscription_deleted(session):
    print("right")
    customer_id = session["object"]["customer"]
    print(customer_id)
    supabase.table("subscriptions").update({
            "stripe_customer_id": None,
            "stripe_subscription_id": None,
            "plan_type":"free",
            "status":"inactive"
        }

    ).eq("stripe_customer_id", customer_id).execute()
    

def handle_successful_checkout(session):
    """Logs successful checkouts in Supabase"""
    try:
        user_id = session["object"]["client_reference_id"]
        print(user_id,"srgsrtfe")
        existing_user = supabase.table("subscriptions").select("user_id").eq("user_id", user_id).execute()

        if existing_user.data:
            supabase.table("subscriptions").update({

            "stripe_customer_id": session["object"]["customer"],
            "stripe_subscription_id": session["object"]["subscription"],
            "plan_type":"paid",
            "status":"active"
        }).eq("user_id", user_id).execute()


        else:
        # Save to Supabase
            supabase.table("subscriptions").upsert({
                "user_id": user_id,
                "stripe_customer_id": session["object"]["customer"],
                "stripe_subscription_id": session["object"]["subscription"],
                "plan_type":"paid",
                "status":"active"
            }).execute()
 
    except Exception:
        print(Exception)
        pass  # Silently handle errors

# Run Flask Server
if __name__ == "__main__":
    app.run()