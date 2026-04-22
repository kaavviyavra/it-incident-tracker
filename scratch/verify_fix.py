import os
from pathlib import Path
from dotenv import load_dotenv

def verify():
    # Simulate main.py logic (if run from root, main.py is in backend/)
    # But here we just check if we can load it.
    env_path = Path('backend') / '.env'
    load_dotenv(dotenv_path=env_path)
    print(f"SNOW_INSTANCE_URL: {os.getenv('SNOW_INSTANCE_URL')}")
    print(f"SNOW_USERNAME: {os.getenv('SNOW_USERNAME')}")
    
    # Check if password is quoted (python-dotenv removes quotes automatically)
    pwd = os.getenv('SNOW_PASSWORD')
    print(f"SNOW_PASSWORD length: {len(pwd) if pwd else 0}")

if __name__ == "__main__":
    verify()
