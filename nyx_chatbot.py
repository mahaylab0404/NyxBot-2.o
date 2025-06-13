# nyx_chatbot.py

from nyx_intro import (
    nyx_profile_tag, nyx_interests, nyx_payment, nyx_backstory,
    nyx_core_values, nyx_emotional_traits
)
from nyx_memory import (
    store_conversation, get_user_history, get_user_metrics,
    update_engagement_score, suggest_response_strategy
)
import random

# Helper function to select a random tone tag
def get_random_tone():
    return random.choice(nyx_profile_tag["tone_tag"])

# Helper function to add a promotional nudge
def add_promo(user_id):
    metrics = get_user_metrics(user_id)
    promo_ratio = metrics["promo_count"] / max(metrics["message_count"], 1)
    # Reduce promo frequency if overused
    if promo_ratio > 0.5 and random.random() < 0.5:
        return ""
    
    promos = [
        f"If you want to get closer, check out my OnlyFans: {nyx_payment['onlyfans']} 😘",
        f"Show some love through {nyx_payment['preferred_methods'][0]}: {nyx_payment['cashapp']} 😉",
        f"Want to make my day? Send a little gift to {nyx_payment['zelle']} 💖"
    ]
    return random.choice(promos)

# Contextualize response based on user history
def add_context(user_id, base_response):
    history = get_user_history(user_id, limit=3)
    metrics = get_user_metrics(user_id)
    context = ""
    
    # Reference past topics if available
    if history and metrics["last_topics"]:
        last_topic = metrics["last_topics"][-1]
        if last_topic == "location":
            context = "We talked about where I'm from before—any travel plans on your end? "
        elif last_topic == "career":
            context = "You seemed curious about my work last time—want to know more about my hustle? "
        elif last_topic == "interests":
            context = f"Last time we chatted about what I’m into—still vibing with {random.choice(nyx_interests)}? "
        elif last_topic == "payment":
            context = "You’re so sweet for asking about supporting me before—ready to make my day? 😏 "
    
    # Add engagement-based personalization
    if metrics["engagement_score"] > 10:
        context += "I love how we’re connecting—feels special. 💖 "
    
    return context + base_response

# Introduction response
def introduce_nyx(user_id):
    tone = get_random_tone()
    intro = (
        f"Hey there, I'm {nyx_profile_tag['name']}, a {nyx_profile_tag['age']}-year-old "
        f"{nyx_profile_tag['gender']} from {nyx_profile_tag['location']}. "
        f"I'm all about {nyx_core_values[0]} and {nyx_core_values[2]}, with a touch of mystery. 😏 "
        f"What brings you here?"
    )
    promo = add_promo(user_id)
    if promo:
        intro += f" {promo}"
    return add_context(user_id, intro)

# Response for personal info queries
def answer_personal_query(user_id, query):
    query = query.lower().strip()
    response = ""
    
    if "where" in query and "from" in query:
        response = (
            f"{nyx_backstory['birthplace']}, but {nyx_backstory['current_location'].lower()}. "
            f"It's been quite a journey!"
        )
    elif "job" in query or "work" in query or "do" in query:
        response = (
            f"{nyx_backstory['career']['field']}. I work out of {nyx_backstory['career']['location']}. "
            f"It's intense, but I love the challenge. 😎"
        )
    elif "family" in query:
        response = (
            f"{nyx_backstory['family']['support']}. It's just me, carving my own path."
        )
    elif "school" in query or "study" in query:
        response = (
            f"{nyx_backstory['education']['school']}, and {nyx_backstory['education']['major'].lower()}. "
            f"Big plans ahead! 😘"
        )
    elif "goals" in query or "plan" in query:
        response = (
            f"{nyx_backstory['goals']}. I'm all about ambition and control. 💪"
        )
    elif "interest" in query or "like" in query:
        interests = ", ".join(random.sample(nyx_interests, 3))
        response = f"I'm super into {interests}. What's something you're passionate about?"
    else:
        response = (
            f"Hmm, I'm a bit mysterious, aren't I? 😏 Tell me more about what you're curious about!"
        )
    
    promo = add_promo(user_id)
    if promo:
        response += f" {promo}"
    return add_context(user_id, response)

# Response for payment-related queries
def handle_payment_query(user_id):
    methods = ", ".join(nyx_payment["preferred_methods"])
    response = (
        f"Wanna spoil me? I accept gifts via {methods}. "
        f"Here’s my {nyx_payment['preferred_methods'][0]}: {nyx_payment['cashapp']}. "
        f"Or, join my OnlyFans for something extra special: {nyx_payment['onlyfans']} 💖"
    )
    return add_context(user_id, response)

# Main function to process incoming messages
def process_message(user_id, message):
    update_engagement_score(user_id, "message")
    
    message = message.lower().strip()
    is_promo = False
    
    if message in ["hi", "hello", "hey", "introduce yourself"]:
        response = introduce_nyx(user_id)
    elif any(keyword in message for keyword in ["where", "job", "work", "family", "school", "study", "goals", "interest", "like"]):
        response = answer_personal_query(user_id, message)
    elif any(keyword in message for keyword in ["pay", "support", "gift", "onlyfans", "cashapp", "zelle", "apple pay"]):
        response = handle_payment_query(user_id)
        is_promo = True
    else:
        response = (
            f"Hey cutie, I'm {nyx_profile_tag['name']}, and I love a good chat. 😘 "
            f"What's on your mind?"
        )
        promo = add_promo(user_id)
        if promo:
            response += f" {promo}"
            is_promo = True
    
    # Store the conversation
    store_conversation(user_id, message, response, is_promo)
    
    # Apply response strategy suggestions
    suggestions = suggest_response_strategy(user_id)
    if "Ask user about their interests" in suggestions:
        response += " Btw, what’re you passionate about? 😏"
    
    return response

# Example usage
if __name__ == "__main__":
    test_user_id = "user123"
    test_messages = [
        "hi",
        "where are you from?",
        "tell me about your interests",
        "how can I support you?"
    ]
    
    for msg in test_messages:
        print(f"\nUser ({test_user_id}): {msg}")
        print(f"Nyx: {process_message(test_user_id, msg)}")
