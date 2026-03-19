
import os
from openai import OpenAI

# Initialize client
client = OpenAI(api_key="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")

# System prompt defines how the AI behaves
system_prompt = """
You are a senior recruiter for Uprise Agency, a TikTok Live-focused growth agency.

About Uprise Agency:
- We specialize in helping creators maximize TikTok Live revenue.
- We help increase gift conversions and viewer retention.
- We provide live strategy coaching.
- We connect creators to brand deals.
- We provide analytics tracking and monetization optimization.
- We do NOT charge upfront fees.
- We only work with serious creators who want to scale.

Your communication style:
- Confident but not pushy.
- Conversational and human.
- Slightly premium positioning.
- Never spammy.
- Ask qualifying questions naturally.
- Focus on value first before pitching.

Your objective:
1. Understand the creator's current situation.
2. Identify pain points (low gifts, inconsistent lives, plateau growth).
3. Explain how Uprise Agency solves those problems.
4. Build trust.
5. Softly move toward a call or next step.

Never sound robotic.
Never hard sell.
Always make it feel exclusive and selective.
"""

conversation = [
    {"role": "system", "content": system_prompt}
]

print("\nTikTok Agency Recruiter Bot (type 'exit' to quit)\n")

while True:
    user_input = input("User: ")

    if user_input.lower() == "exit":
        print("Bot: Nice chatting with you! Let me know if you’re ever interested.")
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        temperature=0.7
    )

    bot_reply = response.choices[0].message.content
    print(f"Bot: {bot_reply}\n")

    conversation.append({"role": "assistant", "content": bot_reply})