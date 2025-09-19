import sqlite3
from pprint import pprint

# Path to your Chroma SQLite database
db_path = r"D:\Clinical Copilot\patient_vectors\chroma.sqlite3"

# Connect to the database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List all tables
print("\n--- Tables ---")
tables = cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
).fetchall()
pprint(tables)

# Count of stored embeddings
print("\n--- Embedding Count ---")
count = cur.execute("SELECT COUNT(*) FROM embeddings;").fetchone()[0]
print("Total embeddings:", count)

# Get collection information
print("\n--- Collections ---")
try:
    collections = cur.execute("SELECT id, name FROM collections;").fetchall()
    for collection in collections:
        print(f"Collection ID: {collection[0]}, Name: {collection[1]}")
except sqlite3.OperationalError as e:
    print(f"Error accessing collections table: {e}")

# Join embeddings with metadata to display documents and their metadata
print("\n--- Sample Embeddings with Documents ---")
try:
    # Get some sample embedding IDs
    embedding_samples = cur.execute(
        "SELECT id, embedding_id FROM embeddings LIMIT 5;"
    ).fetchall()
    
    for embed_id, embed_uuid in embedding_samples:
        print(f"\nEmbedding ID: {embed_id}, UUID: {embed_uuid}")
        
        # Get document text for this embedding
        doc = cur.execute(
            "SELECT string_value FROM embedding_metadata WHERE key = 'chroma:document' AND id = ?;", 
            (embed_id,)
        ).fetchone()
        
        if doc:
            print(f"Document: {doc[0]}")
        else:
            print("No document found")
        
        # Get metadata for this embedding
        metadata_rows = cur.execute(
            "SELECT key, string_value FROM embedding_metadata WHERE key != 'chroma:document' AND id = ?;", 
            (embed_id,)
        ).fetchall()
        
        if metadata_rows:
            print("Metadata:")
            for key, value in metadata_rows:
                print(f"  {key}: {value}")
        else:
            print("No metadata found")
        
        print('-' * 80)
        
except sqlite3.OperationalError as e:
    print(f"Error joining tables: {e}")

conn.close()
print("\nDone.")
