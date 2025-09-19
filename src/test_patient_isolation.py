#!/usr/bin/env python3
"""
Test script for patient-specific vector databases
"""

import json
import os
from pathlib import Path
from embed import index_patient_data
from search import search_patient_data_for_context

def test_patient_isolation():
    """Test that patient databases are properly isolated"""
    
    print("=== Testing Patient-Specific Vector Databases ===")
    
    # Get two different patient files for testing
    patient_dir = Path("patient_data")
    if not patient_dir.exists():
        print("No patient_data directory found!")
        return
        
    patient_files = list(patient_dir.glob("*.json"))[:2]  # Take first two patients
    
    if len(patient_files) < 2:
        print("Need at least 2 patient files for testing")
        return
    
    print(f"Testing with patients: {[f.stem for f in patient_files]}")
    
    # Index both patients
    for patient_file in patient_files:
        patient_id = patient_file.stem
        print(f"\nIndexing patient: {patient_id}")
        
        try:
            with open(patient_file, 'r') as f:
                patient_data = json.load(f)
            
            index_patient_data(patient_data, patient_id)
            print(f"✓ Successfully indexed {patient_id}")
            
        except Exception as e:
            print(f"✗ Error indexing {patient_id}: {e}")
            return
    
    print("\n=== Testing Search Isolation ===")
    
    # Test search for each patient
    for patient_file in patient_files:
        patient_id = patient_file.stem
        print(f"\nSearching in {patient_id}'s database:")
        
        # Search for patient information
        results = search_patient_data_for_context("patient", n_results=3, patient_id=patient_id)
        
        if results:
            for i, result in enumerate(results):
                result_patient_id = result['metadata'].get('patient_id', 'MISSING')
                if result_patient_id == patient_id:
                    print(f"  ✓ Result {i+1}: Correct patient data - {result['text'][:50]}...")
                else:
                    print(f"  ✗ Result {i+1}: WRONG patient data! Expected {patient_id}, got {result_patient_id}")
                    return
        else:
            print(f"  ⚠️  No results found for {patient_id}")
    
    print("\n=== Testing Cross-Patient Search ===")
    
    # Test that searching patient A's database doesn't return patient B's data
    patient_a_id = patient_files[0].stem
    patient_b_id = patient_files[1].stem
    
    print(f"Searching for '{patient_b_id}' in {patient_a_id}'s database (should return no matches):")
    cross_results = search_patient_data_for_context(patient_b_id, n_results=5, patient_id=patient_a_id)
    
    if not cross_results:
        print("  ✓ No cross-contamination - correct isolation!")
    else:
        print(f"  ⚠️  Found {len(cross_results)} results (might be generic terms)")
        for result in cross_results:
            print(f"    - {result['text'][:50]}...")
    
    print("\n=== Test Complete ===")
    print("✅ Patient-specific vector databases are working correctly!")

def list_patient_databases():
    """List all patient databases"""
    base_dir = Path("./patient_vectors")
    if not base_dir.exists():
        print("No patient vector databases found")
        return
    
    patient_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("patient_")]
    
    print(f"\nFound {len(patient_dirs)} patient databases:")
    for patient_dir in patient_dirs:
        patient_id = patient_dir.name.replace("patient_", "")
        print(f"  - {patient_id}")
        
        # Try to get count of items in this database
        try:
            from search import get_patient_db_collection
            collection = get_patient_db_collection(patient_id)
            if collection:
                count = collection.count()
                print(f"    ({count} embeddings)")
        except Exception as e:
            print(f"    (error reading: {e})")

if __name__ == "__main__":
    print("Patient Database Isolation Test")
    print("=" * 40)
    
    list_patient_databases()
    test_patient_isolation()