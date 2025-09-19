// types.ts
export interface Patient {
    id: string
    name: string
    gender: string
    birthDate: string
    age?: number
    mrn?: string
    dob?: string
    phone?: string
    address?: string
    emergencyContact?: string
}

export interface Condition {
    id: string
    name: string
    status: string
    onset: string
}

export interface Medication {
    id: string
    name: string
    dosage: string
    frequency: string
    dose?: string
}

export interface Allergy {
    id: string
    name: string
    severity: string
    reaction: string
}

export interface LabResult {
    id: string
    name: string
    value: string
    date: string
    status: string
    test?: string
}

export interface Vital {
    id: string
    type: string
    value: string
    date: string
    time: string
    systolic?: number
    heartRate?: number
}
