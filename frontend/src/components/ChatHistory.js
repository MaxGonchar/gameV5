import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatHistory = ({ messages, onSummarize, summarizing }) => {
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="chat-history">
      <h2>💬 Chat History</h2>
      
      {messages.length === 0 ? (
        <div className="no-messages">
          No messages yet. Start a conversation below!
        </div>
      ) : (
        <div>
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`chat-message ${message.author_type}`}
            >
              <div className="message-header">
                <div className="message-author">
                  {message.author_name}
                </div>
                {onSummarize && (
                  <button
                    className="summarize-button"
                    onClick={() => onSummarize(message.id)}
                    title="Summarize conversation up to this message"
                    disabled={summarizing}
                  >
                    {summarizing ? '⏳' : '📋'}
                  </button>
                )}
              </div>
              <div className="message-content">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Customize rendering of specific elements if needed
                    p: ({children}) => <p style={{margin: '0.5em 0'}}>{children}</p>,
                    code: ({inline, children, ...props}) => 
                      inline ? (
                        <code style={{
                          backgroundColor: '#f4f4f4',
                          padding: '2px 4px',
                          borderRadius: '3px',
                          fontSize: '0.9em'
                        }} {...props}>
                          {children}
                        </code>
                      ) : (
                        <pre style={{
                          backgroundColor: '#f4f4f4',
                          padding: '8px 12px',
                          borderRadius: '6px',
                          overflow: 'auto',
                          fontSize: '0.9em'
                        }}>
                          <code {...props}>{children}</code>
                        </pre>
                      ),
                    blockquote: ({children}) => (
                      <blockquote style={{
                        borderLeft: '4px solid #ddd',
                        margin: '1em 0',
                        paddingLeft: '1em',
                        fontStyle: 'italic'
                      }}>
                        {children}
                      </blockquote>
                    )
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
      )}
    </div>
  );
};

export default ChatHistory;