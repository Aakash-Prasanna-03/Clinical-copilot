#!/usr/bin/env python3
"""
Script to rebuild the vector database with proper patient isolation
"""

import json
import os
from pathlib import Path
import shutil
from embed import index_patient_data

def clear_vector_database():
    """Clear the entire vector database"""
    vector_db_path = Path("./patient_vectors")
    if vector_db_path.exists():
        print(f"Clearing existing vector database at {vector_db_path}")
        shutil.rmtree(vector_db_path)
        print("Vector database cleared.")
    else:
        print("No existing vector database found.")

def rebuild_patient_vectors():
    """Rebuild vector database with proper patient isolation"""
    
    # Clear existing database
    clear_vector_database()
    
    # Get all patient files
    patient_dir = Path("patient_data")
    if not patient_dir.exists():
        print("No patient_data directory found!")
        return
    
    patient_files = list(patient_dir.glob("*.json"))
    print(f"Found {len(patient_files)} patient files to process")
    
    success_count = 0
    error_count = 0
    
    for patient_file in patient_files:
        try:
            patient_id = patient_file.stem  # Use filename without extension as patient_id
            print(f"\nProcessing patient: {patient_id}")
            
            # Load patient data
            with open(patient_file, 'r') as f:
                patient_data = json.load(f)
            
            # Index with proper patient_id
            index_patient_data(patient_data, patient_id)
            success_count += 1
            print(f"Successfully indexed patient: {patient_id}")
            
        except Exception as e:
            print(f"Error processing {patient_file.name}: {e}")
            error_count += 1
    
    print(f"\n=== Rebuild Complete ===")
    print(f"Successfully processed: {success_count} patients")
    print(f"Errors: {error_count} patients")
    
    # Verify the rebuild
    verify_patient_isolation()

def verify_patient_isolation():
    """Verify that patient isolation is working correctly"""
    print("\n=== Verifying Patient Isolation ===")
    
    from search import get_db_collection, search_patient_data_for_context
    
    collection = get_db_collection()
    if not collection:
        print("ERROR: Cannot access vector database!")
        return
    
    # Get sample from database
    all_items = collection.get(limit=10)
    print(f"Database contains {collection.count()} total items")
    
    # Check for patient_id in metadata
    has_patient_id = 0
    missing_patient_id = 0
    
    sample_items = collection.get(limit=100)
    for metadata in sample_items['metadatas']:
        if 'patient_id' in metadata and metadata['patient_id']:
            has_patient_id += 1
        else:
            missing_patient_id += 1
    
    print(f"Sample of 100 items:")
    print(f"  - With patient_id: {has_patient_id}")
    print(f"  - Missing patient_id: {missing_patient_id}")
    
    # Test patient-specific queries
    print("\n=== Testing Patient-Specific Queries ===")
    
    # Get first two patient files to test
    patient_dir = Path("patient_data")
    patient_files = list(patient_dir.glob("*.json"))[:2]
    
    for patient_file in patient_files:
        patient_id = patient_file.stem
        print(f"\nTesting query for patient: {patient_id}")
        
        results = search_patient_data_for_context("patient", n_results=3, patient_id=patient_id)
        
        if results:
            all_match = True
            for result in results:
                result_patient_id = result['metadata'].get('patient_id', 'MISSING')
                if result_patient_id != patient_id:
                    all_match = False
                    print(f"  ERROR: Found result from different patient: {result_patient_id}")
                else:
                    print(f"  ✓ Correct patient data: {result['text'][:50]}...")
            
            if all_match:
                print(f"  ✅ Patient isolation working correctly for {patient_id}")
            else:
                print(f"  ❌ Patient isolation FAILED for {patient_id}")
        else:
            print(f"  ⚠️  No results found for {patient_id}")

if __name__ == "__main__":
    print("=== Patient Vector Database Rebuild ===")
    print("This will clear the existing vector database and rebuild it with proper patient isolation.")
    
    # Ask for confirmation
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        exit()
    
    rebuild_patient_vectors()