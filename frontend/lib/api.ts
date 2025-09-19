// api.ts
import { Patient, Condition, Medication, Allergy, LabResult, Vital } from "./types"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000/api" // Python Flask backend URL

export async function fetchPatient(): Promise<Patient> {
    const res = await fetch(`${API_BASE}/patient`)
    return res.json()
}

export async function fetchConditions(): Promise<Condition[]> {
    const res = await fetch(`${API_BASE}/conditions`)
    return res.json()
}

export async function fetchMedications(): Promise<Medication[]> {
    const res = await fetch(`${API_BASE}/medications`)
    return res.json()
}

export async function fetchAllergies(): Promise<Allergy[]> {
    const res = await fetch(`${API_BASE}/allergies`)
    return res.json()
}

export async function fetchLabResults(): Promise<LabResult[]> {
    const res = await fetch(`${API_BASE}/labs`)
    return res.json()
}

export async function fetchVitals(): Promise<Vital[]> {
    const res = await fetch(`${API_BASE}/vitals`)
    return res.json()
}

// New API functions for Clinical Copilot features

export interface SearchResult {
    id: string
    content: string
    metadata: Record<string, any>
    similarity: number
}

export interface SearchResponse {
    query: string
    results: SearchResult[]
}

export interface Recommendation {
    id: string
    title: string
    description: string
    priority: 'high' | 'medium' | 'low'
    category: string
}

export async function searchPatientData(
    query: string,
    nResults: number = 5,
    filterType?: string
): Promise<SearchResponse> {
    const res = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query,
            n_results: nResults,
            filter_type: filterType
        })
    })
    
    if (!res.ok) {
        throw new Error(`Search failed: ${res.statusText}`)
    }
    
    return res.json()
}

export async function getRecommendations(patientContext: string): Promise<Recommendation[]> {
    const res = await fetch(`${API_BASE}/recommendations`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            patient_context: patientContext
        })
    })
    
    if (!res.ok) {
        throw new Error(`Recommendations failed: ${res.statusText}`)
    }
    
    return res.json()
}

export async function healthCheck(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/health`)
    return res.json()
}
