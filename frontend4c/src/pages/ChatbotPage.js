import React, { useState } from 'react';
import axios from 'axios';

const ChatbotPage = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      console.log('Sending query:', query);
      const response = await axios.post(
        'http://localhost:8000/issues/classify/', 
        { query: query },
        { 
          withCredentials: true,  // Important for sending/receiving cookies
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      // Add the new message to the chat history
      setMessages([...messages, {
        query: query,
        response: response.data.response,
        productCode: response.data.product_code,
        productName: response.data.product_name,
        issueId: response.data.issue_id
      }]);

      // Clear the input field
      setQuery('');
      setError('');
    } catch (error) {
      console.error('Failed to send query:', error);
      
      if (error.response?.status === 401) {
        setError('Please log in to use the chatbot');
        // Optionally redirect to login page
        // window.location.href = '/login';
      } else {
        setError(error.response?.data?.detail || 'Failed to get response from chatbot');
      }
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      padding: '20px'
    }}>
      {/* Messages Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        marginBottom: '20px'
      }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: '10px' }}>
            <p style={{ fontWeight: 'bold' }}>You: {msg.query}</p>
            <p>Bot: {msg.response}</p>
            <p style={{ fontSize: '0.8em', color: '#666' }}>
              Product: {msg.productName} (Code: {msg.productCode})
            </p>
          </div>
        ))}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{
        display: 'flex',
        gap: '10px',
        position: 'fixed',
        bottom: '20px',
        left: '20px',
        right: '20px',
        backgroundColor: 'white',
        padding: '10px'
      }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your message..."
          style={{
            flex: 1,
            padding: '10px',
            borderRadius: '4px',
            border: '1px solid #ddd'
          }}
        />
        <button 
          type="submit"
          style={{
            padding: '10px 20px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatbotPage;