"""Web coding quiz challenge for kids learning HTML & CSS."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAVE_FILE = HERE / "kid_rewards.json"

QUESTIONS = [
    {
        "q": "Which HTML tag is used for the biggest heading on a page?",
        "options": ["A) <heading>", "B) <h1>", "C) <head>", "D) <big>"],
        "answer": "B",
        "fact": "<h1> creates the top-level headline for your webpage!",
    },
    {
        "q": "What HTML tag do we use to show an image?",
        "options": ["A) <picture>", "B) <photo>", "C) <img>", "D) <src>"],
        "answer": "C",
        "fact": "<img> displays images, using src='...' to point to your picture!",
    },
    {
        "q": "Which tag creates a clickable hyperlink to another website?",
        "options": ["A) <a>", "B) <link>", "C) <button>", "D) <go>"],
        "answer": "A",
        "fact": "<a> stands for 'anchor' and uses href='...' to take visitors places!",
    },
    {
        "q": "What does CSS stand for in web design?",
        "options": [
            "A) Computer Screen Styling",
            "B) Cascading Style Sheets",
            "C) Creative Site Script",
            "D) Color Style System",
        ],
        "answer": "B",
        "fact": "CSS controls the colors, fonts, and layouts of your HTML pages!",
    },
    {
        "q": "Which tag creates an item inside an ordered or bulleted list?",
        "options": ["A) <item>", "B) <li>", "C) <list>", "D) <bullet>"],
        "answer": "B",
        "fact": "<li> stands for 'list item' and lives inside <ul> or <ol> tags!",
    },
    {
        "q": "How do you close an HTML tag like <p>?",
        "options": ["A) </p>", "B) <p/>", "C) <close p>", "D) <!p>"],
        "answer": "A",
        "fact": "A forward slash right before the tag name </p> closes the element!",
    },
    {
        "q": "Which HTML tag holds all the visible content shown on screen?",
        "options": ["A) <head>", "B) <meta>", "C) <body>", "D) <mainpage>"],
        "answer": "C",
        "fact": "<body> contains everything visible: text, images, buttons, and games!",
    },
]

TITLES = [
    (0, "🎨 Web Designer Apprentice"),
    (3, "🌐 HTML Builder"),
    (7, "⚡ CSS Stylist Pro"),
    (12, "🚀 Full-Stack Kid Explorer"),
    (20, "👑 Master Web Creator"),
]

BADGES = [
    (1, "⭐ First Star!", "Answered your first Web HTML riddle!"),
    (3, "🎨 Web Painter!", "3 correct HTML/CSS answers!"),
    (5, "🛡️ Bug Shield!", "5 correct answers! Clean web coder!"),
    (10, "🏆 Webmaster Legend!", "10 correct answers! Certified web wizard!"),
]


def load_rewards() -> dict:
    if SAVE_FILE.is_file():
        try:
            return json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"stars": 0, "streak": 0, "badges": []}


def save_rewards(data: dict):
    SAVE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_title(stars: int) -> str:
    current = TITLES[0][1]
    for req, title in TITLES:
        if stars >= req:
            current = title
    return current


def play():
    rewards = load_rewards()
    stars = rewards.get("stars", 0)
    badges = set(rewards.get("badges", []))

    print("\n" + "=" * 60)
    print("      🌐 HTML & CSS BRAIN CHALLENGE FOR KIDS! 🌐")
    print(f"      Current Rank: {get_title(stars)}")
    print(f"      Total Stars: {'⭐' * min(stars, 15)} ({stars} stars)")
    print("=" * 60 + "\n")

    item = random.choice(QUESTIONS)
    print(f"  ❓ QUESTION:")
    print(f"  {item['q']}\n")
    for opt in item["options"]:
        print(f"    {opt}")
    print()

    choice = input("  Your answer (A, B, C, or D): ").strip().upper()

    if choice == item["answer"]:
        stars += 1
        rewards["stars"] = stars
        print("\n" + "🎉" * 20)
        print("  CORRECT! You earned +1 Star! ⭐")
        print(f"  Web Fact: {item['fact']}")
        print("🎉" * 20)

        new_badges = []
        for req, b_name, b_desc in BADGES:
            if stars >= req and b_name not in badges:
                badges.add(b_name)
                new_badges.append((b_name, b_desc))

        if new_badges:
            print("\n  🎊 NEW REWARD UNLOCKED! 🎊")
            for b_name, b_desc in new_badges:
                print(f"    🏅 {b_name} - {b_desc}")

        rewards["badges"] = sorted(list(badges))
        print(f"\n  Your New Rank: {get_title(stars)}")
    else:
        print("\n  Nice try! Almost had it!")
        print(f"  The right answer was {item['answer']}.")
        print(f"  💡 Web Clue: {item['fact']}")

    save_rewards(rewards)
    print("\n" + "-" * 60)
    print(f"  Total Stars: {stars} ⭐ | Badges Unlocked: {len(rewards['badges'])}")
    print("-" * 60 + "\n")


if __name__ == "__main__":
    play()
