#!/usr/bin/env python3
"""
Create a .env file from the .env.example template.
This script helps users set up their local development environment.
"""

import os
import sys

def create_env_file():
    """Create a .env file from the .env.example template"""
    
    # Check if .env file already exists
    if os.path.exists(".env"):
        print("A .env file already exists. Do you want to overwrite it? (y/n)")
        response = input().lower()
        if response != 'y':
            print("Aborting.")
            return
    
    # Check if .env.example exists
    if not os.path.exists(".env.example"):
        print("Error: .env.example file not found.")
        return
    
    # Read the example file
    with open(".env.example", "r") as example_file:
        example_content = example_file.readlines()
    
    # Collect values from user
    env_content = []
    
    print("Setting up your .env file for local development.")
    print("Press Enter to keep the default value (shown in parentheses).\n")
    
    for line in example_content:
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            env_content.append(line)
            continue
        
        # Parse key and default value
        key, default_value = line.split("=", 1)
        
        # Ask user for value
        print(f"{key}? ({default_value})")
        user_value = input()
        
        # Use default if user didn't provide a value
        if not user_value:
            user_value = default_value
        
        # Add to env content
        env_content.append(f"{key}={user_value}")
    
    # Write to .env file
    with open(".env", "w") as env_file:
        env_file.write("\n".join(env_content) + "\n")
    
    print("\n.env file created successfully!")
    print("You can now run the tests or use the Makefile commands.")

if __name__ == "__main__":
    create_env_file() 