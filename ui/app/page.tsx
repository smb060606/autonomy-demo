"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { AlertCircle, CheckCircle, FileText, Loader2 } from "lucide-react"

export default function Home() {
  const [article, setArticle] = useState("")
  const [report, setReport] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleFactCheck = async () => {
    if (!article.trim()) {
      setError("Please enter an article to fact-check")
      return
    }

    if (article.length < 50) {
      setError("Article is too short. Please provide a substantial article.")
      return
    }

    setIsLoading(true)
    setError("")
    setReport("")

    try {
      const response = await fetch("/api/fact-check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ article }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Fact-check failed")
      }

      const data = await response.json()
      setReport(data.report)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred during fact-checking")
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setArticle("")
    setReport("")
    setError("")
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2 flex items-center justify-center gap-2">
            <FileText className="h-8 w-8" />
            Fact-Check News
          </h1>
          <p className="text-slate-600">
            AI-Powered News Verification using Parallel Agent Processing
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Input Section */}
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Article Input</CardTitle>
              <CardDescription>
                Paste the news article you want to fact-check
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Paste your article here..."
                value={article}
                onChange={(e) => setArticle(e.target.value)}
                className="min-h-[400px] font-mono text-sm"
                disabled={isLoading}
              />
              
              <div className="flex gap-2">
                <Button
                  onClick={handleFactCheck}
                  disabled={isLoading || !article.trim()}
                  className="flex-1"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Fact-Checking...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Fact-Check Article
                    </>
                  )}
                </Button>
                
                <Button
                  onClick={handleClear}
                  variant="outline"
                  disabled={isLoading}
                >
                  Clear
                </Button>
              </div>

              {error && (
                <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-md text-red-800 text-sm">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {isLoading && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm text-blue-900 font-medium mb-2">Processing...</p>
                  <ul className="text-xs text-blue-700 space-y-1 list-disc list-inside">
                    <li>Extracting claims from article</li>
                    <li>Deploying parallel fact-checking agents</li>
                    <li>Searching for evidence using Brave Search</li>
                    <li>Generating comprehensive report</li>
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Report Section */}
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Fact-Check Report</CardTitle>
              <CardDescription>
                Comprehensive analysis with sources and verdicts
              </CardDescription>
            </CardHeader>
            <CardContent>
              {report ? (
                <div className="prose prose-sm max-w-none">
                  <div className="bg-white border rounded-lg p-6 min-h-[400px] whitespace-pre-wrap font-sans text-sm leading-relaxed">
                    {report}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center min-h-[400px] text-center text-slate-400">
                  <FileText className="h-16 w-16 mb-4 opacity-50" />
                  <p className="text-sm">
                    Your fact-check report will appear here
                  </p>
                  <p className="text-xs mt-2">
                    Enter an article and click &quot;Fact-Check Article&quot; to begin
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center text-sm text-slate-500">
          <p>
            Powered by <span className="font-semibold">Autonomy Computer</span> with parallel AI agents and Brave Search
          </p>
        </div>
      </div>
    </main>
  )
}


