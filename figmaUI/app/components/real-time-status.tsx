import { Loader2, CheckCircle, XCircle, Sparkles, Database, Brain } from 'lucide-react';
import { Progress } from './ui/progress';

export type ProcessingStage = 'idle' | 'sending' | 'storing' | 'vectorizing' | 'indexing' | 'completed' | 'error';

interface RealTimeStatusProps {
  stage: ProcessingStage;
  error?: string;
  compact?: boolean;
}

export function RealTimeStatus({ stage, error, compact = false }: RealTimeStatusProps) {
  const getProgress = () => {
    switch (stage) {
      case 'idle': return 0;
      case 'sending': return 20;
      case 'storing': return 40;
      case 'vectorizing': return 60;
      case 'indexing': return 80;
      case 'completed': return 100;
      case 'error': return 0;
    }
  };

  const getStatusColor = () => {
    switch (stage) {
      case 'idle': return 'text-gray-500';
      case 'error': return 'text-red-500';
      case 'completed': return 'text-green-500';
      default: return 'text-blue-500';
    }
  };

  const getStatusMessage = () => {
    switch (stage) {
      case 'idle': return 'Ready to send';
      case 'sending': return 'Sending message...';
      case 'storing': return 'Storing in MongoDB...';
      case 'vectorizing': return 'Generating embeddings with Bedrock (Titan)...';
      case 'indexing': return 'Indexing for vector search...';
      case 'completed': return '✓ Vectorized & indexed! Ready for semantic search';
      case 'error': return error || 'An error occurred';
    }
  };

  if (compact) {
    return (
      <div className={`flex items-center gap-2 text-xs ${getStatusColor()}`}>
        {stage === 'error' && <XCircle className="size-3" />}
        {stage === 'completed' && <CheckCircle className="size-3" />}
        {!['idle', 'error', 'completed'].includes(stage) && <Loader2 className="size-3 animate-spin" />}
        <span>{getStatusMessage()}</span>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Real-time Processing</h4>
        {stage === 'completed' && (
          <CheckCircle className="size-5 text-green-500" />
        )}
        {stage === 'error' && (
          <XCircle className="size-5 text-red-500" />
        )}
      </div>

      <Progress value={getProgress()} className="h-2" />

      <div className="space-y-2 text-xs">
        <div className={`flex items-center gap-2 ${stage === 'storing' || stage === 'completed' ? 'text-green-600' : 'text-gray-400'}`}>
          <Database className="size-4" />
          <span>Stored in MongoDB</span>
          {stage === 'storing' && <Loader2 className="size-3 animate-spin" />}
        </div>

        <div className={`flex items-center gap-2 ${stage === 'vectorizing' || stage === 'completed' ? 'text-purple-600' : 'text-gray-400'}`}>
          <Brain className="size-4" />
          <span>Vectorized by Bedrock (1536 dimensions)</span>
          {stage === 'vectorizing' && <Loader2 className="size-3 animate-spin" />}
        </div>

        <div className={`flex items-center gap-2 ${stage === 'indexing' || stage === 'completed' ? 'text-blue-600' : 'text-gray-400'}`}>
          <Sparkles className="size-4" />
          <span>Indexed in MongoDB Atlas Vector Search</span>
          {stage === 'indexing' && <Loader2 className="size-3 animate-spin" />}
        </div>
      </div>

      {stage === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded p-2 text-xs text-green-800">
          🎯 Try searching: Use different words and see semantic search in action!
        </div>
      )}

      {stage === 'error' && error && (
        <div className="bg-red-50 border border-red-200 rounded p-2 text-xs text-red-800">
          {error}
        </div>
      )}
    </div>
  );
}
