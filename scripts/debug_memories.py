
import sys
import os
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mark_cli.database import MemoryDB, init_database

init_database()
db = MemoryDB()
memories = db.list_memories(limit=100)

print(f"Found {len(memories)} memories:")
for mem in memories:
    print(f"ID: {mem['id']} | Key: {mem.get('key')} | Value: {mem.get('value')}")
