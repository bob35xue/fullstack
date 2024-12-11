import React from 'react';
import { format } from 'date-fns';

function ChatHistory({ messages }) {
  return (
    <div className="chat-history">
      {messages.map((message, index) => (
        <div key={index} className="chat-message">
          <div className="message-time">
            {message.created_at && format(new Date(message.created_at), 'yyyy-MM-dd HH:mm:ss')}
          </div>
          <div className="user-query">
            <strong>Query:</strong> {message.query}
          </div>
          <div className="bot-response">
            <strong>Response:</strong> {message.response}
          </div>
          <div className="product-info">
            Product: {message.productName} (Code: {message.productCode})
          </div>
        </div>
      ))}
    </div>
  );
}

export default ChatHistory; 