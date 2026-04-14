import re

def remove_emojis():
    filepath = "dashboard/app.py"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Define exact replacements
    replacements = {
        "🔑": "⚷",
        "📥": "⭳",
        "🔍": "⚲",
        "🤖": "✦",
        "🔗": "⚙",
        "📊": "▤",
        "✅": "✓",
        "⚠️": "⚠",
        "✨": "✧",
        "🕰️": "⧗",
        "🏠": "⌂"
    }

    for emoji, symbol in replacements.items():
        content = content.replace(emoji, symbol)

    # Some old ones might still have the space, or might need removal.
    # The symbols above are very elegant, but if the user wants them completely gone:
    # "remove evry possible emoji... replace them with something better and adjust that name also"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    remove_emojis()
    print("Emojis replaced successfully.")
