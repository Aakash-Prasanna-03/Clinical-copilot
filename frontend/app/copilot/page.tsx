"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Brain, Search, FileText, ArrowLeft, User } from "lucide-react"
import { useRouter } from "next/navigation"

interface SearchResult {
  id: number
  text: string
  type: string
  relevance: number
  distance: number
}

interface Citation {
  id: number
  text: string
  type: string
  relevance: number
  source: string
  metadata?: any
}

interface CopilotResponse {
  query: string
  answer: string
  citations: Citation[]
  context_used: number
  confidence: number
  response_metadata: {
    model: string
    temperature: number
    context_sources: string[]
  }
  error?: string
}

export default function CopilotPage() {
  const [query, setQuery] = useState("")
  const [isSearching, setIsSearching] = useState(false)
  const [copilotResponse, setCopilotResponse] = useState<CopilotResponse | null>(null)
  const [searchError, setSearchError] = useState("")
  const [hasSearched, setHasSearched] = useState(false)
  const router = useRouter()

  const handleSearch = async () => {
    if (!query.trim()) {
      alert("Please enter a search query")
      return
    }

    setIsSearching(true)
    setSearchError("")
    
    try {
      const response = await fetch("http://127.0.0.1:5000/api/copilot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: query,
          n_results: 5 
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `Server error: ${response.status}`)
      }
      
      const result: CopilotResponse = await response.json()
      
      setCopilotResponse(result)
      setHasSearched(true)
      
    } catch (error) {
      console.error("Copilot error:", error)
      setSearchError((error as Error).message)
      setCopilotResponse(null)
      setHasSearched(true)
    } finally {
      setIsSearching(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isSearching) {
      handleSearch()
    }
  }

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'condition': return "bg-red-100 text-red-800 border-red-200"
      case 'medication': return "bg-blue-100 text-blue-800 border-blue-200"
      case 'observation': return "bg-green-100 text-green-800 border-green-200"
      case 'procedure': return "bg-purple-100 text-purple-800 border-purple-200"
      case 'patient': return "bg-yellow-100 text-yellow-800 border-yellow-200"
      default: return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 0.8) return "text-green-600 font-medium"
    if (relevance >= 0.6) return "text-yellow-600 font-medium"
    return "text-red-600 font-medium"
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <Button
              variant="ghost"
              onClick={() => router.push('/patients')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Upload
            </Button>
            
            {/* Patient Profile Card */}
            <Card className="border-primary/30 bg-gradient-to-r from-primary/10 to-primary/5 shadow-md min-w-[280px]">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary/20 rounded-lg">
                    <User className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-foreground">Abdul218 Harris789</h3>
                    <div className="flex flex-col text-sm text-muted-foreground mt-1">
                      <span>Male • 72 years old</span>
                      <span>DOB: Dec 05, 1952</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-8 h-8 text-primary" />
            <h1 className="text-3xl font-bold">AI Clinical Copilot</h1>
          </div>
          <p className="text-muted-foreground">
            Search your uploaded patient data using natural language queries
          </p>
        </div>

        {/* Search Interface */}
        <Card className="mb-6 shadow-lg border-0">
          <CardHeader className="bg-gradient-to-r from-slate-900 to-slate-700 text-white">
            <CardTitle className="flex items-center gap-3 text-xl">
              <div className="p-2 bg-white/20 rounded-full">
                <Brain className="w-6 h-6" />
              </div>
              Clinical AI Copilot
            </CardTitle>
            <CardDescription className="text-slate-200 mt-2">
              Ask questions about patient data and get AI-powered clinical insights with evidence-based citations
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 bg-gradient-to-b from-white to-slate-50 space-y-4">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  placeholder="e.g., 'Will the patient survive? Analyze their prognosis' or 'What are the clinical considerations?'"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-12 h-12 text-lg border-2 border-gray-200 focus:border-blue-500 transition-colors"
                  disabled={isSearching}
                />
              </div>
              <Button 
                onClick={handleSearch} 
                disabled={!query.trim() || isSearching}
                className="h-12 px-8 bg-blue-600 hover:bg-blue-700 text-white font-semibold"
              >
                {isSearching ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4 mr-2" />
                    Analyze
                  </>
                )}
              </Button>
            </div>
            
            {/* Example Queries */}
            <div className="border-t border-gray-200 pt-4">
              <div className="flex flex-wrap gap-2 items-center">
                <span className="text-sm text-gray-600 font-medium">Quick Start:</span>
                {[
                  "Will the patient survive? Analyze the prognosis",
                  "What are the risk factors for this patient?",
                  "Analyze the patient's current health status",
                  "What clinical considerations should be noted?"
                ].map((example) => (
                  <Button
                    key={example}
                    variant="outline"
                    size="sm"
                    onClick={() => setQuery(example)}
                    disabled={isSearching}
                    className="text-xs hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  >
                    {example.length > 40 ? example.substring(0, 37) + "..." : example}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Copilot Response */}
        {hasSearched && (
          <Card className="shadow-lg border-0">
            <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-3 text-xl">
                <div className="p-2 bg-white/20 rounded-full">
                  <Brain className="w-6 h-6" />
                </div>
                Clinical AI Assistant
                {copilotResponse && (
                  <div className="ml-auto flex items-center gap-2 text-sm bg-white/20 px-3 py-1 rounded-full">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    Analysis Complete
                  </div>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {searchError ? (
                <div className="text-center py-12">
                  <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                    <Brain className="w-8 h-8 text-red-600" />
                  </div>
                  <div className="text-red-800 font-semibold text-lg mb-2">Analysis Error</div>
                  <p className="text-red-600 mb-6 max-w-md mx-auto">{searchError}</p>
                  <div className="flex gap-3 justify-center">
                    <Button 
                      variant="outline" 
                      onClick={() => router.push('/patients')} 
                      className="border-red-200 text-red-700 hover:bg-red-50"
                    >
                      Upload Patient Data
                    </Button>
                    <Button 
                      onClick={() => {setSearchError(''); setHasSearched(false);}}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      Try Again
                    </Button>
                  </div>
                </div>
              ) : !copilotResponse ? (
                <div className="text-center py-12">
                  <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <Brain className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-gray-600 text-lg mb-2">No analysis available</p>
                  <p className="text-gray-500 max-w-md mx-auto mb-6">
                    The AI couldn't generate a response. This might be due to insufficient data or connectivity issues.
                  </p>
                  <Button 
                    onClick={() => router.push('/patients')}
                    variant="outline"
                  >
                    Check Patient Data
                  </Button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* AI Generated Answer */}
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200 shadow-sm">
                    <div className="flex items-center gap-2 mb-4">
                      <Brain className="w-5 h-5 text-blue-600" />
                      <h3 className="font-semibold text-blue-900 text-lg">AI Clinical Analysis</h3>
                    </div>
                    <div className="prose prose-blue max-w-none">
                      <div className="text-gray-800 leading-relaxed whitespace-pre-wrap text-base">
                        {copilotResponse.answer}
                      </div>
                    </div>
                    
                    {/* Context Indicator */}
                    <div className="mt-4 pt-4 border-t border-blue-200 flex items-center justify-between text-sm">
                      <div className="flex items-center gap-4">
                        <div className="text-blue-600">
                          <span className="font-medium">Sources:</span> {copilotResponse.context_used} documents
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Citations */}
                  {copilotResponse.citations && copilotResponse.citations.length > 0 && (
                    <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                      <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2 text-lg">
                        <FileText className="w-5 h-5 text-gray-600" />
                        Supporting Evidence 
                        <Badge variant="secondary" className="ml-2">
                          {copilotResponse.citations.length} {copilotResponse.citations.length === 1 ? 'source' : 'sources'}
                        </Badge>
                      </h3>
                      <div className="grid gap-4">
                        {copilotResponse.citations.map((citation) => (
                          <div key={citation.id} className="bg-gray-50 rounded-lg p-4 border-l-4 border-l-blue-500 hover:bg-gray-100 transition-colors">
                            <div className="flex items-start gap-4">
                              <div className="p-2 bg-white rounded-full shadow-sm">
                                <FileText className="h-4 w-4 text-blue-600" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-2 flex-wrap">
                                  <Badge variant="outline" className={`${getTypeColor(citation.type)} font-medium`}>
                                    {citation.type.charAt(0).toUpperCase() + citation.type.slice(1)}
                                  </Badge>
                                </div>
                                <p className="text-gray-800 leading-relaxed font-medium mb-2">{citation.text}</p>
                                <p className="text-xs text-gray-500 bg-white px-2 py-1 rounded inline-block">
                                  {citation.source}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Metadata */}
                  {copilotResponse.response_metadata && (
                    <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
                      <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                        <Brain className="w-4 h-4 text-slate-600" />
                        Analysis Details
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-white p-3 rounded-lg">
                          <div className="text-slate-600 text-sm font-medium mb-1">AI Model</div>
                          <div className="text-slate-900 font-semibold">
                            {copilotResponse.response_metadata.model}
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded-lg">
                          <div className="text-slate-600 text-sm font-medium mb-1">Context Documents</div>
                          <div className="text-slate-900 font-semibold">
                            {copilotResponse.context_used} documents analyzed
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded-lg">
                          <div className="text-slate-600 text-sm font-medium mb-1">Response Temperature</div>
                          <div className="text-slate-900 font-semibold">
                            {copilotResponse.response_metadata.temperature} (clinical precision)
                          </div>
                        </div>
                      </div>
                      {copilotResponse.response_metadata.context_sources && (
                        <div className="mt-4 pt-3 border-t border-slate-200">
                          <div className="text-slate-600 text-sm font-medium mb-2">Data Sources Analyzed</div>
                          <div className="flex gap-2 flex-wrap">
                            {copilotResponse.response_metadata.context_sources.map((source, idx) => (
                              <Badge key={idx} variant="secondary" className="bg-blue-100 text-blue-800 border-blue-200">
                                {source.charAt(0).toUpperCase() + source.slice(1)}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}