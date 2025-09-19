"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Navigation } from "@/components/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Upload, FileJson, CheckCircle, ArrowRight, Brain } from "lucide-react"
import { Textarea } from "@/components/ui/textarea"

export default function PatientsPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fhirData, setFhirData] = useState("")
  const [isUploading, setIsUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [uploadMethod, setUploadMethod] = useState<'file' | 'text'>('file')
  const router = useRouter()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File select triggered')
    const file = event.target.files?.[0]
    console.log('Selected file:', file)
    
    if (file) {
      console.log('File type:', file.type)
      console.log('File name:', file.name)
      
      // Accept both application/json and files with .json extension
      if (file.type === "application/json" || file.name.toLowerCase().endsWith('.json')) {
        setSelectedFile(file)
        setUploadSuccess(false)
        console.log('File accepted')
      } else {
        console.log('File rejected - not JSON')
        alert("Please select a valid JSON file (.json extension)")
      }
    } else {
      console.log('No file selected')
    }
  }

  const handleFileUpload = async () => {
    console.log('Upload button clicked')
    console.log('Selected file:', selectedFile)
    
    if (!selectedFile) {
      alert("Please select a JSON file first")
      return
    }

    setIsUploading(true)
    console.log('Starting upload...')
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      console.log('Sending request to:', "http://127.0.0.1:5000/api/upload-json")
      
      const response = await fetch("http://127.0.0.1:5000/api/upload-json", {
        method: "POST",
        body: formData,
      })

      console.log('Response status:', response.status)
      console.log('Response ok:', response.ok)

      if (!response.ok) {
        const errorData = await response.json()
        console.error('Upload error:', errorData)
        throw new Error(errorData.error || `Server error: ${response.status}`)
      }
      
      const result = await response.json()
      console.log("Upload successful:", result)
      setUploadSuccess(true)
      
    } catch (error) {
      console.error("Upload error:", error)
      alert("Error uploading file: " + (error as Error).message)
    } finally {
      setIsUploading(false)
      console.log('Upload finished')
    }
  }

  const handleTextUpload = async () => {
    if (!fhirData.trim()) {
      alert("Please paste JSON data")
      return
    }

    setIsUploading(true)
    try {
      // Validate JSON format
      JSON.parse(fhirData)
      
      const response = await fetch("http://127.0.0.1:5000/api/upload-json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonData: fhirData }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Server error: ${response.status}`)
      }
      
      const result = await response.json()
      console.log("Upload successful:", result)
      setUploadSuccess(true)
      setFhirData("")
      
    } catch (error) {
      console.error("Upload error:", error)
      if (error instanceof SyntaxError) {
        alert("Invalid JSON format. Please check your data.")
      } else {
        alert("Error uploading data: " + (error as Error).message)
      }
    } finally {
      setIsUploading(false)
    }
  }

  const handleNavigateToCopilot = () => {
    router.push(`/copilot`)
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Clinical Data Upload</h1>
          <p className="text-muted-foreground">
            Upload your patient JSON data to begin analysis and enable AI-powered clinical insights
          </p>
        </div>

        {!uploadSuccess ? (
          <div className="max-w-2xl mx-auto space-y-6">
            {/* Upload Method Selection */}
            <Card>
              <CardHeader>
                <CardTitle>Select Upload Method</CardTitle>
                <CardDescription>
                  Choose how you'd like to upload your patient data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Button 
                    variant={uploadMethod === 'file' ? 'default' : 'outline'}
                    onClick={() => {
                      console.log('Setting upload method to file')
                      setUploadMethod('file')
                    }}
                    className="flex-1"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Upload File
                  </Button>
                  <Button 
                    variant={uploadMethod === 'text' ? 'default' : 'outline'}
                    onClick={() => {
                      console.log('Setting upload method to text')
                      setUploadMethod('text')
                    }}
                    className="flex-1"
                  >
                    <FileJson className="w-4 h-4 mr-2" />
                    Paste JSON
                  </Button>
                </div>
                
                <div className="text-sm text-center text-muted-foreground">
                  Current method: {uploadMethod}
                </div>
              </CardContent>
            </Card>

            {uploadMethod === 'file' ? (
              /* File Upload */
              <Card>
                <CardHeader>
                  <CardTitle>Upload JSON File</CardTitle>
                  <CardDescription>
                    Select a JSON file containing your patient data
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="border-2 border-dashed border-border rounded-lg p-12 text-center hover:border-primary/50 transition-colors">
                    <FileJson className="w-16 h-16 mx-auto text-muted-foreground mb-6" />
                    <div className="space-y-4">
                      <p className="text-lg font-medium text-foreground">
                        Upload JSON File
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Click the button below to select your JSON file
                      </p>
                      
                      <div className="flex justify-center">
                        <label htmlFor="file-upload" className="cursor-pointer">
                          <Button 
                            variant="outline" 
                            className="relative" 
                            type="button"
                            onClick={() => {
                              console.log('Choose File button clicked')
                              // Trigger the file input
                              document.getElementById('file-upload')?.click()
                            }}
                          >
                            <Upload className="w-4 h-4 mr-2" />
                            Choose File
                          </Button>
                        </label>
                        <input
                          id="file-upload"
                          type="file"
                          accept=".json,application/json"
                          onChange={handleFileSelect}
                          className="hidden"
                          onClick={() => console.log('File input clicked')}
                        />
                      </div>
                      
                      {!selectedFile && (
                        <p className="text-xs text-muted-foreground">
                          No file chosen
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {selectedFile && (
                    <div className="p-4 bg-muted rounded-lg text-center">
                      <p className="text-sm font-medium">Selected file:</p>
                      <p className="text-sm text-muted-foreground">{selectedFile.name}</p>
                      <p className="text-xs text-muted-foreground">
                        Size: {(selectedFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  )}
                  
                  <div className="flex justify-center">
                    <Button 
                      onClick={handleFileUpload} 
                      disabled={!selectedFile || isUploading}
                      className="w-full max-w-sm"
                      size="lg"
                    >
                      {isUploading ? "Uploading and Indexing..." : "Upload and Index Data"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : (
              /* Text Upload */
              <Card>
                <CardHeader>
                  <CardTitle>Paste JSON Data</CardTitle>
                  <CardDescription>
                    Paste your patient JSON data directly
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Textarea
                    placeholder="Paste your JSON data here..."
                    value={fhirData}
                    onChange={(e) => setFhirData(e.target.value)}
                    rows={12}
                    className="font-mono text-sm"
                  />
                  <div className="flex justify-center">
                    <Button 
                      onClick={handleTextUpload} 
                      disabled={!fhirData.trim() || isUploading}
                      className="w-full max-w-xs"
                    >
                      {isUploading ? "Uploading and Indexing..." : "Upload and Index Data"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          /* Success State */
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardContent className="text-center py-12">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold mb-2">Data Uploaded Successfully!</h2>
                <p className="text-muted-foreground mb-6">
                  Your patient data has been uploaded and indexed. You can now use the AI copilot to search and analyze the data.
                </p>
                <Button onClick={handleNavigateToCopilot} size="lg">
                  <Brain className="w-4 h-4 mr-2" />
                  Open AI Copilot
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

