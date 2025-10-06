import React, { createContext, useContext, useEffect, useState } from 'react';
import io from 'socket.io-client';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Connect to the backend WebSocket server
    const newSocket = io('ws://localhost:8000', {
      transports: ['websocket'],
      autoConnect: true
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    newSocket.on('inventory_update', (data) => {
      setMessages(prev => [...prev, {
        type: 'inventory_update',
        data,
        timestamp: new Date()
      }]);
    });

    newSocket.on('agent_message', (data) => {
      setMessages(prev => [...prev, {
        type: 'agent_message',
        data,
        timestamp: new Date()
      }]);
    });

    newSocket.on('optimization_result', (data) => {
      setMessages(prev => [...prev, {
        type: 'optimization_result',
        data,
        timestamp: new Date()
      }]);
    });

    newSocket.on('system_metrics', (data) => {
      setMessages(prev => [...prev, {
        type: 'system_metrics',
        data,
        timestamp: new Date()
      }]);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const sendMessage = (event, data) => {
    if (socket && connected) {
      socket.emit(event, data);
    }
  };

  const value = {
    socket,
    connected,
    messages,
    sendMessage
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};
