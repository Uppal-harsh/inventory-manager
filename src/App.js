import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Alert } from 'react-bootstrap';
import Dashboard from './components/Dashboard';
import AgentStatus from './components/AgentStatus';
import InventoryView from './components/InventoryView';
import SustainabilityMetrics from './components/SustainabilityMetrics';
import Layout from './components/Layout';
import { SocketProvider } from './contexts/SocketContext';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // Simulate some initial alerts
    setAlerts([
      { id: 1, type: 'info', message: 'System initialized successfully', timestamp: new Date() },
      { id: 2, type: 'warning', message: 'Demand spike detected for SKU001', timestamp: new Date() },
    ]);
  }, []);

  const addAlert = (type, message) => {
    const newAlert = {
      id: Date.now(),
      type,
      message,
      timestamp: new Date()
    };
    setAlerts(prev => [newAlert, ...prev.slice(0, 9)]); // Keep last 10 alerts
  };

  const removeAlert = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard addAlert={addAlert} />;
      case 'agents':
        return <AgentStatus addAlert={addAlert} />;
      case 'inventory':
        return <InventoryView addAlert={addAlert} />;
      case 'sustainability':
        return <SustainabilityMetrics addAlert={addAlert} />;
      default:
        return <Dashboard addAlert={addAlert} />;
    }
  };

  return (
    <SocketProvider>
      <div className="App">
        <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
          <Container fluid>
          {/* Alert System */}
          <Row>
            <Col>
              {alerts.map(alert => (
                <Alert 
                  key={alert.id} 
                  variant={alert.type === 'error' ? 'danger' : alert.type}
                  dismissible
                  onClose={() => removeAlert(alert.id)}
                  className="alert-message"
                >
                  <strong>{alert.type.toUpperCase()}:</strong> {alert.message}
                  <small className="text-muted d-block">
                    {alert.timestamp.toLocaleTimeString()}
                  </small>
                </Alert>
              ))}
            </Col>
          </Row>

            {/* Main Content */}
            <Row>
              <Col>
                {renderContent()}
              </Col>
            </Row>
          </Container>
        </Layout>
      </div>
    </SocketProvider>
  );
}

export default App;
