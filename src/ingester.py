# fhir_ingester_extended.py
import json
from typing import Dict, List, Any, Set

class FHIRIngester:
    """
    Extended FHIR R4 Bundle ingester.
    Extracts clinically relevant information from key FHIR resources,
    removes duplicates, and outputs a simplified JSON structure.
    """

    def __init__(self):
        self.supported_resources = {
            "Condition": self.extract_condition,
            "Observation": self.extract_observation,
            "MedicationRequest": self.extract_medication_request,
            "Procedure": self.extract_procedure,
            "AllergyIntolerance": self.extract_allergy_intolerance,
            "DiagnosticReport": self.extract_diagnostic_report,
            "Patient": self.extract_patient,
            "Immunization": self.extract_immunization,
            "Encounter": self.extract_encounter,
            "CarePlan": self.extract_careplan,
            "Claim": self.extract_claim
        }

    def extract_all_patient_resources(self, bundle: Dict[str, Any]) -> Dict[str, List[Any]]:
        """
        Iterates through all entries in a FHIR Bundle and extracts simplified resources.
        Uses sets to remove duplicates.
        """
        simplified_data = {
            "conditions": set(),
            "observations": set(),
            "medications": set(),
            "procedures": set(),
            "allergies": set(),
            "diagnostic_reports": set(),
            "immunizations": set(),
            "encounters": set(),
            "careplans": set(),
            "claims_diagnoses": set(),
            "patient": []
        }

        entries = bundle.get("entry", [])
        for entry in entries:
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")
            if resource_type in self.supported_resources:
                try:
                    simplified = self.supported_resources[resource_type](resource)
                    if simplified:
                        key = self.map_resource_to_key(resource_type)
                        # Handle patient separately (list)
                        if key == "patient":
                            simplified_data[key].append(simplified)
                        # For other types, use sets to deduplicate
                        elif isinstance(simplified, (str, tuple)):
                            simplified_data[key].add(simplified)
                        elif isinstance(simplified, list):
                            simplified_data[key].update(simplified)
                        else:
                            simplified_data[key].add(tuple(simplified.items()))
                except Exception as e:
                    print(f"Warning: Failed to extract {resource_type}: {e}")
            else:
                continue

        # Convert sets back to lists for JSON serialization
        for k, v in simplified_data.items():
            if isinstance(v, set):
                # Convert tuple back to dict if needed
                new_list = []
                for item in v:
                    if isinstance(item, tuple):
                        new_list.append(dict(item))
                    else:
                        new_list.append(item)
                simplified_data[k] = new_list

        return simplified_data

    def process_fhir_data(self, fhir_data: Dict[str, Any]) -> Dict[str, List[Any]]:
        """
        Process FHIR data - handles both Bundle format and pre-processed format.
        """
        # Check if this is already processed data (has our expected keys)
        expected_keys = {"conditions", "observations", "medications", "procedures", "allergies"}
        if any(key in fhir_data for key in expected_keys):
            # Data is already in simplified format, return as-is
            return fhir_data
        
        # Check if this is a FHIR Bundle
        if "entry" in fhir_data and isinstance(fhir_data["entry"], list):
            return self.extract_all_patient_resources(fhir_data)
        
        # If it's neither, try to treat it as a bundle anyway
        return self.extract_all_patient_resources(fhir_data)

    @staticmethod
    def map_resource_to_key(resource_type: str) -> str:
        mapping = {
            "Condition": "conditions",
            "Observation": "observations",
            "MedicationRequest": "medications",
            "Procedure": "procedures",
            "AllergyIntolerance": "allergies",
            "DiagnosticReport": "diagnostic_reports",
            "Patient": "patient",
            "Immunization": "immunizations",
            "Encounter": "encounters",
            "CarePlan": "careplans",
            "Claim": "claims_diagnoses"
        }
        return mapping.get(resource_type, "unknown")

    # ------------------- Resource-specific extractors -------------------

    def extract_condition(self, resource: Dict[str, Any]) -> str:
        code = resource.get("code", {}).get("text")
        return code

    def extract_observation(self, resource: Dict[str, Any]) -> str:
        # Keep value and unit for uniqueness
        value = None
        unit = None
        if "valueQuantity" in resource:
            value = resource["valueQuantity"].get("value")
            unit = resource["valueQuantity"].get("unit")
        elif "valueString" in resource:
            value = resource.get("valueString")
        elif "valueCodeableConcept" in resource:
            value = resource["valueCodeableConcept"].get("text")
        code = resource.get("code", {}).get("text")
        if value:
            return f"{code}: {value} {unit if unit else ''}".strip()
        return code

    def extract_medication_request(self, resource: Dict[str, Any]) -> str:
        med = resource.get("medicationCodeableConcept", {}).get("text")
        return med

    def extract_procedure(self, resource: Dict[str, Any]) -> str:
        return resource.get("code", {}).get("text")

    def extract_allergy_intolerance(self, resource: Dict[str, Any]) -> str:
        return resource.get("code", {}).get("text")

    def extract_diagnostic_report(self, resource: Dict[str, Any]) -> str:
        return resource.get("code", {}).get("text")

    def extract_patient(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        name_obj = resource.get("name", [{}])[0]
        name = None
        if name_obj:
            name = " ".join(name_obj.get("given", []) + [name_obj.get("family", "")])
        return {"name": name, "gender": resource.get("gender"), "birthDate": resource.get("birthDate")}

    def extract_immunization(self, resource: Dict[str, Any]) -> str:
        return resource.get("vaccineCode", {}).get("text")

    def extract_encounter(self, resource: Dict[str, Any]) -> str:
        # Keep encounter type as unique identifier
        type_text = resource.get("type", [{}])[0].get("text")
        return type_text

    def extract_careplan(self, resource: Dict[str, Any]) -> str:
        # Keep only the summary or title
        return resource.get("description") or resource.get("title") # type: ignore

    def extract_claim(self, resource: Dict[str, Any]) -> List[str]:
        # Extract diagnoses from claim items
        diagnoses = set()
        for item in resource.get("diagnosis", []):
            code = item.get("diagnosisCodeableConcept", {}).get("text")
            if code:
                diagnoses.add(code)
        return list(diagnoses)


def extract_patient_data(file_path: str) -> Dict[str, Any]:
    """
    Extract patient data from a FHIR bundle file
    
    Args:
        file_path: Path to the FHIR bundle JSON file
        
    Returns:
        Dictionary containing extracted patient data
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            bundle = json.load(f)
            
        ingester = FHIRIngester()
        simplified_data = ingester.extract_all_patient_resources(bundle)
        
        # Extract patient ID from the bundle
        patient_id = None
        entries = bundle.get("entry", [])
        for entry in entries:
            resource = entry.get("resource", {})
            if resource.get("resourceType") == "Patient":
                patient_id = resource.get("id")
                break
        
        # Add the patient ID to the simplified data
        if patient_id:
            simplified_data["patient_id"] = patient_id
            
        return simplified_data
    except Exception as e:
        print(f"Error extracting data from {file_path}: {str(e)}")
        return {}

def process_fhir_directory(fhir_dir: str, output_dir: str) -> None:
    """
    Process all FHIR files in a directory and create individual JSON files
    
    Args:
        fhir_dir: Path to the directory containing FHIR JSON files
        output_dir: Path to the directory where individual patient files will be saved
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all JSON files in the FHIR directory
    fhir_files = [os.path.join(fhir_dir, f) for f in os.listdir(fhir_dir) 
                 if f.endswith('.json') and os.path.isfile(os.path.join(fhir_dir, f))]
    
    print(f"Found {len(fhir_files)} FHIR files to process.")
    
    # Process each file
    for i, file_path in enumerate(fhir_files):
        try:
            # Extract the patient name from the filename (assuming format like "Name_Surname_ID.json")
            file_name = os.path.basename(file_path)
            name_parts = file_name.split('_')
            if len(name_parts) >= 2:
                patient_name = f"{name_parts[0]}_{name_parts[1]}"
            else:
                patient_name = f"patient_{i}"
            
            # Extract the data
            patient_data = extract_patient_data(file_path)
            
            if not patient_data:
                print(f"Skipping {file_name} due to extraction errors.")
                continue
                
            # Create output file path
            patient_id = patient_data.get("patient_id", f"unknown_{i}")
            output_file = os.path.join(output_dir, f"{patient_name}_{patient_id}.json")
            
            # Save the data
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(patient_data, f, indent=2)
                
            if i % 10 == 0:
                print(f"Processed {i+1}/{len(fhir_files)} files...")
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Completed. Processed {len(fhir_files)} files. Results saved to {output_dir}")

if __name__ == "__main__":
    import os
    import sys
    
    # Default paths
    fhir_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fhir"))
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "patient_data"))
    
    # Check command line arguments
    if len(sys.argv) > 1:
        fhir_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print(f"Processing FHIR files from: {fhir_dir}")
    print(f"Saving patient data to: {output_dir}")
    
    # Process the files
    process_fhir_directory(fhir_dir, output_dir)

