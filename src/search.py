# search_patient_data.py
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
VECTOR_DB_DIR = "./patient_vectors"

def get_db_collection():
    """
    Initialize and return the ChromaDB collection
    """
    chroma_client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    
    # Get the existing collection with embeddings
    try:
        collection = chroma_client.get_collection(
            name="patient_chunks",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )
        return collection
    except Exception as e:
        print(f"Error accessing collection: {str(e)}")
        print("Make sure you've run embed_patient_data.py first to create the embeddings.")
        return None

def search_patient_data(query: str, n_results: int = 5, filter_type: Optional[str] = None) -> None:
    """
    Search the vector database for patient data matching the query
    
    Args:
        query: The search query
        n_results: Number of results to return
        filter_type: Filter by data type (e.g., 'conditions', 'medications')
    """
    collection = get_db_collection()
    if not collection:
        return
    
    # Prepare filter if specified
    where_filter = {"type": filter_type} if filter_type else None
    
    # Search the collection
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter
    )
    
    # Display results
    print(f"\nTop {n_results} results for '{query}':")
    if filter_type:
        print(f"(Filtered to show only '{filter_type}')")
        
    if not results["documents"][0]:
        print("No matching results found.")
        return
    
    for i, (text, metadata, distance) in enumerate(zip(
        results["documents"][0], 
        results["metadatas"][0],
        results["distances"][0]
    )):
        # Convert distance to a similarity score (1.0 = perfect match)
        relevance = 1 - distance
        print(f"{i+1}. {text} (type: {metadata['type']}, relevance: {relevance:.2f})")


def search_patient_data_for_context(query: str, n_results: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search the vector database for patient data and return structured results for context
    
    Args:
        query: The search query
        n_results: Number of results to return
        filter_type: Filter by data type (e.g., 'conditions', 'medications')
        
    Returns:
        List of dictionaries containing search results with text, metadata, and relevance scores
    """
    collection = get_db_collection()
    if not collection:
        return []
    
    # Prepare filter if specified
    where_filter = {"type": filter_type} if filter_type else None
    
    # Search the collection
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter
    )
    
    formatted_results = []
    if results["documents"][0]:
        for i, (text, metadata, distance) in enumerate(zip(
            results["documents"][0], 
            results["metadatas"][0],
            results["distances"][0]
        )):
            # Convert distance to a similarity score (1.0 = perfect match)
            relevance = 1 - distance
            formatted_results.append({
                "text": text,
                "type": metadata.get('type', 'unknown'),
                "relevance": round(relevance, 3),
                "distance": round(distance, 3),
                "metadata": metadata
            })
    
    return formatted_results

def list_collection_stats() -> None:
    """
    Display statistics about the collection
    """
    collection = get_db_collection()
    if not collection:
        return
        
    print("\nCollection Statistics:")
    count = collection.count()
    print(f"Total items: {count}")
    
    # Get type counts
    print("\nBreakdown by data type:")
    all_items = collection.get(limit=count)
    
    type_counts = {}
    for metadata in all_items["metadatas"]:
        item_type = metadata["type"]
        type_counts[item_type] = type_counts.get(item_type, 0) + 1
    
    for data_type, count in sorted(type_counts.items()):
        print(f"- {data_type}: {count} items")

def interactive_search() -> None:
    """
    Run an interactive search session
    """
    collection = get_db_collection()
    if not collection:
        return
    
    print("\n=== Patient Data Search ===")
    print("Type 'exit' to quit, 'stats' to see collection statistics")
    print("Type 'types' to see available data types")
    
    # Get available data types once at the start
    all_items = collection.get(limit=collection.count())
    data_types = set()
    for metadata in all_items["metadatas"]:
        data_types.add(metadata["type"])
    
    while True:
        try:
            # Get search parameters
            query = input("\nEnter search query: ").strip()
            
            if query.lower() == 'exit':
                print("Exiting search...")
                break
            elif query.lower() == 'stats':
                list_collection_stats()
                continue
            elif query.lower() == 'types':
                print("\nAvailable data types:")
                for t in sorted(data_types):
                    print(f"- {t}")
                continue
            
            # Get optional filter
            print(f"Available types: {', '.join(sorted(data_types))}")
            filter_input = input("Filter by type (leave blank for all): ").strip()
            filter_type = filter_input if filter_input else None
            
            # Get number of results
            try:
                n_input = input("Number of results to show (default: 5): ").strip()
                n_results = int(n_input) if n_input else 5
            except ValueError:
                print("Invalid number, using default of 5")
                n_results = 5
            
            # Perform search
            search_patient_data(query, n_results, filter_type)
        except KeyboardInterrupt:
            print("\nSearch interrupted. Exiting...")
            break

def main() -> None:
    if len(sys.argv) == 1:
        # No arguments, run interactive mode
        interactive_search()
    elif len(sys.argv) >= 2:
        # Command line search
        query = sys.argv[1]
        n_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        filter_type = sys.argv[3] if len(sys.argv) > 3 else None
        
        search_patient_data(query, n_results, filter_type)
    else:
        print("Usage: python search.py [query] [n_results] [filter_type]")
        print("Or run without arguments for interactive mode")

if __name__ == "__main__":
    main()