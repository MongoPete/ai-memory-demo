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
      // Search across all users
      const searchPromises = DEMO_USERS.map(async (user) => {
        const params = new URLSearchParams({
          user_id: user.id,
          text: query
        });
        const response = await fetch(`${config.retrieveMemoryEndpoint}?${params}`);
        
        if (response.ok) {
          const data = await response.json();
          if (data.related_conversation && Array.isArray(data.related_conversation)) {
            return data.related_conversation.map((msg: Message) => ({
              ...msg,
              user_id: user.id // Ensure we know which user this is from
            }));
          }
        }
        return [];
      });

      const allResults = await Promise.all(searchPromises);
      const flatResults = allResults.flat();
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
    <div className="max-w-7xl mx-auto space-y-4">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Users className="size-6 text-blue-600" />
              <CardTitle>Multi-User Demo Mode</CardTitle>
            </div>
            <Badge variant="outline" className="text-sm">
              <Sparkles className="size-3 mr-1" />
              Real-time Vector Search
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Three User Chats Side by Side */}
      <div className="grid grid-cols-3 gap-4">
        {DEMO_USERS.map((user) => (
          <Card key={user.id} className="flex flex-col h-[500px]">
            <CardHeader className="pb-3 border-b">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <div className={`size-3 rounded-full ${user.color}`} />
                  <h3 className="font-semibold">{user.name}</h3>
                  {processingUser === user.id && (
                    <Loader2 className="size-3 animate-spin text-blue-500" />
                  )}
                </div>
                <p className="text-xs text-gray-500">{user.conversationId}</p>
              </div>
            </CardHeader>
            
            {/* Messages */}
            <CardContent className="flex-1 overflow-y-auto p-3 space-y-2">
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
                        <div>{msg.text}</div>
                        <div className={`text-[10px] mt-1 ${msg.type === 'human' ? 'text-white/70' : 'text-gray-500'}`}>
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
            <div className="border-t p-3">
              <div className="flex gap-2">
                <Textarea
                  value={inputText[user.id]}
                  onChange={(e) => setInputText(prev => ({ ...prev, [user.id]: e.target.value }))}
                  placeholder="Type message..."
                  rows={2}
                  className="flex-1 resize-none text-sm"
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
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">🔍 Global Search</CardTitle>
          <p className="text-sm text-gray-500">Search across all users and conversations simultaneously</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 size-4 text-gray-400" />
            <Input
              value={globalSearchQuery}
              onChange={(e) => setGlobalSearchQuery(e.target.value)}
              placeholder="Search across Alice, Bob, and Carol's conversations... (try semantic search!)"
              className="pl-10"
            />
            {isSearching && (
              <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 size-4 animate-spin text-gray-400" />
            )}
          </div>

          {/* Global Search Results */}
          {globalSearchQuery && globalSearchResults.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-gray-700">
                Found {globalSearchResults.length} result(s) across all users
              </div>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {globalSearchResults.map((result, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-yellow-50 border border-yellow-200 rounded text-sm"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <div className={`size-2 rounded-full ${getUserColor(result.user_id)}`} />
                          <span className="font-medium text-xs">{getUserName(result.user_id)}</span>
                          <Badge variant="outline" className="text-xs">
                            {result.conversation_id}
                          </Badge>
                        </div>
                        <p className="text-gray-900">{result.text}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatTimestamp(result.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {globalSearchQuery && globalSearchResults.length === 0 && !isSearching && (
            <div className="text-sm text-gray-500 italic text-center py-4">
              No results found across all conversations
            </div>
          )}

          {!globalSearchQuery && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
              <p className="font-medium text-blue-900 mb-2">💡 Try these searches:</p>
              <ul className="text-blue-800 space-y-1 text-xs">
                <li>• Search for topics mentioned by any user</li>
                <li>• Semantic search works across different wording</li>
                <li>• Results show which user and conversation matched</li>
                <li>• Demonstrates scalability: Works for 3 users or 3000 users</li>
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
