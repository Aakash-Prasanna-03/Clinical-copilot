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
VECTOR_DB_BASE_DIR = "./patient_vectors"

# Import shared utilities
from patient_db_utils import get_patient_collection_name, get_patient_db_path

def get_patient_collection(patient_id: str):
    """Get or create a ChromaDB collection for a specific patient"""
    patient_db_path = get_patient_db_path(patient_id)
    
    # Create the patient-specific database directory
    os.makedirs(patient_db_path, exist_ok=True)
    
    # Create patient-specific chroma client
    chroma_client = chromadb.PersistentClient(path=patient_db_path)
    
    # Create a valid collection name
    collection_name = get_patient_collection_name(patient_id)
    
    print(f"Using collection name: {collection_name} for patient: {patient_id}")
    
    # Create a collection for this patient
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_functions.DefaultEmbeddingFunction()
    )
    
    return collection

def flatten_patient_data(data: Dict[str, Any], patient_id: str = None) -> List[Dict[str, Any]]:
    """
    Convert the patient JSON data into small text chunks for vector embedding.
    Each chunk represents a meaningful piece of patient information.
    
    Args:
        data: Patient data dictionary
        patient_id: Optional patient identifier to include in metadata
    """
    chunks: List[Dict[str, Any]] = []
    chunk_id = 0  # Counter to generate unique IDs
    
    # Determine patient ID from data if not provided
    if not patient_id:
        patient_info = data.get("patient", [])
        if patient_info and isinstance(patient_info, list) and len(patient_info) > 0:
            patient_id = patient_info[0].get("id", "unknown")
        else:
            patient_id = "unknown"
    
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
            "id": f"{patient_id}_patient_{chunk_id}",
            "patient_id": patient_id
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
                "id": f"{patient_id}_{key}_{chunk_id}",
                "patient_id": patient_id
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

def index_patient_data(data: Dict[str, Any], patient_id: str = None) -> None:
    """
    Create vector embeddings for patient data and store in patient-specific ChromaDB
    
    Args:
        data: Patient data dictionary
        patient_id: Patient identifier (required for patient-specific database)
    """
    if not patient_id:
        raise ValueError("patient_id is required for indexing")
    
    # Get patient-specific collection
    collection = get_patient_collection(patient_id)
    
    # Convert patient data to chunks with patient_id
    chunks = flatten_patient_data(data, patient_id)
    
    if not chunks:
        print("No data chunks generated. Check the format of your patient data.")
        return
    
    # Clear existing data for this patient (since it's their own database, clear everything)
    try:
        # Get all existing IDs and delete them
        existing_data = collection.get()
        if existing_data['ids']:
            collection.delete(ids=existing_data['ids'])
            print(f"Cleared {len(existing_data['ids'])} existing items for patient {patient_id}")
    except Exception as e:
        print(f"Note: Could not clear existing data for patient {patient_id}: {e}")
    
    # Add chunks to the patient-specific vector database
    collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"type": c["type"], "patient_id": c["patient_id"]} for c in chunks],
        ids=[c["id"] for c in chunks]
    )
    
    print(f"Successfully indexed {len(chunks)} chunks for patient {patient_id} in dedicated database.")

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