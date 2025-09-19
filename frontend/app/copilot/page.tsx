"use client"

import { useState, useEffect } from "react"
import { Navigation } from "@/components/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Brain, Search, FileText, ArrowLeft, User, Activity, Heart } from "lucide-react"
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
  const [patientData, setPatientData] = useState<any>(null)
  const [currentPatient, setCurrentPatient] = useState<string>("Unknown Patient")
  const [currentPatientId, setCurrentPatientId] = useState<string>("")
  const router = useRouter()

  // Fetch current patient data on component mount
  useEffect(() => {
    const fetchPatientData = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/patient")
        if (response.ok) {
          const patient = await response.json()
          setPatientData(patient)
          if (patient.name) {
            setCurrentPatient(patient.name)
          } else if (patient.id) {
            setCurrentPatient(patient.id)
          }
          
          // Set the patient_id directly from the response
          if (patient.patient_id) {
            setCurrentPatientId(patient.patient_id)
            console.log("Using patient_id:", patient.patient_id)
          } else {
            console.warn("No patient_id found in response:", patient)
          }
        }
      } catch (error) {
        console.error("Error fetching patient data:", error)
      }
    }
    
    fetchPatientData()
  }, [])

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
          n_results: 5,
          patient_id: currentPatientId || undefined
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
      case 'condition': return "bg-gradient-to-r from-red-100 to-red-50 dark:from-red-950/50 dark:to-red-900/50 text-red-800 dark:text-red-200 border-red-200 dark:border-red-800 shadow-sm"
      case 'medication': return "bg-gradient-to-r from-blue-100 to-blue-50 dark:from-blue-950/50 dark:to-blue-900/50 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-800 shadow-sm"
      case 'observation': return "bg-gradient-to-r from-emerald-100 to-emerald-50 dark:from-emerald-950/50 dark:to-emerald-900/50 text-emerald-800 dark:text-emerald-200 border-emerald-200 dark:border-emerald-800 shadow-sm"
      case 'procedure': return "bg-gradient-to-r from-purple-100 to-purple-50 dark:from-purple-950/50 dark:to-purple-900/50 text-purple-800 dark:text-purple-200 border-purple-200 dark:border-purple-800 shadow-sm"
      case 'patient': return "bg-gradient-to-r from-amber-100 to-amber-50 dark:from-amber-950/50 dark:to-amber-900/50 text-amber-800 dark:text-amber-200 border-amber-200 dark:border-amber-800 shadow-sm"
      default: return "bg-gradient-to-r from-muted to-muted/50 text-muted-foreground border-border shadow-sm"
    }
  }

  const getRelevanceColor = (relevance: number) => {
    if (relevance >= 0.8) return "text-emerald-700 dark:text-emerald-300 font-semibold bg-emerald-50 dark:bg-emerald-950/50 px-3 py-1 rounded-full border border-emerald-200 dark:border-emerald-800"
    if (relevance >= 0.6) return "text-amber-700 dark:text-amber-300 font-semibold bg-amber-50 dark:bg-amber-950/50 px-3 py-1 rounded-full border border-amber-200 dark:border-amber-800"
    return "text-red-700 dark:text-red-300 font-semibold bg-red-50 dark:bg-red-950/50 px-3 py-1 rounded-full border border-red-200 dark:border-red-800"
  }

  // Function to clean markdown formatting
  const cleanMarkdownText = (text: string): string => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove **bold** formatting
      .replace(/\*(.*?)\*/g, '$1')     // Remove *italic* formatting
      .replace(/__(.*?)__/g, '$1')     // Remove __bold__ formatting
      .replace(/_(.*?)_/g, '$1')       // Remove _italic_ formatting
      .replace(/`(.*?)`/g, '$1')       // Remove `code` formatting
      .trim()
  }

  // Function to get unique top citations (limit duplicates)
  const getTopUniqueCitations = (citations: Citation[], limit: number = 3): Citation[] => {
    const uniqueCitations: Citation[] = []
    const seenTexts = new Set<string>()
    
    for (const citation of citations) {
      const cleanText = cleanMarkdownText(citation.text.toLowerCase().trim())
      if (!seenTexts.has(cleanText) && uniqueCitations.length < limit) {
        seenTexts.add(cleanText)
        uniqueCitations.push({
          ...citation,
          text: cleanMarkdownText(citation.text)
        })
      }
    }
    
    return uniqueCitations
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/20 to-accent/10 dark:from-background dark:via-background/50 dark:to-muted/10">
      <Navigation />
      
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between mb-6 gap-4">
            <Button
              variant="ghost"
              onClick={() => router.push('/patients')}
              className="flex items-center gap-2 hover:bg-muted transition-all duration-200 hover:scale-105 self-start glass"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Upload
            </Button>
            
            {/* Enhanced Patient Profile Card */}
            <Card className="border-primary/20 medical-card-gradient shadow-xl hover:shadow-2xl transition-all duration-300 w-full lg:w-auto max-w-md lg:max-w-none lg:min-w-[320px] card-hover">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-gradient-to-br from-primary to-blue-600 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                    <User className="h-7 w-7 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-xl text-foreground truncate">
                      {patientData?.name || currentPatient}
                    </h3>
                    <div className="flex flex-col text-sm text-muted-foreground mt-2 space-y-1">
                      <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary flex-shrink-0" />
                        <span className="font-medium">
                          {patientData?.gender || "Unknown"} • 
                          {patientData?.birthDate 
                            ? ` ${new Date().getFullYear() - new Date(patientData.birthDate).getFullYear()} years old`
                            : " Age unknown"
                          }
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Heart className="w-4 h-4 text-red-500 flex-shrink-0" />
                        <span>DOB: {patientData?.birthDate || "Unknown"}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-4">
            <div className="p-3 bg-gradient-to-br from-primary to-blue-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110">
              <Brain className="w-10 h-10 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
                AI Clinical Copilot
              </h1>
              <p className="text-muted-foreground text-lg font-medium mt-1">
                Advanced medical intelligence at your fingertips
              </p>
            </div>
          </div>
        </div>

        {/* Enhanced Search Interface */}
        <Card className="mb-8 shadow-2xl border-0 overflow-hidden card-interactive">
          <CardHeader className="bg-gradient-to-r from-primary via-blue-600 to-indigo-600 text-white relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 animate-pulse-soft"></div>
            <CardTitle className="flex items-center gap-4 text-2xl relative z-10">
              <div className="p-3 bg-white/20 backdrop-blur rounded-xl hover:bg-white/30 transition-colors">
                <Brain className="w-7 h-7" />
              </div>
              <div>
                <div className="text-2xl font-bold">Clinical AI Assistant</div>
                <div className="text-blue-100 text-sm font-normal mt-1">Powered by advanced medical AI</div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6 lg:p-8 medical-card-gradient">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-6 w-6 text-muted-foreground" />
                <Input
                  placeholder="Ask about patient condition, prognosis, risk factors, or treatment considerations..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="pl-14 h-12 lg:h-14 text-base lg:text-lg border-2 border-border focus:border-primary focus:ring-4 focus:ring-primary/20 rounded-xl shadow-sm transition-all duration-300 hover:border-primary/50 bg-background"
                  disabled={isSearching}
                />
              </div>
              <Button 
                onClick={handleSearch} 
                disabled={!query.trim() || isSearching}
                className="h-12 lg:h-14 px-6 lg:px-10 btn-primary text-white font-bold rounded-xl shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSearching ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-3"></div>
                    <span className="hidden sm:inline">Analyzing...</span>
                    <span className="sm:hidden">...</span>
                  </>
                ) : (
                  <>
                    <Brain className="w-5 h-5 mr-2 lg:mr-3" />
                    <span className="hidden sm:inline">Analyze</span>
                    <span className="sm:hidden">Go</span>
                  </>
                )}
              </Button>
            </div>
            
            {/* Enhanced Example Queries */}
            <div className="border-t border-border pt-6 mt-6">
              <div className="flex flex-wrap gap-2 lg:gap-3 items-start">
                <span className="text-foreground font-semibold text-sm mb-2 w-full lg:w-auto">Quick Examples:</span>
                <div className="flex flex-wrap gap-2 lg:gap-3">
                  {[
                    "Will the patient survive? Analyze prognosis",
                    "What are the key risk factors?",
                    "Analyze current health status",
                    "Treatment recommendations?"
                  ].map((example) => (
                    <Button
                      key={example}
                      variant="outline"
                      size="sm"
                      onClick={() => setQuery(example)}
                      disabled={isSearching}
                      className="text-xs lg:text-sm hover:bg-primary/10 hover:border-primary/50 hover:text-primary transition-all duration-300 rounded-lg border-border shadow-sm hover:shadow-md card-hover disabled:hover:scale-100 interactive-hover"
                    >
                      {example}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Copilot Response */}
        {hasSearched && (
          <Card className="shadow-2xl border-0 overflow-hidden card-interactive backdrop-blur-sm">
            <CardHeader className="bg-gradient-to-r from-emerald-600 via-teal-600 to-blue-600 text-white relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-400/30 via-teal-400/20 to-blue-400/30 animate-pulse-soft"></div>
              <div className="absolute top-0 left-0 w-full h-full">
                <div className="absolute top-2 left-2 w-3 h-3 bg-white/30 rounded-full animate-ping"></div>
                <div className="absolute top-6 right-8 w-2 h-2 bg-white/20 rounded-full animate-pulse"></div>
                <div className="absolute bottom-4 left-8 w-4 h-4 bg-white/20 rounded-full animate-bounce" style={{animationDelay: '0.5s'}}></div>
              </div>
              <CardTitle className="flex items-center gap-4 text-2xl relative z-10">
                <div className="p-4 bg-white/25 backdrop-blur-sm rounded-2xl hover:bg-white/35 transition-all duration-300 shadow-lg hover:shadow-xl">
                  <Brain className="w-8 h-8 drop-shadow-sm" />
                </div>
                <div className="flex-1">
                  <div className="text-3xl font-bold mb-1 tracking-tight drop-shadow-sm">Clinical Analysis Results</div>
                  {copilotResponse && (
                    <div className="flex items-center gap-3 text-sm bg-white/20 px-5 py-2.5 rounded-full backdrop-blur-sm border border-white/20 shadow-lg">
                      <div className="relative">
                        <div className="w-3.5 h-3.5 bg-emerald-300 rounded-full animate-pulse shadow-lg"></div>
                        <div className="absolute inset-0 w-3.5 h-3.5 bg-emerald-300 rounded-full animate-ping"></div>
                      </div>
                      <span className="font-semibold tracking-wide">Analysis Complete • AI Powered Insights</span>
                    </div>
                  )}
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-8 lg:p-12 medical-card-gradient">
              {searchError ? (
                <div className="text-center py-16 lg:py-20">
                  <div className="relative mx-auto w-20 lg:w-24 h-20 lg:h-24 mb-8">
                    <div className="absolute inset-0 bg-gradient-to-br from-red-100 to-red-200 dark:from-red-950/60 dark:to-red-900/60 rounded-full flex items-center justify-center shadow-xl">
                      <Brain className="w-10 lg:w-12 h-10 lg:h-12 text-red-600 dark:text-red-400" />
                    </div>
                    <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">!</span>
                    </div>
                  </div>
                  <div className="text-red-800 dark:text-red-300 font-bold text-2xl lg:text-3xl mb-4">Analysis Error</div>
                  <p className="text-red-600 dark:text-red-400 mb-8 lg:mb-10 max-w-lg mx-auto text-lg lg:text-xl leading-relaxed px-4">{searchError}</p>
                  <div className="flex flex-col sm:flex-row gap-4 lg:gap-6 justify-center items-center max-w-md mx-auto">
                    <Button 
                      variant="outline" 
                      onClick={() => router.push('/patients')} 
                      className="border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-950/50 px-8 py-4 font-medium w-full sm:w-auto rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      Upload Patient Data
                    </Button>
                    <Button 
                      onClick={() => {setSearchError(''); setHasSearched(false);}}
                      className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 px-8 py-4 font-medium w-full sm:w-auto rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                    >
                      Try Again
                    </Button>
                  </div>
                </div>
              ) : !copilotResponse ? (
                <div className="text-center py-16 lg:py-20">
                  <div className="mx-auto w-20 lg:w-24 h-20 lg:h-24 bg-gradient-to-br from-muted to-muted/80 rounded-full flex items-center justify-center mb-8 shadow-xl">
                    <Brain className="w-10 lg:w-12 h-10 lg:h-12 text-muted-foreground animate-pulse" />
                  </div>
                  <p className="text-foreground text-2xl lg:text-3xl mb-4 font-bold">No Analysis Available</p>
                  <p className="text-muted-foreground max-w-lg mx-auto mb-8 lg:mb-10 text-lg lg:text-xl leading-relaxed px-4">
                    Unable to generate analysis. Please check your connection and patient data.
                  </p>
                  <Button 
                    onClick={() => router.push('/patients')}
                    variant="outline"
                    className="px-8 py-4 font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                  >
                    Check Patient Data
                  </Button>
                </div>
              ) : (
                <div className="space-y-8 lg:space-y-10">
                  {/* Enhanced AI Generated Answer */}
                  <div className="relative bg-gradient-to-br from-emerald-50/80 via-blue-50/80 to-indigo-50/80 dark:from-emerald-950/30 dark:via-blue-950/30 dark:to-indigo-950/30 p-8 lg:p-10 rounded-3xl border border-emerald-200/60 dark:border-emerald-800/60 shadow-xl hover:shadow-2xl transition-all duration-500 backdrop-blur-sm">
                    <div className="absolute top-4 right-4 w-12 h-12 bg-gradient-to-br from-emerald-400/20 to-blue-400/20 rounded-full animate-pulse"></div>
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-8">
                      <div className="relative p-4 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300">
                        <Brain className="w-7 h-7 text-white drop-shadow-sm" />
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-400 rounded-full flex items-center justify-center shadow-md">
                          <div className="w-2 h-2 bg-yellow-600 rounded-full"></div>
                        </div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-bold text-emerald-900 dark:text-emerald-100 text-xl lg:text-2xl mb-2 tracking-tight">AI Clinical Analysis</h3>
                        <p className="text-emerald-700 dark:text-emerald-300 text-sm font-medium">Advanced medical intelligence powered by AI</p>
                      </div>
                      <Badge className="bg-gradient-to-r from-emerald-100 to-blue-100 dark:from-emerald-900/50 dark:to-blue-900/50 text-emerald-800 dark:text-emerald-200 border-emerald-300 dark:border-emerald-700 font-semibold px-4 py-2 text-sm rounded-full shadow-sm">
                        Medical Grade AI
                      </Badge>
                    </div>
                    <div className="prose prose-lg max-w-none">
                      <div className="text-foreground/90 leading-relaxed whitespace-pre-wrap text-lg lg:text-xl font-medium bg-background/50 dark:bg-background/30 p-6 rounded-2xl border border-border/50 shadow-inner">
                        {cleanMarkdownText(copilotResponse.answer)}
                      </div>
                    </div>
                    
                    {/* Enhanced Context Indicator */}
                    <div className="mt-8 pt-6 border-t border-emerald-200/60 dark:border-emerald-800/60">
                      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 lg:gap-8">
                          <div className="flex items-center gap-3 bg-emerald-100/60 dark:bg-emerald-900/30 px-4 py-3 rounded-xl shadow-sm">
                            <FileText className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                            <div>
                              <span className="font-bold text-emerald-800 dark:text-emerald-200 text-sm">Sources Used</span>
                              <div className="bg-emerald-200 dark:bg-emerald-800 text-emerald-900 dark:text-emerald-100 px-3 py-1 rounded-full font-bold text-lg ml-2 inline-block shadow-sm">
                                {copilotResponse.context_used}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 bg-blue-100/60 dark:bg-blue-900/30 px-4 py-3 rounded-xl shadow-sm">
                            <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                            <div>
                              <span className="font-bold text-blue-800 dark:text-blue-200 text-sm">AI Confidence</span>
                              <div className={`ml-2 px-3 py-1 rounded-full font-bold text-lg inline-block shadow-sm ${getRelevanceColor(copilotResponse.confidence || 0.5)}`}>
                                {Math.round((copilotResponse.confidence || 0.5) * 100)}%
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground bg-muted/50 px-3 py-2 rounded-lg">
                          Model: {copilotResponse.response_metadata?.model || 'Medical AI'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Enhanced Citations - Top 3 Only */}
                  {copilotResponse.citations && copilotResponse.citations.length > 0 && (
                    <div className="medical-card-gradient p-8 lg:p-10 rounded-3xl border border-border shadow-xl hover:shadow-2xl transition-all duration-500">
                      <h3 className="font-bold text-foreground mb-8 flex flex-col sm:flex-row items-start sm:items-center gap-4 text-xl lg:text-2xl">
                        <div className="flex items-center gap-3">
                          <div className="p-3 bg-gradient-to-br from-primary to-blue-600 rounded-xl shadow-lg">
                            <FileText className="w-7 h-7 text-white" />
                          </div>
                          <span>Supporting Evidence</span>
                        </div>
                        <Badge variant="secondary" className="bg-gradient-to-r from-primary/10 to-blue-500/10 text-primary border-primary/20 font-bold px-4 py-2 text-sm rounded-full shadow-sm">
                          {Math.min(copilotResponse.citations.length, 3)} key {Math.min(copilotResponse.citations.length, 3) === 1 ? 'source' : 'sources'}
                        </Badge>
                      </h3>
                      <div className="grid gap-6 lg:gap-8">
                        {getTopUniqueCitations(copilotResponse.citations, 3).map((citation, index) => (
                          <div key={citation.id} className="relative bg-gradient-to-br from-background/80 to-muted/20 dark:from-background/60 dark:to-muted/10 rounded-2xl p-6 lg:p-8 border border-primary/20 hover:border-primary/40 transition-all duration-300 shadow-lg hover:shadow-xl card-hover backdrop-blur-sm">
                            <div className="absolute top-4 right-4 w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                              <span className="font-bold text-primary text-sm">{index + 1}</span>
                            </div>
                            <div className="flex items-start gap-4 lg:gap-6">
                              <div className="p-3 lg:p-4 bg-gradient-to-br from-primary/10 to-blue-500/10 rounded-xl shadow-sm border border-primary/20 flex-shrink-0">
                                <FileText className="w-6 lg:w-7 h-6 lg:h-7 text-primary" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 lg:gap-4 mb-4 lg:mb-5">
                                  <Badge variant="outline" className={`${getTypeColor(citation.type)} font-bold text-sm lg:text-base px-3 lg:px-4 py-1.5 rounded-full shadow-sm`}>
                                    {citation.type.charAt(0).toUpperCase() + citation.type.slice(1)}
                                  </Badge>
                                  <div className={`text-sm font-semibold ${getRelevanceColor(citation.relevance)}`}>
                                    {Math.round(citation.relevance * 100)}% match
                                  </div>
                                </div>
                                <p className="text-foreground/90 leading-relaxed font-medium mb-4 lg:mb-5 text-lg lg:text-xl bg-background/40 dark:bg-background/20 p-4 rounded-xl border border-border/50">
                                  {cleanMarkdownText(citation.text)}
                                </p>
                                <p className="text-xs text-slate-500 bg-slate-100 px-3 py-2 rounded-lg inline-block font-medium border border-slate-200">
                                  📋 {citation.source}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      {copilotResponse.citations.length > 3 && (
                        <div className="mt-4 lg:mt-6 text-center">
                          <p className="text-slate-600 text-sm bg-slate-100 px-4 py-2 rounded-lg inline-block border border-slate-200">
                            <span className="font-semibold">Note:</span> Showing top 3 most relevant sources out of {copilotResponse.citations.length} total sources
                          </p>
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