# tests/locust/utils/cli.py

def banner(title):
    print("\n=====================================================")
    print(f" {title}")
    print("=====================================================\n")

def section(title):
    print(f"\n{title}")

def bullet(text):
    print(f"   • {text}")
