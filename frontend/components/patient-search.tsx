"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { searchPatientData, healthCheck, SearchResult } from "@/lib/api"
import { Search, Loader2 } from "lucide-react"

export function PatientSearch() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [isConnected, setIsConnected] = useState<boolean | null>(null)

  const testConnection = async () => {
    try {
      await healthCheck()
      setIsConnected(true)
      setError("")
    } catch (err) {
      setIsConnected(false)
      setError("Cannot connect to backend server. Please ensure Python server is running.")
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    
    setIsLoading(true)
    setError("")
    
    try {
      const response = await searchPatientData(query, 5)
      setResults(response.results)
      setIsConnected(true)
    } catch (err) {
      setError("Search failed. Please check backend connection.")
      setIsConnected(false)
      console.error("Search error:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Clinical Search</CardTitle>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={testConnection}
                disabled={isLoading}
              >
                Test Connection
              </Button>
              {isConnected === true && (
                <Badge variant="default" className="bg-green-500">
                  Connected
                </Badge>
              )}
              {isConnected === false && (
                <Badge variant="destructive">
                  Disconnected
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <Input
              placeholder="Search patient data (e.g., 'diabetes', 'blood pressure', 'medications')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button onClick={handleSearch} disabled={isLoading || !query.trim()}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
            </Button>
          </div>
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Search Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="p-3 border rounded-md hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <p className="text-sm">{result.content}</p>
                    <Badge variant="secondary" className="ml-2 shrink-0">
                      {Math.round(result.similarity * 100)}% match
                    </Badge>
                  </div>
                  {result.metadata && result.metadata.type && (
                    <p className="text-xs text-gray-500 mt-1">
                      Type: {result.metadata.type}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}