"""
Database Seeds Generator Wrapper

Executes the NovaCart data generator located in data/generate.py.
"""

from data.generate import generate_dataset

if __name__ == "__main__":
    generate_dataset()
