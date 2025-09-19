from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add the current directory to Python path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import search functions, but handle if ChromaDB is not available
try:
    from search import search_patient_data, get_db_collection
    VECTOR_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Vector search not available: {e}")
    VECTOR_SEARCH_AVAILABLE = False

# Try to import search functions, but handle if not available
try:
    from search import search_patient_data, get_db_collection, search_patient_data_for_context
    SEARCH_AVAILABLE = True
    print("Search functions imported successfully from search.py")
except ImportError as e:
    print(f"Warning: Search functions not available: {e}")
    SEARCH_AVAILABLE = False
    search_patient_data = None
    get_db_collection = None
    search_patient_data_for_context = None

# Try to import embed functions for indexing
try:
    from embed import index_patient_data, flatten_patient_data
    EMBED_AVAILABLE = True
    print("Embed functions imported successfully from embed.py")
except ImportError as e:
    print(f"Warning: Embed functions not available: {e}")
    EMBED_AVAILABLE = False
    index_patient_data = None
    flatten_patient_data = None

# Import ingester which should always be available
try:
    from ingester import FHIRIngester
    INGESTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: FHIR ingester not available: {e}")
    INGESTER_AVAILABLE = False

# Try to import Gemini integration
try:
    from gemini_integration import GeminiCopilot
    GEMINI_AVAILABLE = True
    print("Gemini integration imported successfully")
except ImportError as e:
    print(f"Warning: Gemini integration not available: {e}")
    GEMINI_AVAILABLE = False
    GeminiCopilot = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

