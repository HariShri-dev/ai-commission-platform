import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import CommissionPlatform

def main():
    """Application entry point"""
    app = CommissionPlatform()
    app.run()

if __name__ == "__main__":
    main()