import { useState } from "react";
import { TrendingUp, TrendingDown, Minus, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from "recharts";
import type { AnalysisData } from "@/App";

interface ResultsProps {
  data: AnalysisData;
  onGenerateProposal: (gaps: string[], questions: string[], methods: string[]) => void;
  proposalLoading: boolean;
}

export function Results({ data, onGenerateProposal, proposalLoading }: ResultsProps) {
  const [selectedGaps, setSelectedGaps] = useState<string[]>(data.research_gaps);
  const [selectedQuestions, setSelectedQuestions] = useState<string[]>(data.research_questions);
  const [selectedMethods, setSelectedMethods] = useState<string[]>(data.methodology_suggestions);

  const chartData = data.trend_analysis.chart_data.years.map((year, i) => ({
    year,
    citations: data.trend_analysis.chart_data.citations[i],
  }));

  const TrendIcon = {
    heating_up: TrendingUp,
    cooling_down: TrendingDown,
    stable: Minus,
  }[data.trend_analysis.trend_direction] || Minus;

  const trendColor = {
    heating_up: "text-green-600",
    cooling_down: "text-red-600",
    stable: "text-yellow-600",
  }[data.trend_analysis.trend_direction] || "text-muted-foreground";

  const toggleItem = (
    item: string,
    _list: string[],
    setList: React.Dispatch<React.SetStateAction<string[]>>
  ) => {
    setList((prev) =>
      prev.includes(item) ? prev.filter((i) => i !== item) : [...prev, item]
    );
  };

  return (
    <div className="space-y-4">
      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">{data.paper_summary.total_papers}</p>
            <p className="text-xs text-muted-foreground">Papers</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold">{data.paper_summary.avg_citations}</p>
            <p className="text-xs text-muted-foreground">Avg Citations</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className={`flex items-center justify-center gap-1 ${trendColor}`}>
              <TrendIcon className="w-5 h-5" />
              <span className="text-lg font-bold capitalize">
                {data.trend_analysis.trend_direction.replace("_", " ")}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">Trend</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className={`text-2xl font-bold ${data.trend_analysis.growth_percentage >= 0 ? "text-green-600" : "text-red-600"}`}>
              {data.trend_analysis.growth_percentage > 0 ? "+" : ""}
              {data.trend_analysis.growth_percentage}%
            </p>
            <p className="text-xs text-muted-foreground">Growth</p>
          </CardContent>
        </Card>
      </div>

      {/* Chart */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Citation Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <XAxis dataKey="year" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={30} />
                <Line
                  type="monotone"
                  dataKey="citations"
                  stroke=""
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Tabs defaultValue="gaps">
          <CardHeader className="pb-0">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="gaps">Gaps</TabsTrigger>
              <TabsTrigger value="questions">Questions</TabsTrigger>
              <TabsTrigger value="methods">Methods</TabsTrigger>
              <TabsTrigger value="refs">References</TabsTrigger>
            </TabsList>
          </CardHeader>
          <CardContent className="pt-4">
            <TabsContent value="gaps" className="mt-0">
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {data.research_gaps.map((gap, i) => (
                    <div key={i} className="flex items-start gap-3 p-2 rounded hover:bg-muted/50">
                      <Checkbox
                        checked={selectedGaps.includes(gap)}
                        onCheckedChange={() => toggleItem(gap, selectedGaps, setSelectedGaps)}
                      />
                      <p className="text-sm">{gap}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="questions" className="mt-0">
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {data.research_questions.map((q, i) => (
                    <div key={i} className="flex items-start gap-3 p-2 rounded hover:bg-muted/50">
                      <Checkbox
                        checked={selectedQuestions.includes(q)}
                        onCheckedChange={() => toggleItem(q, selectedQuestions, setSelectedQuestions)}
                      />
                      <p className="text-sm">
                        <span className="font-medium">{i + 1}.</span> {q}
                      </p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="methods" className="mt-0">
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {data.methodology_suggestions.map((m, i) => (
                    <div key={i} className="flex items-start gap-3 p-2 rounded hover:bg-muted/50">
                      <Checkbox
                        checked={selectedMethods.includes(m)}
                        onCheckedChange={() => toggleItem(m, selectedMethods, setSelectedMethods)}
                      />
                      <p className="text-sm">{m}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="refs" className="mt-0">
              <ScrollArea className="h-64">
                <div className="space-y-3">
                  {data.references.map((ref) => (
                    <div key={ref.number} className="p-2 border-b last:border-0">
                      <div className="flex items-start gap-2">
                        <Badge variant="secondary" className="shrink-0">
                          {ref.number}
                        </Badge>
                        <div>
                          {ref.url ? (
                            <a
                              href={ref.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm hover:text-primary hover:underline"
                            >
                              {ref.reference}
                            </a>
                          ) : (
                            <p className="text-sm">{ref.reference}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>
          </CardContent>
        </Tabs>
      </Card>

      {/* Generate Proposal */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Generate Proposal</p>
              <p className="text-xs text-muted-foreground">
                {selectedGaps.length} gaps, {selectedQuestions.length} questions, {selectedMethods.length} methods selected
              </p>
            </div>
            <Button
              onClick={() => onGenerateProposal(selectedGaps, selectedQuestions, selectedMethods)}
              disabled={proposalLoading || (selectedGaps.length === 0 && selectedQuestions.length === 0 && selectedMethods.length === 0)}
            >
              {proposalLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Generating...
                </>
              ) : (
                "Generate Proposal"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
