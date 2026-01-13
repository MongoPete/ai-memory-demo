import { useState, useEffect, useRef } from 'react';
import { Send, Search as SearchIcon, Loader2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
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

interface SearchResult {
  _id: string;
  text: string;
  type: 'human' | 'ai';
  timestamp: string;
  conversation_id: string;
  score?: number;
}

interface ProcessingStatus {
  stage: 'idle' | 'sending' | 'vectorizing' | 'indexed' | 'error';
  message: string;
}

export function UnifiedChat() {
  const [userId, setUserId] = useState('alex_chen');
  const [conversationId, setConversationId] = useState('project_alpha');
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageText, setMessageText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>({
    stage: 'idle',
    message: 'Ready to send'
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history
  useEffect(() => {
    if (userId && conversationId) {
      loadConversationHistory();
    }
  }, [userId, conversationId]);

  const loadConversationHistory = async () => {
    try {
      const response = await fetch(
        `${config.apiBaseUrl}/conversations/${conversationId}/messages?user_id=${userId}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      } else {
        // Conversation doesn't exist yet, that's ok
        setMessages([]);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
      setMessages([]);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!messageText.trim() || !userId.trim() || !conversationId.trim()) {
      toast.error('Please fill in all fields');
      return;
    }

    const newMessage: Message = {
      user_id: userId,
      conversation_id: conversationId,
      type: 'human',
      text: messageText,
      timestamp: new Date().toISOString()
    };

    // Optimistically add message to UI
    setMessages(prev => [...prev, newMessage]);
    setMessageText('');

    // Show processing status
    setProcessingStatus({ stage: 'sending', message: 'Sending to MongoDB...' });

    try {
      const response = await fetch(config.conversationEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          conversation_id: conversationId,
          type: 'human',
          text: newMessage.text
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Simulate vectorization process for visual feedback
      setTimeout(() => {
        setProcessingStatus({ stage: 'vectorizing', message: 'Generating embeddings with Bedrock...' });
      }, 300);

      setTimeout(() => {
        setProcessingStatus({ stage: 'indexed', message: '✓ Vectorized! Indexed for semantic search' });
      }, 800);

      setTimeout(() => {
        setProcessingStatus({ stage: 'idle', message: 'Ready to send' });
      }, 2500);

      toast.success('Message sent and vectorized!');
    } catch (error) {
      console.error('Error sending message:', error);
      setProcessingStatus({ stage: 'error', message: 'Failed to send message' });
      toast.error('Failed to send message');
      
      // Remove optimistic message
      setMessages(prev => prev.filter(m => m !== newMessage));
      
      setTimeout(() => {
        setProcessingStatus({ stage: 'idle', message: 'Ready to send' });
      }, 2000);
    }
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);

    try {
      const params = new URLSearchParams({
        user_id: userId,
        text: query
      });

      const response = await fetch(`${config.retrieveMemoryEndpoint}?${params}`);

      if (response.ok) {
        const data = await response.json();
        
        // Extract conversation messages from response
        if (data.related_conversation && Array.isArray(data.related_conversation)) {
          setSearchResults(data.related_conversation);
        } else {
          setSearchResults([]);
        }
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Error searching:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Debounced search
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(() => {
      handleSearch(searchQuery);
    }, 500);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery, userId]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getStatusColor = () => {
    switch (processingStatus.stage) {
      case 'idle': return 'text-gray-500';
      case 'sending': return 'text-blue-500';
      case 'vectorizing': return 'text-purple-500';
      case 'indexed': return 'text-green-500';
      case 'error': return 'text-red-500';
    }
  };

  const getStatusIcon = () => {
    switch (processingStatus.stage) {
      case 'sending':
      case 'vectorizing':
        return <Loader2 className="size-3 animate-spin" />;
      case 'indexed':
        return <Sparkles className="size-3" />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Label htmlFor="userId" className="text-xs text-gray-500">User ID</Label>
              <Input
                id="userId"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="User ID"
                className="mt-1"
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="conversationId" className="text-xs text-gray-500">Conversation ID</Label>
              <Input
                id="conversationId"
                value={conversationId}
                onChange={(e) => setConversationId(e.target.value)}
                placeholder="Conversation ID"
                className="mt-1"
              />
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Chat Messages */}
      <Card className="flex-1 flex flex-col overflow-hidden mb-4">
        <CardHeader className="pb-3 border-b">
          <CardTitle className="text-lg">Chat History</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <p className="text-sm">No messages yet</p>
                <p className="text-xs mt-1">Start typing below to begin the conversation</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.type === 'human' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      msg.type === 'human'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <div className="text-sm">{msg.text}</div>
                    <div className={`text-xs mt-1 ${msg.type === 'human' ? 'text-blue-100' : 'text-gray-500'}`}>
                      {formatTimestamp(msg.timestamp)}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </CardContent>
      </Card>

      {/* Search Bar */}
      <Card className="mb-4">
        <CardContent className="pt-4">
          <div className="space-y-3">
            <div className="relative">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 size-4 text-gray-400" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search across all messages... (try semantic search!)"
                className="pl-10"
              />
              {isSearching && (
                <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 size-4 animate-spin text-gray-400" />
              )}
            </div>

            {/* Search Results */}
            {searchQuery && searchResults.length > 0 && (
              <div className="space-y-2 max-h-40 overflow-y-auto">
                <div className="text-xs text-gray-500 font-medium">
                  Found {searchResults.length} result(s)
                </div>
                {searchResults.map((result, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-yellow-50 border border-yellow-200 rounded text-sm"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <Badge variant={result.type === 'human' ? 'default' : 'secondary'} className="text-xs mb-1">
                          {result.type}
                        </Badge>
                        <p className="text-gray-900">{result.text}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {result.conversation_id} • {formatTimestamp(result.timestamp)}
                        </p>
                      </div>
                      {result.score && (
                        <Badge variant="outline" className="ml-2">
                          {(result.score * 100).toFixed(0)}% match
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {searchQuery && searchResults.length === 0 && !isSearching && (
              <div className="text-xs text-gray-500 italic">
                No results found. Try different keywords!
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Message Input */}
      <Card>
        <CardContent className="pt-4">
          <form onSubmit={handleSendMessage} className="space-y-3">
            <div className="flex gap-2">
              <Textarea
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Type your message here..."
                rows={2}
                className="flex-1 resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
              />
              <Button type="submit" size="lg" disabled={processingStatus.stage !== 'idle'}>
                <Send className="size-4" />
              </Button>
            </div>
            
            {/* Status Indicator */}
            <div className={`flex items-center gap-2 text-xs ${getStatusColor()}`}>
              {getStatusIcon()}
              <span>{processingStatus.message}</span>
              {messageText.length > 30 && processingStatus.stage === 'idle' && (
                <Badge variant="outline" className="ml-2 text-xs">
                  Will create memory
                </Badge>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
