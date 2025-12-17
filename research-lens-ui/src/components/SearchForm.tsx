import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

interface SearchFormProps {
  onSearch: (topic: string) => void;
  loading: boolean;
}

export function SearchForm({ onSearch, loading }: SearchFormProps) {
  const [topic, setTopic] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (topic.trim() && !loading) {
      onSearch(topic.trim());
    }
  };

  return (
    <Card className="p-4">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter research topic (e.g., machine learning in healthcare)"
          className="flex-1"
          disabled={loading}
        />
        <Button type="submit" disabled={loading || !topic.trim()}>
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          <span className="ml-2">{loading ? "Analyzing..." : "Analyze"}</span>
        </Button>
      </form>
    </Card>
  );
}
