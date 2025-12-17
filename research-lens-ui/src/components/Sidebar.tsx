import { Clock, Trash2, FileText, Key } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { HistoryItem } from "@/App";

interface SidebarProps {
  history: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
  onClear: () => void;
}

export function Sidebar({ history, onSelect, onClear }: SidebarProps) {
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  return (
    <aside className="w-64 border-r bg-sidebar flex flex-col">
      <div className="p-4 border-b">
        <h2 className="font-semibold text-sm text-sidebar-foreground flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Search History
        </h2>
      </div>

      {/* Demo Credentials Info */}
      <div className="p-3 border-b bg-muted/30">
        <Alert className="bg-primary/10 border-primary/20">
          <Key className="h-4 w-4" />
          <AlertDescription className="text-xs">
            <div className="font-semibold mb-1">Demo Mode</div>
            <p className="text-muted-foreground">
              Using sample AWS credentials. Update .env with your keys for full access.
            </p>
          </AlertDescription>
        </Alert>
      </div>

      <ScrollArea className="flex-1">
        {history.length === 0 ? (
          <p className="p-4 text-sm text-muted-foreground text-center">
            No searches yet
          </p>
        ) : (
          <div className="p-2 space-y-1">
            {history.map((item) => (
              <button
                key={item.id}
                onClick={() => onSelect(item)}
                className="w-full text-left p-3 rounded-md hover:bg-sidebar-accent transition-colors"
              >
                <p className="text-sm font-medium text-sidebar-foreground truncate">
                  {item.topic}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-muted-foreground">
                    {formatTime(item.timestamp)}
                  </span>
                  {item.proposal && (
                    <span className="text-xs text-primary flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      Proposal
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </ScrollArea>

      {history.length > 0 && (
        <>
          <Separator />
          <div className="p-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={onClear}
              className="w-full text-muted-foreground hover:text-destructive"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear History
            </Button>
          </div>
        </>
      )}
    </aside>
  );
}
