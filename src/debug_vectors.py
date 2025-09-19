#!/usr/bin/env python3
"""
Debug script to examine the vector database contents
"""

import sys
from pathlib import Path
from search import get_db_collection

def debug_vector_database():
    """Debug the vector database to see what's stored"""
    collection = get_db_collection()
    if not collection:
        print("No collection found!")
        return
    
    # Get all items in the collection
    all_items = collection.get()
    
    print(f"Total items in vector database: {len(all_items['ids'])}")
    print("\n=== Sample of stored items ===")
    
    # Show first 10 items with their metadata
    for i in range(min(10, len(all_items['ids']))):
        item_id = all_items['ids'][i]
        metadata = all_items['metadatas'][i]
        document = all_items['documents'][i][:100] + "..." if len(all_items['documents'][i]) > 100 else all_items['documents'][i]
        
        print(f"\nItem {i+1}:")
        print(f"  ID: {item_id}")
        print(f"  Metadata: {metadata}")
        print(f"  Document: {document}")
    
    # Check patient_id distribution
    print("\n=== Patient ID distribution ===")
    patient_ids = {}
    for metadata in all_items['metadatas']:
        patient_id = metadata.get('patient_id', 'NO_PATIENT_ID')
        patient_ids[patient_id] = patient_ids.get(patient_id, 0) + 1
    
    for pid, count in patient_ids.items():
        print(f"  {pid}: {count} items")
    
    # Check type distribution
    print("\n=== Type distribution ===")
    types = {}
    for metadata in all_items['metadatas']:
        type_val = metadata.get('type', 'NO_TYPE')
        types[type_val] = types.get(type_val, 0) + 1
    
    for type_val, count in types.items():
        print(f"  {type_val}: {count} items")

def test_patient_filtering():
    """Test patient filtering with a specific query"""
    from search import search_patient_data_for_context
    
    print("\n=== Testing patient filtering ===")
    
    # Test with no patient filter
    print("\n1. Query without patient filter:")
    results = search_patient_data_for_context("patient condition", n_results=5)
    for i, result in enumerate(results):
        print(f"  {i+1}. Patient ID: {result['metadata'].get('patient_id', 'MISSING')} - {result['text'][:50]}...")
    
    # Test with specific patient filter
    print("\n2. Query with Abdul patient filter:")
    results = search_patient_data_for_context("patient condition", n_results=5, patient_id="Abdul218_Harris789_b0a06ead-cc42-aa48-dad6-841d4aa679fa")
    for i, result in enumerate(results):
        print(f"  {i+1}. Patient ID: {result['metadata'].get('patient_id', 'MISSING')} - {result['text'][:50]}...")
    
    # Test with Alicia patient filter
    print("\n3. Query with Alicia patient filter:")
    # Need to find Alicia's actual patient ID from the files
    from pathlib import Path
    import json
    
    patient_files = list(Path("patient_data").glob("Alicia*.json"))
    if patient_files:
        alicia_id = patient_files[0].stem
        print(f"   Using Alicia ID: {alicia_id}")
        results = search_patient_data_for_context("patient condition", n_results=5, patient_id=alicia_id)
        for i, result in enumerate(results):
            print(f"  {i+1}. Patient ID: {result['metadata'].get('patient_id', 'MISSING')} - {result['text'][:50]}...")
    else:
        print("   No Alicia patient files found")

if __name__ == "__main__":
    print("=== Vector Database Debug ===")
    debug_vector_database()
    test_patient_filtering()
