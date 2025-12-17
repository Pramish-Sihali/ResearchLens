import { useState, useEffect } from "react";
import { Sidebar } from "@/components/Sidebar";
import { SearchForm } from "@/components/SearchForm";
import { Results } from "@/components/Results";
import { References } from "@/components/References";
import { Proposal } from "@/components/Proposal";
import { AuthForm } from "@/components/AuthForm";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export interface AnalysisData {
  topic: string;
  paper_summary: {
    total_papers: number;
    avg_citations: number;
  };
  trend_analysis: {
    trend_direction: string;
    growth_percentage: number;
    chart_data: {
      years: number[];
      citations: number[];
    };
  };
  research_gaps: string[];
  research_questions: string[];
  methodology_suggestions: string[];
  references: Array<{
    number: number;
    reference: string;
    url: string;
    abstract: string;
  }>;
  from_cache?: boolean;
}

export interface ProposalData {
  title: string;
  introduction: string;
  literature_review: string;
  research_questions: string[];
  methodology: string;
  expected_outcomes: string;
  timeline: string;
}

export interface HistoryItem {
  id: string;
  topic: string;
  timestamp: Date;
  analysis: AnalysisData;
  proposal?: ProposalData;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisData | null>(null);
  const [currentProposal, setCurrentProposal] = useState<ProposalData | null>(null);
  const [loading, setLoading] = useState(false);
  const [proposalLoading, setProposalLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check for saved auth on mount
  useEffect(() => {
    const savedAuth = localStorage.getItem("researchlens-auth");
    if (savedAuth) {
      const { username: savedUsername } = JSON.parse(savedAuth);
      setUsername(savedUsername);
      setIsAuthenticated(true);
    }
  }, []);

  // Load history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("researchlens-history");
    if (saved) {
      const parsed = JSON.parse(saved);
      setHistory(parsed.map((h: HistoryItem) => ({
        ...h,
        timestamp: new Date(h.timestamp)
      })));
    }
  }, []);

  // Save history to localStorage
  useEffect(() => {
    if (history.length > 0) {
      localStorage.setItem("researchlens-history", JSON.stringify(history));
    }
  }, [history]);

  const handleSearch = async (topic: string) => {
    setLoading(true);
    setError(null);
    setCurrentProposal(null);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Analysis failed");

      setCurrentAnalysis(data);

      // Add to history
      const newItem: HistoryItem = {
        id: Date.now().toString(),
        topic: data.topic,
        timestamp: new Date(),
        analysis: data,
      };
      setHistory((prev) => [newItem, ...prev.slice(0, 9)]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateProposal = async (
    gaps: string[],
    questions: string[],
    methods: string[]
  ) => {
    if (!currentAnalysis) return;

    setProposalLoading(true);
    try {
      const response = await fetch(`${API_URL}/generate-proposal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: currentAnalysis.topic,
          research_gaps: gaps,
          research_questions: questions,
          methodology_suggestions: methods,
        }),
      });

      const data = await response.json();
      if (data.proposal) {
        setCurrentProposal(data.proposal);

        // Update history with proposal
        setHistory((prev) =>
          prev.map((h) =>
            h.analysis === currentAnalysis
              ? { ...h, proposal: data.proposal }
              : h
          )
        );
      }
    } catch (err) {
      setError("Failed to generate proposal");
    } finally {
      setProposalLoading(false);
    }
  };

  const handleSelectHistory = (item: HistoryItem) => {
    setCurrentAnalysis(item.analysis);
    setCurrentProposal(item.proposal || null);
    setError(null);
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem("researchlens-history");
  };

  const handleLogin = (loginUsername: string) => {
    setUsername(loginUsername);
    setIsAuthenticated(true);
    localStorage.setItem("researchlens-auth", JSON.stringify({ username: loginUsername }));
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUsername("");
    localStorage.removeItem("researchlens-auth");
    setHistory([]);
    setCurrentAnalysis(null);
    setCurrentProposal(null);
  };

  // Show auth form if not authenticated
  if (!isAuthenticated) {
    return <AuthForm onLogin={handleLogin} />;
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        history={history}
        onSelect={handleSelectHistory}
        onClear={handleClearHistory}
        username={username}
        onLogout={handleLogout}
      />

      <main className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          {/* Header */}
          <header className="text-center py-4">
            <h1 className="text-3xl font-bold text-foreground">ResearchLens</h1>
            <p className="text-muted-foreground text-sm mt-1">
              AI-Powered Research Analysis
            </p>
          </header>

          {/* Search */}
          <SearchForm onSearch={handleSearch} loading={loading} />

          {/* Error */}
          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Results */}
          {currentAnalysis && (
            <>
              <Results
                data={currentAnalysis}
                onGenerateProposal={handleGenerateProposal}
                proposalLoading={proposalLoading}
              />

              {/* References */}
              <References references={currentAnalysis.references} />
            </>
          )}

          {/* Proposal */}
          {currentProposal && currentAnalysis && (
            <Proposal
              proposal={currentProposal}
              references={currentAnalysis.references}
              topic={currentAnalysis.topic}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
