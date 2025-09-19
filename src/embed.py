# embed_patient_data.py
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
VECTOR_DB_DIR = "./patient_vectors"

# --- Chroma Init ---
chroma_client = chromadb.PersistentClient(path=VECTOR_DB_DIR)

# Create a collection with the default embedding function
# This uses sentence-transformers for embeddings rather than OpenAI
collection = chroma_client.get_or_create_collection(
    name="patient_chunks",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

def flatten_patient_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert the patient JSON data into small text chunks for vector embedding.
    Each chunk represents a meaningful piece of patient information.
    """
    chunks: List[Dict[str, Any]] = []
    chunk_id = 0  # Counter to generate unique IDs
    
    # --- Process patient demographics ---
    for p in data.get("patient", []):
        demo_text = (
            f"Patient: Name={p.get('name')}, "
            f"Gender={p.get('gender')}, "
            f"BirthDate={p.get('birthDate')}"
        )
        chunks.append({
            "text": demo_text,
            "type": "patient",
            "id": f"patient_{chunk_id}"
        })
        chunk_id += 1

    # --- Process lists of medical data ---
    # Helper function to process list fields
    def add_list_chunks(key: str, items: List):
        nonlocal chunk_id
        for item in items:
            chunks.append({
                "text": f"{key.capitalize()}: {item}",
                "type": key,
                "id": f"{key}_{chunk_id}"
            })
            chunk_id += 1

    # Process all medical data categories
    categories = [
        "conditions", 
        "observations", 
        "medications", 
        "procedures",
        "allergies", 
        "diagnostic_reports", 
        "immunizations",
        "encounters", 
        "careplans", 
        "claims_diagnoses"
    ]
    
    for category in categories:
        if category in data and data[category]:
            add_list_chunks(category, data[category])
    
    return chunks

def index_patient_data(data: Dict[str, Any]) -> None:
    """
    Create vector embeddings for patient data and store in ChromaDB
    """
    # Convert patient data to chunks
    chunks = flatten_patient_data(data)
    
    if not chunks:
        print("No data chunks generated. Check the format of your patient data.")
        return
    
    # Add chunks to the vector database
    collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"type": c["type"]} for c in chunks],
        ids=[c["id"] for c in chunks]
    )
    
    print(f"Successfully indexed {len(chunks)} chunks of patient data.")

def query_examples():
    """
    Show examples of how to query the vector database
    """
    print("\n--- Example Queries ---")
    
    # Example 1: Query for conditions
    results = collection.query(
        query_texts=["heart disease"],
        n_results=3
    )
    print("\nTop 3 results for 'heart disease':")
    for i, (text, metadata, distance) in enumerate(zip(
        results["documents"][0], 
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"{i+1}. {text} (type: {metadata['type']}, relevance: {1-distance:.2f})")
    
    # Example 2: Query for medications
    results = collection.query(
        query_texts=["blood pressure medication"],
        n_results=2
    )
    print("\nTop 2 results for 'blood pressure medication':")
    for i, (text, metadata, distance) in enumerate(zip(
        results["documents"][0], 
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"{i+1}. {text} (type: {metadata['type']}, relevance: {1-distance:.2f})")

def main():
    """
    Main function to process the patient data file
    """
    # File path for patient data
    patient_data_path = Path("D:/Copilot/clinicalcopilot/src/patient_data.json")
    
    # Check if file exists
    if not patient_data_path.exists():
        print(f"Error: File not found at {patient_data_path}")
        return
    
    print(f"Processing patient data from: {patient_data_path}")
    
    # Load and process the patient data
    try:
        with open(patient_data_path, "r", encoding="utf-8") as f:
            patient_data = json.load(f)
        
        # Create vector embeddings
        index_patient_data(patient_data)
        
        # Show collection information
        print("\nCollection Information:")
        print(f"Collection name: {collection.name}")
        print(f"Collection count: {collection.count()}")
        
        # Show sample documents
        print("\nSample Documents:")
        peek_results = collection.peek(limit=5)
        for i, (doc, metadata) in enumerate(zip(peek_results["documents"], peek_results["metadatas"])):
            print(f"{i+1}. {doc} (type: {metadata['type']})")
        
        # Show example queries
        query_examples()
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the patient data file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()