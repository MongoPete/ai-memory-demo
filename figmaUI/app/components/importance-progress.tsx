import { cn } from './ui/utils';

interface ImportanceProgressProps {
  value: number; // 0-100
  className?: string;
  showLabel?: boolean;
}

export function ImportanceProgress({ value, className, showLabel = false }: ImportanceProgressProps) {
  const getColorClass = () => {
    if (value >= 70) return 'bg-green-500';
    if (value >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getLabel = () => {
    if (value >= 70) return 'High';
    if (value >= 40) return 'Medium';
    return 'Low';
  };

  return (
    <div className="flex items-center gap-2">
      <div className={cn("flex-1 relative", className)}>
        <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
          <div
            className={cn('h-full transition-all duration-300', getColorClass())}
            style={{ width: `${value}%` }}
          />
        </div>
      </div>
      {showLabel && (
        <span className="text-xs font-medium text-gray-600 min-w-[50px]">
          {getLabel()}
        </span>
      )}
    </div>
  );
}

interface SimilarityProgressProps {
  value: number; // 0-100
  className?: string;
}

export function SimilarityProgress({ value, className }: SimilarityProgressProps) {
  const getColorClass = () => {
    if (value >= 85) return 'bg-blue-600';
    if (value >= 70) return 'bg-blue-500';
    if (value >= 50) return 'bg-blue-400';
    return 'bg-blue-300';
  };

  return (
    <div className={cn("relative", className)}>
      <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
        <div
          className={cn('h-full transition-all duration-300', getColorClass())}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
