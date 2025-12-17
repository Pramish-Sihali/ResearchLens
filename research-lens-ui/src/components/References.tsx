import { useState } from "react";
import { ChevronDown, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ReferencesProps {
  references: Array<{
    number: number;
    reference: string;
    url: string;
    abstract: string;
  }>;
}

export function References({ references }: ReferencesProps) {
  const [expandedRef, setExpandedRef] = useState<number | null>(null);

  const toggleAbstract = (refNumber: number) => {
    setExpandedRef(expandedRef === refNumber ? null : refNumber);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">References ({references.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-96">
          <div className="space-y-3">
            {references.map((ref) => (
              <div
                key={ref.number}
                className="border-b pb-3 last:border-0"
              >
                <div className="flex items-start gap-2 mb-2">
                  <Badge variant="secondary" className="shrink-0 mt-0.5">
                    {ref.number}
                  </Badge>
                  <div className="flex-1">
                    {ref.url ? (
                      <a
                        href={ref.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm hover:text-primary hover:underline inline-flex items-center gap-1"
                      >
                        {ref.reference}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <p className="text-sm">{ref.reference}</p>
                    )}
                  </div>
                </div>

                {ref.abstract && (
                  <div className="ml-8">
                    <button
                      onClick={() => toggleAbstract(ref.number)}
                      className="text-xs text-primary hover:underline flex items-center gap-1"
                    >
                      {expandedRef === ref.number ? "Hide" : "View"} Abstract
                      <ChevronDown
                        className={`w-3 h-3 transition-transform ${
                          expandedRef === ref.number ? "rotate-180" : ""
                        }`}
                      />
                    </button>

                    {expandedRef === ref.number && (
                      <div className="mt-2 p-3 bg-muted/50 rounded-md text-xs text-muted-foreground leading-relaxed">
                        {ref.abstract}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
