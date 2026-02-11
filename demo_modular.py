#!/usr/bin/env python3
"""
Quick demo of the modular Cortana Assistant
"""

import asyncio
from cortana_assistant import CortanaAssistant

async def demo():
    """Demo the modular assistant"""
    assistant = CortanaAssistant()
    
    # Initialize
    print("Initializing assistant...")
    success = await assistant.initialize()
    
    if not success:
        print("Failed to initialize!")
        return
    
    print("\nAssistant initialized successfully!\n")
    
    # Test queries
    queries = [
        "hello",
        "status",
        "skills",
        "memory usage",
    ]
    
    for query in queries:
        print(f"You: {query}")
        response = await assistant.process_query(query)
        print(f"Cortana: {response}\n")
    
    # Cleanup
    await assistant.cleanup()
    print("Demo complete!")

if __name__ == "__main__":
    asyncio.run(demo())
