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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Brain className="size-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">AI Memory Service</h1>
                <p className="text-xs text-gray-500">MongoDB Vector Search + AWS Bedrock</p>
              </div>
            </div>

            <nav className="flex items-center gap-2">
              <button
                onClick={() => setCurrentScreen('chat')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  currentScreen === 'chat'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <MessageSquare className="size-4" />
                <span>Chat</span>
              </button>

              <button
                onClick={() => setCurrentScreen('demo')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  currentScreen === 'demo'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Users className="size-4" />
                <span>Demo Mode</span>
              </button>

              <button
                onClick={() => setCurrentScreen('memories')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
                  currentScreen === 'memories'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Brain className="size-4" />
                <span>Memories</span>
              </button>

              <div className="ml-4 flex items-center gap-2">
                <div className={`size-2 rounded-full ${getHealthColor()}`} />
                <button
                  onClick={checkHealth}
                  className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  title="System Health"
                >
                  <Activity className="size-3" />
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
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentScreen === 'chat' && <UnifiedChat />}
        {currentScreen === 'demo' && <SplitScreenDemo />}
        {currentScreen === 'memories' && <MemoryDashboard />}
      </main>

      {/* Toast notifications */}
      <Toaster position="top-right" />
    </div>
  );
}