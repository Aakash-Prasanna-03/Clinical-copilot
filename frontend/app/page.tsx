"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Activity, Brain, Shield, Users } from "lucide-react"
import { useRouter } from "next/navigation"
import { supabase } from "@/lib/supabase"

export async function login(email: string, password: string) {
  const { data, error } = await supabase
    .from("doctors")
    .select("*")
    .eq("email", email)
    .eq("password", password)
    .single()

  if (error || !data) throw new Error("Invalid login")
  return data
}


export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [errorMsg, setErrorMsg] = useState("")
  const router = useRouter()

  const handleLogin = async () => {
    try {
      const user = await login(username, password)
      console.log("Logged in:", user)
      router.push("/patients")
    } catch (err) {
      setErrorMsg("Invalid username or password")
    }
  }


  const handleGuestAccess = () => {
    router.push("/patients")
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 overflow-hidden">
      {/* 🔹 Background Video */}
      <video
        className="absolute top-0 left-0 w-full h-full object-cover z-[-1]"
        src="/video.mp4"  
        autoPlay
        loop
        muted
        playsInline
      />

      
  {/* 🔹 Dark Overlay */}
  <div className="absolute top-0 left-0 w-full h-full bg-black/60 z-[-1]" />
      {/* 🔹 Foreground content */}
        <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
          {/* Left side - Branding */}
          <div className="space-y-8 animate-slide-up">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary/10 rounded-xl">
                  <Brain className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold text-white">CaseSense</h1>
                  <p className="text-xl text-gray-200">Smarter Clinical Decisions with AI</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div
              className="flex items-center gap-3 p-4 rounded-lg backdrop-blur-sm animate-fade-in 
             border border-transparent hover:border-primary/30 transition-colors"
              style={{ animationDelay: "0.4s" }}
              >
                <Activity className="h-6 w-6 text-primary" />
                <div>
                  <h3 className="font-semibold text-white">Real-time Analysis</h3>
                  <p className="text-sm text-gray-300">Instant patient insights</p>
                </div>
              </div>
              <div
              className="flex items-center gap-3 p-4 rounded-lg backdrop-blur-sm animate-fade-in 
             border border-transparent hover:border-primary/30 transition-colors"
              style={{ animationDelay: "0.4s" }}
              >
                <Shield className="h-6 w-6 text-primary" />
                <div>
                  <h3 className="font-semibold text-white">HIPAA Compliant</h3>
                  <p className="text-sm text-gray-300">Secure & private</p>
                </div>
              </div>
              <div
              className="flex items-center gap-3 p-4 rounded-lg backdrop-blur-sm animate-fade-in 
             border border-transparent hover:border-primary/30 transition-colors"
              style={{ animationDelay: "0.4s" }}
              >
                <Brain className="h-6 w-6 text-primary" />
                <div>
                  <h3 className="font-semibold text-white">AI-Powered</h3>
                  <p className="text-sm text-gray-300">Evidence-based recommendations</p>
                </div>
              </div>
              <div
              className="flex items-center gap-3 p-4 rounded-lg backdrop-blur-sm animate-fade-in 
             border border-transparent hover:border-primary/30 transition-colors"
              style={{ animationDelay: "0.4s" }}
              >
                <Users className="h-6 w-6 text-primary" />
                <div>
                  <h3 className="font-semibold text-white">Collaborative</h3>
                  <p className="text-sm text-gray-300">Team-based care</p>
                </div>
              </div>
            </div>
          </div>


        {/* Right side - Login Form */}
        <div className="flex justify-center animate-scale-in">
          <Card className="w-full max-w-md shadow-xl border-0 bg-black/50 backdrop-blur-sm">
            <CardHeader className="space-y-2 text-center">
              <CardTitle className="text-2xl text-white">Welcome Back</CardTitle>
              <CardDescription className="text-gray-300">Sign in to access your clinical dashboard</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Email</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="Enter your email"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="h-11"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11"
                  />
                </div>
              </div>

              {errorMsg && (
                <p className="text-sm text-red-400 text-center">{errorMsg}</p>
              )}

              <div className="space-y-3">
                <Button
                  onClick={handleLogin}
                  className="w-full h-11 bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  Sign In
                </Button>
                <Button
                  onClick={handleGuestAccess}
                  variant="outline"
                  className="w-full h-11 border-white/20 hover:bg-white/5 bg-transparent text-white"
                >
                  Continue as Guest
                </Button>
              </div>

              <div className="text-center">
                <p className="text-sm text-gray-400">Prototype - Not for clinical use</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
