import React, { useState, useEffect } from 'react';
import { MessageSquare, History, Upload, Plus, Send, Paperclip, Image, Video, FileText, Mic, X, Search, Folder, Cloud, Link2, ChevronRight, AlertCircle, CheckCircle } from 'lucide-react';
import { api } from './api';

// Main App Component
const App = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeView, setActiveView] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [attachmentMenu, setAttachmentMenu] = useState(false);
  const [uploadSourceMenu, setUploadSourceMenu] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [isLoading, setIsLoading] = useState(false);

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth();
    loadStats();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await api.healthCheck();
      setBackendStatus('connected');
    } catch (error) {
      setBackendStatus('disconnected');
      console.error('Backend health check failed:', error);
    }
  };

  const loadStats = async () => {
    try {
      const stats = await api.getStats();
      console.log('System stats:', stats);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleViewChange = (view) => {
    setActiveView(view);
    setSidebarOpen(true);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Backend Status Indicator */}
      <BackendStatusBanner status={backendStatus} onRetry={checkBackendHealth} />
      
      {/* Icon Sidebar */}
      <IconSidebar 
        activeView={activeView} 
        onViewChange={handleViewChange}
        sidebarOpen={sidebarOpen}
      />

      {/* Expandable Sidebar */}
      {sidebarOpen && (
        <ExpandableSidebar 
          activeView={activeView}
          onClose={() => setSidebarOpen(false)}
          uploadedFiles={uploadedFiles}
          setUploadedFiles={setUploadedFiles}
        />
      )}

      {/* Main Content Area */}
      <MainContent 
        activeView={activeView}
        messages={messages}
        setMessages={setMessages}
        inputValue={inputValue}
        setInputValue={setInputValue}
        attachmentMenu={attachmentMenu}
        setAttachmentMenu={setAttachmentMenu}
        uploadSourceMenu={uploadSourceMenu}
        setUploadSourceMenu={setUploadSourceMenu}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
        backendStatus={backendStatus}
      />
    </div>
  );
};

// Backend Status Banner Component
const BackendStatusBanner = ({ status, onRetry }) => {
  if (status === 'connected') return null;
  
  return (
    <div className={`absolute top-0 left-0 right-0 z-50 px-4 py-2 text-sm text-center ${
      status === 'checking' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'
    }`}>
      {status === 'checking' && (
        <span>Connecting to backend...</span>
      )}
      {status === 'disconnected' && (
        <span>
          ⚠️ Backend disconnected. Make sure the API is running on http://localhost:8000
          <button 
            onClick={onRetry}
            className="ml-3 underline hover:no-underline"
          >
            Retry
          </button>
        </span>
      )}
    </div>
  );
};

