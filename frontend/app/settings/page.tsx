"use client"

import { Navigation } from "@/components/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Brain, Shield, Users, Award, ExternalLink, AlertTriangle } from "lucide-react"

const teamMembers = [
  {
    name: "Modammed Faheem",
    role: "Backend",
    github: "https://github.com/Faheem12005",
  },
  {
    name: "Michael Rodriguez",
    role: "Senior Software Engineer",
    credentials: "MS Computer Science",
    bio: "Expert in healthcare software development and HIPAA-compliant systems.",
  },
  {
    name: "Dr. Emily Watson",
    role: "Clinical Advisor",
    credentials: "MD, Internal Medicine",
    bio: "Practicing physician providing clinical validation and user experience insights.",
  },
  {
    name: "David Kim",
    role: "AI/ML Engineer",
    credentials: "PhD Machine Learning",
    bio: "Develops and maintains the AI models powering clinical recommendations.",
  },
]

const features = [
  {
    icon: Brain,
    title: "AI-Powered Recommendations",
    description:
      "Advanced machine learning algorithms analyze patient data to provide evidence-based clinical suggestions.",
  },
  {
    icon: Shield,
    title: "HIPAA Compliant",
    description:
      "Built with privacy and security at its core, ensuring patient data protection and regulatory compliance.",
  },
  {
    icon: Users,
    title: "Collaborative Care",
    description: "Designed to enhance team-based healthcare delivery and improve care coordination.",
  },
  {
    icon: Award,
    title: "Evidence-Based",
    description: "All recommendations are backed by peer-reviewed research and established clinical guidelines.",
  },
]

export default function SettingsPage() {
  return (
    <div className="min-h-screen medical-gradient">
      <Navigation />

      <div className="container mx-auto px-4 py-8 max-w-4xl space-y-8">
        {/* Header */}
        <div className="text-center animate-slide-up">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-primary/10 rounded-xl">
              <Brain className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-3xl font-bold text-foreground">Clinical Copilot</h1>
          </div>
          <p className="text-xl text-muted-foreground mb-2">Smarter Clinical Decisions with AI</p>
          <Badge className="bg-orange-100 text-orange-800 border-orange-200">
            Prototype Version - Not for Clinical Use
          </Badge>
        </div>

        {/* About Section */}
        <Card className="medical-card-gradient shadow-lg border-0 animate-fade-in">
          <CardHeader>
            <CardTitle className="text-2xl">About the Project</CardTitle>
            <CardDescription>
              Advancing healthcare through artificial intelligence and clinical decision support
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="prose prose-sm max-w-none text-muted-foreground">
              <p className="leading-relaxed">
                Clinical Copilot is an innovative AI-powered clinical decision support system designed to assist
                healthcare professionals in making evidence-based treatment decisions. By analyzing patient data and
                cross-referencing with the latest medical research, our platform provides personalized recommendations
                that enhance clinical workflows and improve patient outcomes.
              </p>
              <p className="leading-relaxed">
                Our mission is to bridge the gap between cutting-edge medical research and everyday clinical practice,
                ensuring that healthcare providers have access to the most current and relevant information when making
                critical patient care decisions.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {features.map((feature, index) => (
                <div key={index} className="flex gap-4 p-4 bg-muted/20 rounded-lg">
                  <div className="p-2 bg-primary/10 rounded-lg flex-shrink-0">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-medium mb-1">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Team Section */}
        <Card className="medical-card-gradient shadow-lg border-0 animate-fade-in">
          <CardHeader>
            <CardTitle className="text-2xl">Meet Our Team</CardTitle>
            <CardDescription>
              Experienced professionals combining clinical expertise with cutting-edge technology
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              {teamMembers.map((member, index) => (
                <div key={index} className="p-4 bg-muted/20 rounded-lg space-y-3">
                  <div>
                    <h3 className="font-semibold text-lg">{member.name}</h3>
                    <p className="text-primary font-medium">{member.role}</p>
                    <p className="text-sm text-muted-foreground">{member.credentials}</p>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{member.bio}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Important Disclaimers */}
        <Card className="medical-card-gradient shadow-lg border-0 border-l-4 border-l-orange-500 animate-fade-in">
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2 text-orange-700">
              <AlertTriangle className="h-5 w-5" />
              Important Disclaimers
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
              <h4 className="font-semibold text-orange-800 mb-2">Prototype - Not for Clinical Use</h4>
              <p className="text-sm text-orange-700 leading-relaxed">
                This application is a research prototype and demonstration tool. It is NOT intended for actual clinical
                use, patient diagnosis, or treatment decisions. All recommendations are for educational and research
                purposes only.
              </p>
            </div>

            <div className="space-y-3 text-sm text-muted-foreground">
              <p className="leading-relaxed">
                <strong>No Medical Advice:</strong> The information provided by Clinical Copilot does not constitute
                medical advice, diagnosis, or treatment recommendations. Always consult with qualified healthcare
                professionals for medical decisions.
              </p>

              <p className="leading-relaxed">
                <strong>Research Purpose:</strong> This tool is designed for research, education, and demonstration of
                AI capabilities in healthcare. It should not be used as a substitute for professional medical judgment
                or established clinical protocols.
              </p>

              <p className="leading-relaxed">
                <strong>Data Privacy:</strong> While this prototype implements security measures, it should not be used
                with real patient data. All data used in demonstrations is synthetic and for illustrative purposes only.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Technical Information */}
        <Card className="medical-card-gradient shadow-lg border-0 animate-fade-in">
          <CardHeader>
            <CardTitle className="text-xl">Technical Information</CardTitle>
            <CardDescription>Built with modern technologies and best practices</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Frontend Technologies</h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  <li>• React & Next.js</li>
                  <li>• TypeScript</li>
                  <li>• Tailwind CSS</li>
                  <li>• shadcn/ui Components</li>
                  <li>• Recharts for Data Visualization</li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium mb-3">AI & Backend</h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  <li>• Machine Learning Models</li>
                  <li>• Natural Language Processing</li>
                  <li>• Evidence-Based Algorithms</li>
                  <li>• FHIR Standard Compliance</li>
                  <li>• Secure API Architecture</li>
                </ul>
              </div>
            </div>

            <Separator />

            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Version 1.0.0 (Prototype) • Last Updated: January 2024</p>
              </div>
              <div className="flex gap-3">
                <a href="_target" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                  <ExternalLink className="h-4 w-4" />
                  Documentation
                </Button>
                </a>
              <a href="https://github.com/your-repo" target="_blank" rel="noopener noreferrer">

                <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                  <ExternalLink className="h-4 w-4" />
                  GitHub Repository
                </Button>
                </a>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card className="medical-card-gradient shadow-lg border-0 animate-fade-in">
          <CardHeader>
            <CardTitle className="text-xl">Contact & Support</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-2">Research Inquiries</h4>
                <p className="text-sm text-muted-foreground">
                  For questions about our research or collaboration opportunities:
                </p>
                <p className="text-sm font-medium text-primary">research@clinicalcopilot.ai</p>
              </div>

              <div>
                <h4 className="font-medium mb-2">Technical Support</h4>
                <p className="text-sm text-muted-foreground">For technical questions or bug reports:</p>
                <p className="text-sm font-medium text-primary">support@clinicalcopilot.ai</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
