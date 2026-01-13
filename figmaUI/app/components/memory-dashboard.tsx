import { useState } from 'react';
import { Brain, Loader2, Eye } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { ImportanceProgress } from './importance-progress';
import { config } from '../config';

interface MemoryNode {
  id: string;
  user_id: string;  // Returned by backend
  content: string;
  summary: string;
  importance: number;
  access_count: number;
  effective_importance: number;  // Calculated by backend (importance * (1 + ln(access_count + 1)))
  timestamp: string;
  last_accessed?: string;  // Optional, included if memory was accessed
}

export function MemoryDashboard() {
  const [userId, setUserId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [memories, setMemories] = useState<MemoryNode[]>([]);

  const handleLoadMemories = async () => {
    if (!userId.trim()) {
      toast.error('Please enter a User ID');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(config.memoriesEndpoint(userId));

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: MemoryNode[] = await response.json();
      setMemories(data);
      
      if (data.length === 0) {
        toast.info('No memories found for this user');
      } else {
        toast.success(`Loaded ${data.length} memories`);
      }
    } catch (error) {
      console.error('Error loading memories:', error);
      toast.error('Failed to load memories');
      setMemories([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getImportanceBadge = (importance: number) => {
    if (importance >= 0.7) return { label: 'High', variant: 'default' as const };
    if (importance >= 0.4) return { label: 'Medium', variant: 'secondary' as const };
    return { label: 'Low', variant: 'outline' as const };
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="size-6 text-blue-600" />
            AI Memory Dashboard
          </CardTitle>
          <CardDescription>
            View AI-generated memories and their importance scores
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <div className="flex-1">
              <Label htmlFor="dashboardUserId" className="sr-only">User ID</Label>
              <Input
                id="dashboardUserId"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="Enter user ID to view memories"
                required
              />
            </div>
            <Button onClick={handleLoadMemories} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="size-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                'Load Memories'
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Memory List */}
      {memories.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-sm font-medium text-gray-700">
              {memories.length} {memories.length === 1 ? 'Memory' : 'Memories'}
            </h3>
            <Badge variant="outline" className="text-xs">
              Max 5 per user
            </Badge>
          </div>

          {memories.map((memory) => (
            <Card key={memory.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm text-gray-900 mb-1">
                      📌 {memory.summary}
                    </h4>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {memory.content}
                    </p>
                  </div>
                  <Badge {...getImportanceBadge(memory.importance)}>
                    {getImportanceBadge(memory.importance).label}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Importance Score</div>
                    <div className="flex items-center gap-2">
                      <ImportanceProgress value={memory.importance * 100} className="flex-1 h-2" />
                      <span className="text-xs font-medium">{memory.importance.toFixed(2)}</span>
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-gray-500 mb-1">Access Count</div>
                    <div className="flex items-center gap-2">
                      <Eye className="size-3 text-blue-600" />
                      <span className="text-xs font-medium">{memory.access_count} times</span>
                    </div>
                  </div>
                </div>

                <div className="text-xs text-gray-500 mt-3 pt-3 border-t">
                  Created {formatTimestamp(memory.timestamp)}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && memories.length === 0 && userId && (
        <Card>
          <CardContent className="py-12 text-center">
            <Brain className="size-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No memories found for this user</p>
            <p className="text-sm text-gray-500 mt-2">
              Add conversations to create AI memories
            </p>
          </CardContent>
        </Card>
      )}

      {/* Info */}
      {!userId && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="space-y-3 text-sm">
              <p className="font-medium text-blue-900">
                💡 How AI Memory Works
              </p>
              <ul className="text-blue-800 space-y-1 text-xs">
                <li>• Claude AI assesses importance (0-1 scale) based on significance</li>
                <li>• AI generates concise summaries of key information</li>
                <li>• Similar memories (0.85+ similarity) are reinforced</li>
                <li>• Moderately similar (0.7-0.85) are merged together</li>
                <li>• Maximum 5 memories per user (lowest pruned when exceeded)</li>
                <li>• Access count shows memory reinforcement over time</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