// Icon Sidebar Component
const IconSidebar = ({ activeView, onViewChange, sidebarOpen }) => {
  const items = [
    { id: 'chat', icon: MessageSquare, label: 'New Chat' },
    { id: 'history', icon: History, label: 'History' },
    { id: 'uploads', icon: Upload, label: 'Uploads' }
  ];

  return (
    <div className="w-16 bg-white border-r border-gray-200 flex flex-col items-center py-4 space-y-2">
      <button
        onClick={() => onViewChange('chat')}
        className="w-10 h-10 rounded-lg bg-blue-600 hover:bg-blue-700 flex items-center justify-center mb-4 transition-colors"
      >
        <Plus className="w-5 h-5 text-white" />
      </button>
      
      {items.map((item) => (
        <button
          key={item.id}
          onClick={() => onViewChange(item.id)}
          className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${
            activeView === item.id && sidebarOpen
              ? 'bg-blue-50 text-blue-600'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
          title={item.label}
        >
          <item.icon className="w-5 h-5" />
        </button>
      ))}
    </div>
  );
};

// Expandable Sidebar Component
const ExpandableSidebar = ({ activeView, onClose, uploadedFiles, setUploadedFiles }) => {
  return (
    <div className="w-72 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">
          {activeView === 'chat' && 'New Chat'}
          {activeView === 'history' && 'Chat History'}
          {activeView === 'uploads' && 'Uploads'}
        </h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {activeView === 'history' && <HistoryView />}
        {activeView === 'uploads' && (
          <UploadsView 
            uploadedFiles={uploadedFiles} 
            setUploadedFiles={setUploadedFiles}
          />
        )}
        {activeView === 'chat' && (
          <div className="p-4 text-sm text-gray-500 text-center">
            Start a new conversation
          </div>
        )}
      </div>
    </div>
  );
};

// History View Component
const HistoryView = () => {
  const [chats] = useState([
    { id: 1, title: 'International Development Report 2024', time: '2 hours ago' },
    { id: 2, title: 'Email screenshot analysis', time: 'Yesterday' },
    { id: 3, title: 'Audio transcript from meeting', time: '2 days ago' },
    { id: 4, title: 'Budget proposal documents', time: '1 week ago' },
  ]);

  return (
    <div className="p-2">
      {chats.map((chat) => (
        <button
          key={chat.id}
          className="w-full p-3 rounded-lg hover:bg-gray-50 text-left transition-colors mb-1 group"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">
                {chat.title}
              </p>
              <p className="text-xs text-gray-500 mt-1">{chat.time}</p>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2" />
          </div>
        </button>
      ))}
    </div>
  );
};

// Uploads View Component
const UploadsView = ({ uploadedFiles, setUploadedFiles }) => {
  const [activeTab, setActiveTab] = useState('all');
  const [showUploadSource, setShowUploadSource] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setUploading(true);
    setUploadStatus(null);

    try {
      const results = await api.uploadDocuments(files);
      setUploadStatus({ type: 'success', message: `Successfully uploaded ${files.length} file(s)` });
      
      // Add to uploaded files list
      const newFiles = files.map((file, idx) => ({
        name: file.name,
        type: file.type.includes('pdf') ? 'document' : 'document',
        size: file.size,
        chunks: results[idx]?.chunks_created || 0,
        uploadedAt: new Date().toISOString()
      }));
      
      setUploadedFiles(prev => [...newFiles, ...prev]);
      
      setTimeout(() => setUploadStatus(null), 3000);
    } catch (error) {
      setUploadStatus({ type: 'error', message: error.message || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  const tabs = [
    { id: 'all', label: 'All', count: uploadedFiles.length },
    { id: 'documents', label: 'Documents', count: uploadedFiles.length },
  ];

  const uploadSources = [
    { id: 'local', icon: Folder, label: 'From Device' },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <label className="block">
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
          />
          <span className={`w-full px-4 py-2 ${uploading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'} text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2 cursor-pointer`}>
            <Upload className="w-4 h-4" />
            <span>{uploading ? 'Uploading...' : 'Upload Files'}</span>
          </span>
        </label>

        {uploadStatus && (
          <div className={`mt-2 p-2 rounded-lg text-sm flex items-center space-x-2 ${
            uploadStatus.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}>
            {uploadStatus.type === 'success' ? (
              <CheckCircle className="w-4 h-4" />
            ) : (
              <AlertCircle className="w-4 h-4" />
            )}
            <span>{uploadStatus.message}</span>
          </div>
        )}
      </div>

      <div className="p-2 border-b border-gray-200 flex space-x-1 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {uploadedFiles.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-8">
            No files uploaded yet
          </div>
        ) : (
          <div className="space-y-2">
            {uploadedFiles.map((file, idx) => (
              <div
                key={idx}
                className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-start space-x-3">
                  <FileText className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {file.chunks} chunks • {new Date(file.uploadedAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Main Content Component
const MainContent = ({ 
  activeView, 
  messages, 
  setMessages, 
  inputValue, 
  setInputValue,
  attachmentMenu,
  setAttachmentMenu,
  uploadSourceMenu,
  setUploadSourceMenu,
  isLoading,
  setIsLoading,
  backendStatus
}) => {
  const handleSend = async () => {
    if (!inputValue.trim() || backendStatus !== 'connected') return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // Query the backend
      const response = await api.queryDocuments(inputValue, {
        top_k: 5,
        rerank: true
      });
      
      // Map backend response to frontend format
      const mappedSources = (response.sources || []).map(source => ({
        content: source.text || source.content || '',
        score: source.similarity_score || source.score || 0,
        metadata: {
          file_name: source.file_name || 'Unknown',
          page: source.page || null,
          chunk_id: source.chunk_id
        }
      }));
      
      // Create assistant message with response
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        sources: mappedSources,
        metadata: {
          query_time: response.metadata?.query_time,
          total_sources: mappedSources.length
        }
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      // Error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `❌ Error: ${error.message}. Make sure you have uploaded documents first.`,
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <MessageList messages={messages} isLoading={isLoading} />
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-4xl mx-auto">
          <div className="relative flex items-end space-x-2">
            {/* Input Field */}
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
                placeholder="Ask anything about your documents..."
                disabled={isLoading || backendStatus !== 'connected'}
                className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
            </div>

            {/* Send Button */}
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading || backendStatus !== 'connected'}
              className="p-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Source List Component
const SourceList = ({ sources }) => {
  if (!sources || sources.length === 0) return null;
  
  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      <p className="text-sm font-semibold text-gray-700 mb-3">📚 Detailed Sources:</p>
      <div className="space-y-3">
        {sources.map((source, idx) => (
          <div
            key={idx}
            className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-600 text-white text-xs font-bold rounded-full">
                  {idx + 1}
                </span>
                <span className="font-semibold text-gray-800">
                  {source.metadata?.file_name || 'Unknown'}
                </span>
              </div>
              <span className="text-xs font-medium text-blue-700 bg-blue-100 px-2 py-1 rounded">
                {(source.score * 100).toFixed(1)}% match
              </span>
            </div>
            <p className="text-gray-700 text-sm leading-relaxed ml-8">
              {source.content}
            </p>
            <div className="flex items-center space-x-3 mt-2 ml-8 text-xs text-gray-600">
              {source.metadata?.page && (
                <span className="flex items-center space-x-1">
                  <FileText className="w-3 h-3" />
                  <span>Page {source.metadata.page}</span>
                </span>
              )}
              {source.metadata?.chunk_id !== undefined && (
                <span>• Chunk {source.metadata.chunk_id}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Remove old unused components
const AttachmentMenu = ({ onClose }) => {
  return null;
};

// Empty State Component
const EmptyState = () => {
  const suggestions = [
    "What are the main findings in the uploaded documents?",
    "Summarize the key points from the PDF",
    "Find information about the budget",
  ];

  return (
    <div className="max-w-3xl mx-auto text-center py-12">
      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <Search className="w-8 h-8 text-white" />
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-3">
        DocuMind RAG System
      </h1>
      <p className="text-gray-600 mb-8">
        Upload documents and ask questions to get citation-based answers
      </p>
      
      <div className="space-y-3">
        <p className="text-sm font-medium text-gray-500 mb-4">Try asking:</p>
        {suggestions.map((suggestion, idx) => (
          <button
            key={idx}
            className="w-full p-4 text-left rounded-xl border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all group"
          >
            <p className="text-sm text-gray-700 group-hover:text-blue-700">
              {suggestion}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};

// Message List Component
const MessageList = ({ messages, isLoading }) => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm p-4">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Message Component
const Message = ({ message }) => {
  if (message.type === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm max-w-2xl">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className={`border rounded-2xl rounded-tl-sm p-5 max-w-3xl shadow-sm ${
        message.isError ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200'
      }`}>
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
        
        {message.sources && message.sources.length > 0 && (
          <SourceList sources={message.sources} />
        )}

        {message.metadata && (
          <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
            <span>⚡ Query processed in {message.metadata.query_time?.toFixed(2)}s</span>
            <span>{message.metadata.total_sources} source{message.metadata.total_sources !== 1 ? 's' : ''} retrieved</span>
          </div>
        )}
      </div>
    </div>
  );
};

// Attachment Grid Component
const AttachmentGrid = ({ attachments }) => {
  return (
    <div className="grid grid-cols-2 gap-3 mb-4">
      {attachments.map((attachment, idx) => (
        <AttachmentCard key={idx} attachment={attachment} />
      ))}
    </div>
  );
};

// Attachment Card Component
const AttachmentCard = ({ attachment }) => {
  const getIcon = () => {
    switch (attachment.type) {
      case 'image': return <Image className="w-5 h-5" />;
      case 'video': return <Video className="w-5 h-5" />;
      case 'audio': return <Mic className="w-5 h-5" />;
      case 'document': return <FileText className="w-5 h-5" />;
      default: return <FileText className="w-5 h-5" />;
    }
  };

  const getColor = () => {
    switch (attachment.type) {
      case 'image': return 'bg-purple-50 text-purple-600 border-purple-200';
      case 'video': return 'bg-red-50 text-red-600 border-red-200';
      case 'audio': return 'bg-green-50 text-green-600 border-green-200';
      case 'document': return 'bg-blue-50 text-blue-600 border-blue-200';
      default: return 'bg-gray-50 text-gray-600 border-gray-200';
    }
  };

  return (
    <button className={`p-4 rounded-xl border-2 hover:shadow-md transition-all text-left ${getColor()}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{attachment.name}</p>
          {attachment.duration && (
            <p className="text-xs opacity-75 mt-1">{attachment.duration}</p>
          )}
        </div>
      </div>
    </button>
  );
};

// Citation List Component
const CitationList = ({ citations }) => {
  return (
    <div className="pt-3 border-t border-gray-200">
      <p className="text-xs font-medium text-gray-500 mb-2">Sources:</p>
      <div className="flex flex-wrap gap-2">
        {citations.map((citation) => (
          <button
            key={citation.id}
            className="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs text-gray-700 transition-colors"
          >
            [{citation.id}] {citation.source}
            {citation.page && ` - Page ${citation.page}`}
          </button>
        ))}
      </div>
    </div>
  );
};

export default App;