# Load patient data
def load_patient_data():
    """Load the patient data from JSON file"""
    try:
        with open('patient_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: patient_data.json not found")
        return {}

# Global patient data
patient_data = load_patient_data()

@app.route('/api/patient', methods=['GET'])
def get_patient():
    """Get patient demographic information"""
    try:
        patient_info = patient_data.get('patient', [])
        if patient_info:
            return jsonify(patient_info[0])  # Return first patient
        else:
            # Return default patient structure
            return jsonify({
                "name": "John Doe",
                "gender": "male",
                "birthDate": "1980-01-01",
                "id": "patient-1"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/conditions', methods=['GET'])
def get_conditions():
    """Get patient conditions"""
    try:
        conditions = patient_data.get('conditions', [])
        # Transform to match frontend expectations
        formatted_conditions = [
            {
                "id": f"condition-{i}",
                "name": condition,
                "status": "active",
                "onset": "2023-01-01"
            }
            for i, condition in enumerate(conditions)
        ]
        return jsonify(formatted_conditions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """Get patient medications"""
    try:
        medications = patient_data.get('medications', [])
        # Transform to match frontend expectations
        formatted_medications = [
            {
                "id": f"medication-{i}",
                "name": medication,
                "dosage": "As prescribed",
                "frequency": "Daily"
            }
            for i, medication in enumerate(medications)
        ]
        return jsonify(formatted_medications)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/allergies', methods=['GET'])
def get_allergies():
    """Get patient allergies"""
    try:
        allergies = patient_data.get('allergies', [])
        # Transform to match frontend expectations
        formatted_allergies = [
            {
                "id": f"allergy-{i}",
                "name": allergy,
                "severity": "moderate",
                "reaction": "Unknown"
            }
            for i, allergy in enumerate(allergies)
        ]
        return jsonify(formatted_allergies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/labs', methods=['GET'])
def get_lab_results():
    """Get patient lab results"""
    try:
        observations = patient_data.get('observations', [])
        # Filter for lab-like observations and transform
        formatted_labs = []
        for i, obs in enumerate(observations):
            if any(lab_term in obs.lower() for lab_term in ['glucose', 'cholesterol', 'hemoglobin', 'creatinine', 'potassium']):
                parts = obs.split(':')
                if len(parts) >= 2:
                    formatted_labs.append({
                        "id": f"lab-{i}",
                        "name": parts[0].strip(),
                        "value": parts[1].strip(),
                        "date": "2023-01-01",
                        "status": "final"
                    })
        return jsonify(formatted_labs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vitals', methods=['GET'])
def get_vitals():
    """Get patient vital signs"""
    try:
        observations = patient_data.get('observations', [])
        # Filter for vital signs and transform
        formatted_vitals = []
        for i, obs in enumerate(observations):
            if any(vital_term in obs.lower() for vital_term in ['heart rate', 'blood pressure', 'temperature', 'respiratory rate', 'body mass index']):
                parts = obs.split(':')
                if len(parts) >= 2:
                    formatted_vitals.append({
                        "id": f"vital-{i}",
                        "type": parts[0].strip(),
                        "value": parts[1].strip(),
                        "date": "2023-01-01",
                        "time": "10:00 AM"
                    })
        return jsonify(formatted_vitals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def simple_text_search(query: str, n_results: int = 5):
    """Fallback simple text search when vector search is not available"""
    try:
        query_lower = query.lower()
        results = []
        
        # Search in conditions
        for i, condition in enumerate(patient_data.get('conditions', [])):
            if query_lower in condition.lower():
                results.append({
                    "id": f"condition-{i}",
                    "content": f"Condition: {condition}",
                    "metadata": {"type": "condition"},
                    "similarity": 0.8
                })
        
        # Search in observations
        for i, obs in enumerate(patient_data.get('observations', [])):
            if query_lower in obs.lower():
                results.append({
                    "id": f"observation-{i}",
                    "content": f"Observation: {obs}",
                    "metadata": {"type": "observation"},
                    "similarity": 0.7
                })
        
        # Search in medications
        for i, med in enumerate(patient_data.get('medications', [])):
            if query_lower in med.lower():
                results.append({
                    "id": f"medication-{i}",
                    "content": f"Medication: {med}",
                    "metadata": {"type": "medication"},
                    "similarity": 0.8
                })
        
        # Limit results
        results = results[:n_results]
        
        return jsonify({
            "query": query,
            "results": results,
            "fallback": True,
            "message": "Using simple text search (vector search not available)"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get clinical recommendations based on patient data"""
    try:
        data = request.get_json()
        patient_context = data.get('patient_context', '')
        
        # This is a placeholder for more sophisticated recommendation logic
        # You could integrate with AI models or clinical decision support systems
        recommendations = [
            {
                "id": "rec-1",
                "title": "Regular Blood Pressure Monitoring",
                "description": "Monitor blood pressure daily due to cardiovascular risk factors",
                "priority": "high",
                "category": "monitoring"
            },
            {
                "id": "rec-2", 
                "title": "Medication Adherence Review",
                "description": "Review current medications for interactions and adherence",
                "priority": "medium",
                "category": "medication"
            }
        ]
        
        return jsonify(recommendations)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_fhir', methods=['POST'])
def upload_fhir():
    """Upload FHIR data and process it"""
    try:
        # Get the raw JSON data from the request
        fhir_data = request.get_json(force=True)
        
        if not fhir_data:
            return jsonify({"error": "No FHIR data provided"}), 400
        
        # Validate that it's valid JSON (it should be if we got here)
        if not isinstance(fhir_data, dict):
            return jsonify({"error": "FHIR data must be a valid JSON object"}), 400
        
        print(f"Received FHIR data with keys: {list(fhir_data.keys())}")
        
        # If FHIR ingester is available, use it to process the data
        if INGESTER_AVAILABLE:
            try:
                ingester = FHIRIngester()
                processed_data = ingester.process_fhir_data(fhir_data)
                print(f"FHIR data processed successfully")
                
                # Update the global patient_data
                global patient_data
                patient_data.update(processed_data)
                
                # Index the processed data for searching
                if EMBED_AVAILABLE:
                    try:
                        index_patient_data(processed_data)
                        indexed = True
                        print("Data indexed successfully for search")
                    except Exception as e:
                        print(f"Warning: Could not index data: {e}")
                        indexed = False
                else:
                    indexed = False
                
                return jsonify({
                    "message": "FHIR data uploaded and processed successfully",
                    "processed": True,
                    "indexed": indexed,
                    "patient_id": processed_data.get('patient_id', 'unknown')
                })
            except Exception as e:
                print(f"Error processing FHIR data: {e}")
                # Fall back to storing raw data
                pass
        
        # Fallback: just store the raw FHIR data
        patient_data.update(fhir_data)
        
        # Save to a file for persistence (optional)
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uploaded_fhir_{timestamp}.json"
            
            # Create uploads directory if it doesn't exist
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(exist_ok=True)
            
            with open(uploads_dir / filename, 'w') as f:
                json.dump(fhir_data, f, indent=2)
                
            print(f"FHIR data saved to {filename}")
        except Exception as e:
            print(f"Warning: Could not save FHIR data to file: {e}")
        
        return jsonify({
            "message": "FHIR data uploaded successfully",
            "processed": False,
            "note": "Data stored as-is (FHIR processor not available)"
        })
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        print(f"Error uploading FHIR data: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/search', methods=['POST'])
def search_patient_vector():
    """Search patient data using vector similarity"""
    try:
        if not SEARCH_AVAILABLE:
            return jsonify({"error": "Search functionality not available"}), 503
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query parameter required"}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)
        filter_type = data.get('filter_type', None)
        
        # Check if collection exists
        collection = get_db_collection()
        if not collection:
            return jsonify({"error": "Patient data not indexed. Please upload and process FHIR data first."}), 404
        
        # Perform search
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"type": filter_type} if filter_type else None
        )
        
        # Format results for frontend
        formatted_results = []
        if results["documents"][0]:
            for i, (text, metadata, distance) in enumerate(zip(
                results["documents"][0], 
                results["metadatas"][0],
                results["distances"][0]
            )):
                relevance = 1 - distance
                formatted_results.append({
                    "id": i + 1,
                    "text": text,
                    "type": metadata.get('type', 'unknown'),
                    "relevance": round(relevance, 3),
                    "distance": round(distance, 3)
                })
        
        return jsonify({
            "query": query,
            "results": formatted_results,
            "total_results": len(formatted_results)
        })
        
    except Exception as e:
        print(f"Error searching patient data: {e}")
        return jsonify({"error": f"Search error: {str(e)}"}), 500

@app.route('/api/copilot', methods=['POST'])
def copilot_query():
    """Process query using Gemini AI with patient data context and provide copilot-style response with citations"""
    try:
        if not GEMINI_AVAILABLE:
            return jsonify({"error": "Gemini AI integration not available. Please check your GEMINI_API_KEY environment variable."}), 503
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query parameter required"}), 400
        
        query = data['query']
        n_results = data.get('n_results', 5)  # Number of context documents to retrieve
        filter_type = data.get('filter_type', None)  # Optional filter for specific data types
        
        # Initialize Gemini copilot
        try:
            copilot = GeminiCopilot()
        except ValueError as e:
            return jsonify({"error": str(e)}), 503
        
        # Get context from vector search if available
        context_results = []
        if SEARCH_AVAILABLE:
            try:
                # Check if collection exists
                collection = get_db_collection()
                if collection:
                    context_results = search_patient_data_for_context(query, n_results, filter_type)
                    print(f"Retrieved {len(context_results)} context results for query: {query}")
                else:
                    print("No vector database collection found, using fallback mode")
            except Exception as e:
                print(f"Error retrieving context from vector database: {e}")
        
        # Generate response using Gemini with context
        if context_results:
            # Use context-aware response generation
            response = copilot.generate_copilot_response(query, context_results, patient_data)
        else:
            # Fallback to simple response with basic patient data
            response = copilot.generate_simple_response(query, patient_data)
            response["fallback_reason"] = "Vector search not available or no indexed data found"
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error processing copilot query: {e}")
        return jsonify({
            "error": f"Copilot error: {str(e)}",
            "query": data.get('query', '') if 'data' in locals() else '',
            "answer": "I apologize, but I encountered an error while processing your query. Please try again.",
            "citations": [],
            "context_used": 0,
            "confidence": 0.0
        }), 500

@app.route('/api/index', methods=['POST'])
def index_current_data():
    """Manually trigger indexing of current patient data"""
    try:
        if not EMBED_AVAILABLE:
            return jsonify({"error": "Indexing functionality not available"}), 503
        
        global patient_data
        if not patient_data:
            return jsonify({"error": "No patient data to index"}), 400
        
        # Index the current patient data
        index_patient_data(patient_data)
        
        # Get collection info
        if SEARCH_AVAILABLE:
            collection = get_db_collection()
            count = collection.count() if collection else 0
        else:
            count = "unknown"
        
        return jsonify({
            "message": "Patient data indexed successfully",
            "total_indexed_items": count
        })
        
    except Exception as e:
        print(f"Error indexing patient data: {e}")
        return jsonify({"error": f"Indexing error: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Clinical Copilot API is running"
    })

@app.route('/api/upload-json', methods=['POST'])
def upload_json():
    """Upload JSON data (either file or direct JSON) and process it with automatic indexing"""
    try:
        json_data = None
        
        # Check if it's a file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith('.json'):
                try:
                    content = file.read().decode('utf-8')
                    json_data = json.loads(content)
                    print(f"File upload successful: {file.filename}")
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid JSON format in uploaded file"}), 400
                except Exception as e:
                    return jsonify({"error": f"Error reading file: {str(e)}"}), 400
            else:
                return jsonify({"error": "Please upload a valid JSON file"}), 400
        
        # Check if it's direct JSON data
        elif request.is_json:
            request_data = request.get_json()
            if 'jsonData' in request_data:
                try:
                    json_data = json.loads(request_data['jsonData'])
                    print("Direct JSON upload successful")
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid JSON format in provided data"}), 400
            else:
                json_data = request_data
                print("Direct JSON object upload successful")
        
        else:
            return jsonify({"error": "No JSON data provided. Send either a file upload or JSON data."}), 400
        
        if not json_data:
            return jsonify({"error": "No valid JSON data found"}), 400
        
        # Validate that it's valid JSON object
        if not isinstance(json_data, dict):
            return jsonify({"error": "JSON data must be a valid object"}), 400
        
        print(f"Processing JSON data with keys: {list(json_data.keys())}")
        
        # Process the data using FHIR ingester if available
        processed_data = json_data
        if INGESTER_AVAILABLE:
            try:
                ingester = FHIRIngester()
                processed_data = ingester.process_fhir_data(json_data)
                print("JSON data processed through FHIR ingester successfully")
            except Exception as e:
                print(f"Warning: FHIR processing failed, using raw data: {e}")
                processed_data = json_data
        
        # Update the global patient_data
        global patient_data
        patient_data.update(processed_data)
        
        # Save the processed data to file for persistence
        try:
            with open('patient_data.json', 'w') as f:
                json.dump(processed_data, f, indent=2)
            print("Patient data saved to patient_data.json")
        except Exception as e:
            print(f"Warning: Could not save patient data to file: {e}")
        
        # Automatically index the data for searching
        indexing_success = False
        if EMBED_AVAILABLE:
            try:
                index_patient_data(processed_data)
                indexing_success = True
                print("Data indexed successfully for vector search")
            except Exception as e:
                print(f"Warning: Could not index data for search: {e}")
        
        return jsonify({
            "message": "JSON data uploaded and processed successfully",
            "processed": True,
            "indexed": indexing_success,
            "data_summary": {
                "conditions": len(processed_data.get('conditions', [])),
                "medications": len(processed_data.get('medications', [])),
                "observations": len(processed_data.get('observations', [])),
                "allergies": len(processed_data.get('allergies', [])),
                "patient_info": "patient" in processed_data
            }
        })
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        print(f"Error processing JSON data: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting Clinical Copilot API server...")
    print(f"Patient data loaded: {len(patient_data.get('conditions', []))} conditions, {len(patient_data.get('observations', []))} observations")
    print(f"Vector search available: {VECTOR_SEARCH_AVAILABLE}")
    print(f"Search functions available: {SEARCH_AVAILABLE}")
    print(f"Embed functions available: {EMBED_AVAILABLE}")
    print(f"FHIR ingester available: {INGESTER_AVAILABLE}")
    print(f"Gemini AI available: {GEMINI_AVAILABLE}")
    app.run(debug=True, host='0.0.0.0', port=5000)