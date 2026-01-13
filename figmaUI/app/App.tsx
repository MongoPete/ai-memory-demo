import { useState, useEffect } from 'react';
import { Brain, MessageSquare, Users, Activity } from 'lucide-react';
import { Toaster } from './components/ui/sonner';
import { UnifiedChat } from './components/unified-chat';
import { SplitScreenDemo } from './components/split-screen-demo';
import { MemoryDashboard } from './components/memory-dashboard';
import { config } from './config';

type Screen = 'chat' | 'demo' | 'memories';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('chat');
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unhealthy' | 'checking'>('checking');

  // Check health status on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      setHealthStatus('checking');
      const response = await fetch(config.healthCheckEndpoint);
      if (response.ok) {
        setHealthStatus('healthy');
      } else {
        setHealthStatus('unhealthy');
      }
    } catch (error) {
      setHealthStatus('unhealthy');
    }
  };

  const getHealthColor = () => {
    switch (healthStatus) {
      case 'healthy':
        return 'bg-green-500';
      case 'unhealthy':
        return 'bg-red-500';
      case 'checking':
        return 'bg-yellow-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header Navigation */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            <div className="flex items-center gap-2 sm:gap-3 min-w-0">
              <Brain className="size-6 sm:size-8 text-blue-600 shrink-0" />
              <div className="min-w-0">
                <h1 className="text-sm sm:text-xl font-semibold text-gray-900 truncate">AI Memory Service</h1>
                <p className="text-[10px] sm:text-xs text-gray-500 hidden sm:block">MongoDB Vector Search + AWS Bedrock</p>
              </div>
            </div>

            <nav className="flex items-center gap-1 sm:gap-2">
              <button
                onClick={() => setCurrentScreen('chat')}
                className={`px-2 sm:px-4 py-1.5 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors flex items-center gap-1 sm:gap-2 ${
                  currentScreen === 'chat'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <MessageSquare className="size-3 sm:size-4" />
                <span className="hidden xs:inline">Chat</span>
              </button>

              <button
                onClick={() => setCurrentScreen('demo')}
                className={`px-2 sm:px-4 py-1.5 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors flex items-center gap-1 sm:gap-2 ${
                  currentScreen === 'demo'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Users className="size-3 sm:size-4" />
                <span className="hidden xs:inline">Demo</span>
              </button>

              <button
                onClick={() => setCurrentScreen('memories')}
                className={`px-2 sm:px-4 py-1.5 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors flex items-center gap-1 sm:gap-2 ${
                  currentScreen === 'memories'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Brain className="size-3 sm:size-4" />
                <span className="hidden sm:inline">Memories</span>
              </button>

              <div className="ml-2 sm:ml-4 flex items-center gap-1 sm:gap-2">
                <div className={`size-1.5 sm:size-2 rounded-full ${getHealthColor()}`} />
                <button
                  onClick={checkHealth}
                  className="text-[10px] sm:text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  title="System Health"
                >
                  <Activity className="size-2.5 sm:size-3" />
                  <span className="hidden sm:inline">
                    {healthStatus === 'healthy' ? 'Healthy' : healthStatus === 'unhealthy' ? 'Offline' : 'Checking...'}
                  </span>
                </button>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-2 sm:px-6 lg:px-8 py-4 sm:py-8">
        {currentScreen === 'chat' && <UnifiedChat />}
        {currentScreen === 'demo' && <SplitScreenDemo />}
        {currentScreen === 'memories' && <MemoryDashboard />}
      </main>

      {/* Toast notifications */}
      <Toaster position="top-right" />
    </div>
  );
}