import { useState, useRef, useEffect } from 'react';
import { 
  Linkedin, 
  Twitter, 
  Send, 
  User, 
  Bot, 
  Briefcase, 
  MessageSquare, 
  Sparkles,
  Search
} from 'lucide-react';
import './App.css';

function App() {
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [twitterUrl, setTwitterUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [profileLoaded, setProfileLoaded] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleConnect = async (e) => {
    e.preventDefault();
    if (!linkedinUrl) return;
    
    setIsProcessing(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          linkedin_url: linkedinUrl,
          x_url: twitterUrl
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.status === 'success') {
        setProfileLoaded(true);
        setMessages([
          {
            id: Date.now(),
            role: 'assistant',
            content: "I've successfully received the profile data. You can now ask me questions about their background, skills, recent transitions, or anything else!",
            timestamp: new Date()
          }
        ]);
      } else {
        alert("Error connecting profile: " + data.message);
      }
    } catch (error) {
      alert("Failed to connect to backend: " + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    
    if (!inputValue.trim() || !profileLoaded) return;
    
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage.content,
          linkedin_url: linkedinUrl 
        })
      });
      
      const data = await response.json();
      
      if (response.ok && data.status === 'success') {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            role: 'assistant',
            content: data.reply,
            timestamp: new Date()
          }
        ]);
      } else {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            role: 'assistant',
            content: "Sorry, I encountered an error: " + (data.message || "Unknown error"),
            timestamp: new Date()
          }
        ]);
      }
    } catch (error) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: "Failed to connect to backend: " + error.message,
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar for Profile Inputs */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">
            <Briefcase className="icon" size={24} />
            Profile Insights
          </h1>
        </div>
        
        <form onSubmit={handleConnect} className="profile-form">
          <div className="form-group">
            <label className="form-label">LinkedIn Profile (Mandatory)</label>
            <div className="input-wrapper">
              <Linkedin className="input-icon" />
              <input 
                type="url" 
                className="form-input" 
                placeholder="https://linkedin.com/in/username" 
                value={linkedinUrl}
                onChange={(e) => setLinkedinUrl(e.target.value)}
                required
                disabled={isProcessing || profileLoaded}
              />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">X/Twitter Profile (Optional)</label>
            <div className="input-wrapper">
              <Twitter className="input-icon" />
              <input 
                type="url" 
                className="form-input" 
                placeholder="https://x.com/username" 
                value={twitterUrl}
                onChange={(e) => setTwitterUrl(e.target.value)}
                disabled={isProcessing || profileLoaded}
              />
            </div>
          </div>
          
          {!profileLoaded ? (
            <button 
              type="submit" 
              className="submit-btn"
              disabled={!linkedinUrl || isProcessing}
            >
              {isProcessing ? (
                <>
                  <div className="typing-dot" style={{backgroundColor: 'white'}}></div>
                  <div className="typing-dot" style={{backgroundColor: 'white'}}></div>
                  <div className="typing-dot" style={{backgroundColor: 'white'}}></div>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Search size={18} />
                  Analyze Profile
                </>
              )}
            </button>
          ) : (
            <button 
              type="button" 
              className="submit-btn"
              style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
              onClick={() => {
                setProfileLoaded(false);
                setMessages([]);
                setLinkedinUrl('');
                setTwitterUrl('');
              }}
            >
              Analyze Another Profile
            </button>
          )}
        </form>

        <div className="profile-summary">
          <div className="status-indicator">
            <div className={`dot ${profileLoaded ? 'active' : ''}`}></div>
            <span>{profileLoaded ? 'Profile context active' : 'Waiting for profile'}</span>
          </div>
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="chat-area">
        <header className="chat-header">
          <div>
            <h2 className="chat-header-title">Insight Chat</h2>
            <p className="chat-header-subtitle">
              {profileLoaded 
                ? 'Ask questions about the compiled profile data' 
                : 'Connect a profile to begin'}
            </p>
          </div>
        </header>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Sparkles className="empty-state-icon" />
              <h3>Discover Professional Insights</h3>
              <p>Enter a LinkedIn profile URL in the sidebar to load their context. Then, you can ask questions like "What are their core strengths?" or "Describe their most recent career pivot."</p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div key={msg.id} className={`message-wrapper ${msg.role === 'user' ? 'user' : 'bot'}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                  </div>
                  <div className="message-bubble">
                    {msg.content}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="message-wrapper bot">
                  <div className="message-avatar">
                    <Bot size={20} />
                  </div>
                  <div className="message-bubble typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="chat-input-container">
          <form className="input-box" onSubmit={handleSendMessage}>
            <textarea
              className="chat-input"
              placeholder={profileLoaded ? "Ask a question about this profile..." : "Connect a profile first..."}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={!profileLoaded || isTyping}
              rows={1}
            />
            <button 
              type="submit" 
              className={`send-btn ${inputValue.trim() && profileLoaded ? 'active' : ''}`}
              disabled={!inputValue.trim() || !profileLoaded || isTyping}
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
