import os
import sys

print("=" * 50)
print("DEBUGGING ENVIRONMENT VARIABLES")
print("=" * 50)

# Check all environment variables
print("\nAll environment variables:")
for key, value in os.environ.items():
    if 'TOKEN' in key.upper() or 'BOT' in key.upper():
        # Mask token for security
        if 'TOKEN' in key.upper():
            print(f"  {key}: {value[:10]}...{value[-5:] if len(value) > 15 else value}")
        else:
            print(f"  {key}: {value}")

# Check specific variables
print("\nChecking specific variables:")
token_vars = ['TELEGRAM_BOT_TOKEN', 'BOT_TOKEN', 'TELEGRAM_TOKEN']
for var in token_vars:
    value = os.getenv(var)
    if value:
        print(f"  ✅ {var}: {value[:10]}...{value[-5:] if len(value) > 15 else value}")
    else:
        print(f"  ❌ {var}: Not set")

# Try to read .env file
print("\nChecking .env file:")
try:
    with open('.env', 'r') as f:
        for line in f:
            if 'TOKEN' in line.upper():
                print(f"  Found in .env: {line.strip()[:20]}...")
except FileNotFoundError:
    print("  No .env file found")
except Exception as e:
    print(f"  Error reading .env: {e}")

print("\n" + "=" * 50)
