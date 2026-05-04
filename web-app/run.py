"""
Entry point for the Flask web application.
"""

from app import create_app
from dotenv import load_dotenv
import os

def main():
    """
    Main function
    """
    load_dotenv()
    config = {
        "SECRET_KEY": os.getenv("SECRET_KEY"),
    }
    app = create_app(config = config)
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
