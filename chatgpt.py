from openai import OpenAI
import json

client = OpenAI()

def draft_email(post):

    master_prompt = f"""
    You are an expert Sales Development Representative at AIRPARK.
    Generate a personalized outreach email based on this JSON lead: {json.dumps(post)}

    GUIDELINES:
    1. Tone: Professional/Efficiency-driven for corporate roles, Warm/Aspirational for personal travel.
    2. Intent: Since the intent is {post.get('travel_intent_level')}, be {'direct' if post.get('travel_intent_level') == 'High' else 'consultative'}.
    3. Personalization: Mention their specific role as {post.get('role_business')} and their interest in {post.get('location')}.
    4. Call to Action: Suggest a meeting or a custom proposal based on their budget: {post.get('hotel_requirements')}.
    5. Constraint: Max 150 words. No 'I hope this email finds you well.'
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a High-End Travel Email Marketing Specialist for AIRPARK."
                },
                {"role": "user", "content": master_prompt}
            ]
        )
        
        email_content = response.choices[0].message.content
        print(f"--- EMAIL FOR: {post['author_name']} ({post['contact_email']}) ---")
        print(email_content)
        print("-" * 50)
        
        return email_content

    except Exception as e:
        print(f"Error drafting email for {post['author_name']}: {e}")



