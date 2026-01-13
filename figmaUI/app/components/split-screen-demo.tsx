import { useState, useEffect, useRef } from 'react';
import { Send, Search as SearchIcon, Loader2, Users, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { config } from '../config';

interface Message {
  _id?: string;
  user_id: string;
  conversation_id: string;
  type: 'human' | 'ai';
  text: string;
  timestamp: string;
}

interface User {
  id: string;
  name: string;
  conversationId: string;
  color: string;
}

const DEMO_USERS: User[] = [
  { id: 'alice', name: 'Alice', conversationId: 'marketing_q1', color: 'bg-blue-600' },
  { id: 'bob', name: 'Bob', conversationId: 'engineering_sprint', color: 'bg-green-600' },
  { id: 'carol', name: 'Carol', conversationId: 'design_review', color: 'bg-purple-600' }
];

export function SplitScreenDemo() {
  const [messages, setMessages] = useState<Record<string, Message[]>>({
    alice: [],
    bob: [],
    carol: []
  });
  const [inputText, setInputText] = useState<Record<string, string>>({
    alice: '',
    bob: '',
    carol: ''
  });
  const [globalSearchQuery, setGlobalSearchQuery] = useState('');
  const [globalSearchResults, setGlobalSearchResults] = useState<Message[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [processingUser, setProcessingUser] = useState<string | null>(null);

  const messagesEndRefs = useRef<Record<string, HTMLDivElement | null>>({});
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const scrollToBottom = (userId: string) => {
    messagesEndRefs.current[userId]?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    DEMO_USERS.forEach(user => {
      loadConversationHistory(user.id, user.conversationId);
    });
  }, []);

  const loadConversationHistory = async (userId: string, conversationId: string) => {
    try {
      const response = await fetch(
        `${config.apiBaseUrl}/conversations/${conversationId}/messages?user_id=${userId}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => ({ ...prev, [userId]: data }));
      }
    } catch (error) {
      console.error(`Error loading conversation for ${userId}:`, error);
    }
  };

  const handleSendMessage = async (userId: string) => {
    const text = inputText[userId];
    if (!text.trim()) {
      toast.error('Please enter a message');
      return;
    }

    const user = DEMO_USERS.find(u => u.id === userId);
    if (!user) return;

    const newMessage: Message = {
      user_id: userId,
      conversation_id: user.conversationId,
      type: 'human',
      text: text,
      timestamp: new Date().toISOString()
    };

    // Optimistically add message
    setMessages(prev => ({
      ...prev,
      [userId]: [...prev[userId], newMessage]
    }));
    setInputText(prev => ({ ...prev, [userId]: '' }));
    setProcessingUser(userId);

    try {
      const response = await fetch(config.conversationEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          conversation_id: user.conversationId,
          type: 'human',
          text: text
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setTimeout(() => {
        scrollToBottom(userId);
      }, 100);

      // Show processing complete
      setTimeout(() => {
        setProcessingUser(null);
        toast.success(`${user.name}'s message vectorized!`, { duration: 2000 });
      }, 1500);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => ({
        ...prev,
        [userId]: prev[userId].filter(m => m !== newMessage)
      }));
      setProcessingUser(null);
      toast.error('Failed to send message');
    }
  };

  const handleGlobalSearch = async (query: string) => {
    if (!query.trim()) {
      setGlobalSearchResults([]);
      return;
    }

    setIsSearching(true);

    try {
      // Search across all users using the dedicated search endpoint
      // This endpoint returns ONLY relevant, filtered results with scores
      const searchPromises = DEMO_USERS.map(async (user) => {
        const params = new URLSearchParams({
          user_id: user.id,
          query: query
        });
        const response = await fetch(`${config.searchEndpoint}?${params}`);
        
        if (response.ok) {
          const data = await response.json();
          
          // Check if we have valid documents (not "No documents found")
          if (data.documents && Array.isArray(data.documents) && data.documents.length > 0) {
            // Add user context and return filtered results with scores
            return data.documents.map((doc: any) => ({
              ...doc,
              user_id: user.id, // Ensure we know which user this is from
              relevance_scores: doc.relevance_scores, // Include relevance scores
              search_metadata: data.search_metadata // Include search metadata
            }));
          }
        }
        return [];
      });

      const allResults = await Promise.all(searchPromises);
      const flatResults = allResults.flat();
      
      // Sort by relevance score (if available)
      flatResults.sort((a: any, b: any) => {
        const scoreA = a.relevance_scores?.hybrid_score || 0;
        const scoreB = b.relevance_scores?.hybrid_score || 0;
        return scoreB - scoreA;
      });
      
      setGlobalSearchResults(flatResults);
    } catch (error) {
      console.error('Error searching:', error);
      setGlobalSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Debounced global search
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(() => {
      handleGlobalSearch(globalSearchQuery);
    }, 500);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [globalSearchQuery]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getUserColor = (userId: string) => {
    return DEMO_USERS.find(u => u.id === userId)?.color || 'bg-gray-600';
  };

  const getUserName = (userId: string) => {
    return DEMO_USERS.find(u => u.id === userId)?.name || userId;
  };

  return (
    <div className="max-w-7xl mx-auto space-y-4 px-2 sm:px-4">
      {/* Header */}
      <Card>
        <CardHeader className="p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Users className="size-5 sm:size-6 text-blue-600" />
              <CardTitle className="text-base sm:text-lg">Multi-User Demo Mode</CardTitle>
            </div>
            <Badge variant="outline" className="text-xs sm:text-sm">
              <Sparkles className="size-3 mr-1" />
              Real-time Vector Search
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Three User Chats - Responsive Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        {DEMO_USERS.map((user) => (
          <Card key={user.id} className="flex flex-col h-[450px] sm:h-[500px]">
            <CardHeader className="pb-3 border-b px-3 sm:px-4 py-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <div className={`size-2.5 sm:size-3 rounded-full ${user.color}`} />
                  <h3 className="font-semibold text-sm sm:text-base">{user.name}</h3>
                  {processingUser === user.id && (
                    <Loader2 className="size-3 animate-spin text-blue-500" />
                  )}
                </div>
                <p className="text-[10px] sm:text-xs text-gray-500">{user.conversationId}</p>
              </div>
            </CardHeader>
            
            {/* Messages */}
            <CardContent className="flex-1 overflow-y-auto p-2 sm:p-3 space-y-2">
              {messages[user.id]?.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-400 text-xs">
                  No messages yet
                </div>
              ) : (
                <>
                  {messages[user.id]?.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.type === 'human' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-lg p-2 text-xs ${
                          msg.type === 'human'
                            ? `${user.color} text-white`
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <div className="break-words">{msg.text}</div>
                        <div className={`text-[9px] sm:text-[10px] mt-1 ${msg.type === 'human' ? 'text-white/70' : 'text-gray-500'}`}>
                          {formatTimestamp(msg.timestamp)}
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={(el) => messagesEndRefs.current[user.id] = el} />
                </>
              )}
            </CardContent>

            {/* Input */}
            <div className="border-t p-2 sm:p-3">
              <div className="flex gap-2">
                <Textarea
                  value={inputText[user.id]}
                  onChange={(e) => setInputText(prev => ({ ...prev, [user.id]: e.target.value }))}
                  placeholder="Type message..."
                  rows={2}
                  className="flex-1 resize-none text-xs sm:text-sm"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage(user.id);
                    }
                  }}
                />
                <Button 
                  size="sm" 
                  onClick={() => handleSendMessage(user.id)}
                  disabled={processingUser === user.id}
                  className="shrink-0 h-auto"
                >
                  <Send className="size-3" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Global Search */}
      <Card>
        <CardHeader className="pb-3 p-4 sm:p-6">
          <CardTitle className="text-base sm:text-lg">🔍 Global Search</CardTitle>
          <p className="text-xs sm:text-sm text-gray-500">Search across all users and conversations simultaneously</p>
        </CardHeader>
        <CardContent className="space-y-4 p-4 sm:p-6">
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 size-3 sm:size-4 text-gray-400" />
            <Input
              value={globalSearchQuery}
              onChange={(e) => setGlobalSearchQuery(e.target.value)}
              placeholder="Search across Alice, Bob, and Carol's conversations..."
              className="pl-9 sm:pl-10 text-sm"
            />
            {isSearching && (
              <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 size-3 sm:size-4 animate-spin text-gray-400" />
            )}
          </div>

          {/* Global Search Results */}
          {globalSearchQuery && globalSearchResults.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs sm:text-sm font-medium text-gray-700">
                Found {globalSearchResults.length} relevant result(s) across all users
              </div>
              <div className="space-y-2 max-h-60 sm:max-h-80 overflow-y-auto">
                {globalSearchResults.map((result: any, idx) => (
                  <div
                    key={idx}
                    className="p-2 sm:p-3 bg-yellow-50 border border-yellow-200 rounded text-sm"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-1 sm:gap-2 mb-1">
                          <div className={`size-2 rounded-full ${getUserColor(result.user_id)} shrink-0`} />
                          <span className="font-medium text-[10px] sm:text-xs">{getUserName(result.user_id)}</span>
                          <Badge variant="outline" className="text-[10px] sm:text-xs">
                            {result.conversation_id}
                          </Badge>
                          {/* Show relevance score if available */}
                          {result.relevance_scores?.hybrid_score && (
                            <Badge variant="secondary" className="text-[10px] sm:text-xs bg-green-100 text-green-800">
                              {Math.round(result.relevance_scores.hybrid_score * 100)}% relevant
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs sm:text-sm text-gray-900 break-words">{result.text}</p>
                        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 mt-1">
                          <p className="text-[10px] sm:text-xs text-gray-500">
                            {formatTimestamp(result.timestamp)}
                          </p>
                          {/* Show score breakdown */}
                          {result.relevance_scores && (
                            <span className="text-[9px] sm:text-xs text-gray-400" title={result.relevance_scores.explanation}>
                              📊 Vector: {Math.round((result.relevance_scores.vector_similarity || 0) * 100)}% | 
                              Text: {Math.round((result.relevance_scores.fulltext_score || 0) * 100)}%
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {globalSearchQuery && globalSearchResults.length === 0 && !isSearching && (
            <div className="text-sm text-gray-500 italic text-center py-4">
              No relevant results found (results below 70% relevance threshold were filtered)
            </div>
          )}

          {!globalSearchQuery && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
              <p className="font-medium text-blue-900 mb-2">💡 How it works:</p>
              <ul className="text-blue-800 space-y-1 text-xs">
                <li>• <strong>Hybrid Search:</strong> Combines vector similarity + full-text search</li>
                <li>• <strong>Smart Filtering:</strong> Only shows results ≥70% relevant</li>
                <li>• <strong>Semantic Understanding:</strong> Finds related concepts, not just keywords</li>
                <li>• <strong>Relevance Scores:</strong> See why each result was selected</li>
                <li>• <strong>Multi-User:</strong> Searches across all users simultaneously</li>
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Banner */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <Sparkles className="size-6 text-blue-600 flex-shrink-0 mt-1" />
            <div className="space-y-2 text-sm">
              <p className="font-medium text-gray-900">
                How it works: Each message is automatically vectorized and indexed
              </p>
              <ul className="text-gray-700 space-y-1 text-xs">
                <li>1. User types message → Stored in MongoDB</li>
                <li>2. AWS Bedrock Titan generates 1536-dimensional vector embedding</li>
                <li>3. MongoDB Atlas Vector Search indexes it for semantic similarity</li>
                <li>4. Global search uses cosine similarity across all users' vectors</li>
                <li>5. Results ranked by relevance, not just keyword matching</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
