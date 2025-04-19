"""
Run this script to set up the database with sample problems
"""
from add_sample_problems import add_sample_problems

if __name__ == "__main__":
    print("Setting up sample problems in the database...")
    add_sample_problems()
    print("Setup complete. You can now start the server normally with 'python main.py'") 