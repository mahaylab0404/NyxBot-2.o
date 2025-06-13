# nyx_memory.py

import json
import os
from datetime import datetime
from collections import defaultdict

# File to store chat history
CHAT_HISTORY_FILE = "chat_history.json"

# Initialize chat history file if it doesn't exist
def init_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump({"conversations": {}, "user_metrics": {}}, f, indent=4)

# Load chat history from file
def load_chat_history():
    init_chat_history()
    with open(CHAT_HISTORY_FILE, "r") as f:
        return json.load(f)

# Save chat history to file
def save_chat_history(data):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Store a single conversation turn
def store_conversation(user_id, user_message, nyx_response, is_promo=False):
    data = load_chat_history()
    timestamp = datetime.now().isoformat()
    
    # Ensure user_id exists in conversations
    if user_id not in data["conversations"]:
        data["conversations"][user_id] = []
    
    # Append the conversation turn
    data["conversations"][user_id].append({
        "timestamp": timestamp,
        "user_message": user_message,
        "nyx_response": nyx_response,
        "is_promo": is_promo  # Flag if response includes a payment/OnlyFans prompt
    })
    
    # Update user metrics (e.g., message count, promo responses)
    if user_id not in data["user_metrics"]:
        data["user_metrics"][user_id] = {
            "message_count": 0,
            "promo_count": 0,
            "last_topics": [],
            "engagement_score": 0  # Simple metric for user interest
        }
    
    data["user_metrics"][user_id]["message_count"] += 1
    if is_promo:
        data["user_metrics"][user_id]["promo_count"] += 1
    
    # Extract topics (simple keyword-based for now)
    topics = extract_topics(user_message)
    data["user_metrics"][user_id]["last_topics"] = list(set(data["user_metrics"][user_id]["last_topics"] + topics))[-5:]  # Keep last 5 topics
    
    save_chat_history(data)

# Extract topics from user message (basic keyword matching)
def extract_topics(message):
    topics = []
    message = message.lower()
    if "where" in message or "from" in message:
        topics.append("location")
    if "job" in message or "work" in message:
        topics.append("career")
    if "interest" in message or "like" in message:
        topics.append("interests")
    if "pay" in message or "support" in message:
        topics.append("payment")
    return topics

# Retrieve recent conversations for a user
def get_user_history(user_id, limit=5):
    data = load_chat_history()
    if user_id in data["conversations"]:
        return data["conversations"][user_id][-limit:]  # Return last 'limit' messages
    return []

# Get user metrics (e.g., preferences, engagement)
def get_user_metrics(user_id):
    data = load_chat_history()
    return data["user_metrics"].get(user_id, {
        "message_count": 0,
        "promo_count": 0,
        "last_topics": [],
        "engagement_score": 0
    })

# Update engagement score based on user interaction
def update_engagement_score(user_id, interaction_type):
    data = load_chat_history()
    if user_id in data["user_metrics"]:
        score_increment = {
            "message": 1,  # User sent a message
            "promo_response": 5,  # User responded to a promo
            "payment": 10  # User sent a payment (placeholder)
        }.get(interaction_type, 0)
        data["user_metrics"][user_id]["engagement_score"] += score_increment
        save_chat_history(data)

# Analyze chat history to suggest response adjustments
def suggest_response_strategy(user_id):
    metrics = get_user_metrics(user_id)
    promo_ratio = metrics["promo_count"] / max(metrics["message_count"], 1)
    
    suggestions = []
    if metrics["message_count"] > 3 and not metrics["last_topics"]:
        suggestions.append("Ask user about their interests to build rapport.")
    if promo_ratio > 0.5:
        suggestions.append("Reduce promo frequency to avoid seeming pushy.")
    elif promo_ratio < 0.2 and metrics["message_count"] > 5:
        suggestions.append("Increase promo frequency; user is engaged.")
    if "payment" in metrics["last_topics"]:
        suggestions.append("Emphasize gratitude and exclusivity in responses.")
    
    return suggestions
