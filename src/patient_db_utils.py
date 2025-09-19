#!/usr/bin/env python3
"""
Shared utilities for patient-specific vector databases
"""

import hashlib
import re

def get_patient_collection_name(patient_id: str) -> str:
    """Generate a valid ChromaDB collection name for a patient
    
    ChromaDB collection naming requirements:
    - 3-63 characters
    - Start and end with alphanumeric character
    - Only alphanumeric, underscores, or hyphens
    - No consecutive special characters
    """
    # Create a hash of the patient_id to ensure uniqueness while keeping it valid
    patient_hash = hashlib.md5(patient_id.encode()).hexdigest()[:8]
    
    # Clean the patient name part for readability
    patient_name_part = re.sub(r'[^a-zA-Z0-9]', '_', patient_id)[:20]  # Take first 20 chars
    patient_name_part = re.sub(r'_+', '_', patient_name_part)  # Remove consecutive underscores
    patient_name_part = patient_name_part.strip('_')  # Remove leading/trailing underscores
    
    # Create collection name: patient_<name>_<hash>
    collection_name = f"patient_{patient_name_part}_{patient_hash}"
    
    # Ensure it meets requirements
    if len(collection_name) > 63:
        collection_name = f"patient_{patient_hash}"
    
    return collection_name

def get_patient_db_path(patient_id: str) -> str:
    """Get the path for a specific patient's vector database"""
    import os
    VECTOR_DB_BASE_DIR = "./patient_vectors"
    return os.path.join(VECTOR_DB_BASE_DIR, f"patient_{patient_id}")