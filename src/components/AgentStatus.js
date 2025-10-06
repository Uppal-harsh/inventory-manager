import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Badge, ListGroup } from 'react-bootstrap';
import { useSocket } from '../contexts/SocketContext';

const AgentStatus = ({ addAlert }) => {
  const { connected, messages } = useSocket();
  const [agents, setAgents] = useState({
    demand: {
      name: 'Demand Agent',
      status: 'active',
      lastActivity: new Date(),
      messagesProcessed: 45,
      forecastsGenerated: 12,
      confidence: 0.87,
      color: '#28a745'
    },
    supply: {
      name: 'Supply Agent',
      status: 'active',
      lastActivity: new Date(),
      ordersProcessed: 23,
      suppliersMonitored: 4,
      reliability: 0.92,
      color: '#007bff'
    },
    logistics: {
      name: 'Logistics Agent',
      status: 'active',
      lastActivity: new Date(),
      shipmentsOptimized: 18,
      routesCalculated: 156,
      efficiency: 0.89,
      color: '#ffc107'
    },
    negotiation: {
      name: 'Negotiation Agent',
      status: 'active',
      lastActivity: new Date(),
      negotiationsCompleted: 7,
      costSavings: 12500,
      successRate: 0.85,
      color: '#dc3545'
    }
  });

  const [recentMessages, setRecentMessages] = useState([
    {
      id: 1,
      from: 'demand',
      to: 'supply',
      type: 'demand_forecast',
      content: 'Forecast spike for SKU001 - 150% increase expected',
      timestamp: new Date(Date.now() - 2 * 60 * 1000)
    },
    {
      id: 2,
      from: 'supply',
      to: 'negotiation',
      type: 'supply_alert',
      content: 'Low stock alert for SKU003 - immediate reorder needed',
      timestamp: new Date(Date.now() - 5 * 60 * 1000)
    },
    {
      id: 3,
      from: 'logistics',
      to: 'supply',
      type: 'logistics_request',
      content: 'Proposing inventory transfer from North to South warehouse',
      timestamp: new Date(Date.now() - 8 * 60 * 1000)
    },
    {
      id: 4,
      from: 'negotiation',
      to: 'supply',
      type: 'negotiation_offer',
      content: 'Secured 15% discount from SUP002 for bulk order',
      timestamp: new Date(Date.now() - 12 * 60 * 1000)
    }
  ]);

  useEffect(() => {
    // Update agent activity based on incoming messages
    messages.forEach(message => {
      if (message.type === 'agent_message') {
        const data = message.data;
        const agentKey = data.from_agent?.toLowerCase();
        
        if (agentKey && agents[agentKey]) {
          setAgents(prev => ({
            ...prev,
            [agentKey]: {
              ...prev[agentKey],
              lastActivity: new Date(),
              messagesProcessed: prev[agentKey].messagesProcessed + 1
            }
          }));

          // Add to recent messages
          const newMessage = {
            id: Date.now(),
            from: data.from_agent,
            to: data.to_agent,
            type: data.message_type,
            content: JSON.stringify(data.content).substring(0, 100) + '...',
            timestamp: new Date()
          };
          
          setRecentMessages(prev => [newMessage, ...prev.slice(0, 9)]);
        }
      }
    });
  }, [messages, agents]);

  const getStatusBadge = (status) => {
    const variants = {
      active: 'success',
      inactive: 'secondary',
      error: 'danger',
      warning: 'warning'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const getAgentIcon = (agentType) => {
    const icons = {
      demand: '📊',
      supply: '📦',
      logistics: '🚚',
      negotiation: '🤝'
    };
    return icons[agentType] || '🤖';
  };

  return (
    <div>
      <Row className="mb-4">
        <Col>
          <h2>Agent Status & Communication</h2>
          <p className="text-muted">Real-time monitoring of AI agents and their interactions</p>
        </Col>
      </Row>

      {/* Agent Cards */}
      <Row className="mb-4">
        {Object.entries(agents).map(([key, agent]) => (
          <Col md={6} lg={3} key={key}>
            <Card className={`agent-card ${key}-agent`}>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <div>
                  {getAgentIcon(key)} <strong>{agent.name}</strong>
                </div>
                {getStatusBadge(agent.status)}
              </Card.Header>
              <Card.Body>
                <div className="mb-2">
                  <small className="text-muted">Last Activity:</small>
                  <div>{agent.lastActivity.toLocaleTimeString()}</div>
                </div>
                
                {key === 'demand' && (
                  <>
                    <div className="mb-1">
                      <small className="text-muted">Forecasts Generated:</small>
                      <Badge bg="primary" className="ms-2">{agent.forecastsGenerated}</Badge>
                    </div>
                    <div className="mb-1">
                      <small className="text-muted">Confidence:</small>
                      <Badge bg="success" className="ms-2">{(agent.confidence * 100).toFixed(1)}%</Badge>
                    </div>
                  </>
                )}
                
                {key === 'supply' && (
                  <>
                    <div className="mb-1">
                      <small className="text-muted">Orders Processed:</small>
                      <Badge bg="info" className="ms-2">{agent.ordersProcessed}</Badge>
                    </div>
                    <div className="mb-1">
                      <small className="text-muted">Suppliers:</small>
                      <Badge bg="secondary" className="ms-2">{agent.suppliersMonitored}</Badge>
                    </div>
                  </>
                )}
                
                {key === 'logistics' && (
                  <>
                    <div className="mb-1">
                      <small className="text-muted">Shipments:</small>
                      <Badge bg="warning" className="ms-2">{agent.shipmentsOptimized}</Badge>
                    </div>
                    <div className="mb-1">
                      <small className="text-muted">Efficiency:</small>
                      <Badge bg="success" className="ms-2">{(agent.efficiency * 100).toFixed(1)}%</Badge>
                    </div>
                  </>
                )}
                
                {key === 'negotiation' && (
                  <>
                    <div className="mb-1">
                      <small className="text-muted">Negotiations:</small>
                      <Badge bg="danger" className="ms-2">{agent.negotiationsCompleted}</Badge>
                    </div>
                    <div className="mb-1">
                      <small className="text-muted">Savings:</small>
                      <Badge bg="success" className="ms-2">${agent.costSavings.toLocaleString()}</Badge>
                    </div>
                  </>
                )}
                
                <div className="mt-2">
                  <small className="text-muted">Messages:</small>
                  <Badge bg="dark" className="ms-2">{agent.messagesProcessed}</Badge>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Communication Log */}
      <Row>
        <Col md={8}>
          <Card>
            <Card.Header>
              <h5>Recent Agent Communication</h5>
            </Card.Header>
            <Card.Body>
              <ListGroup variant="flush">
                {recentMessages.map(message => (
                  <ListGroup.Item key={message.id} className="d-flex justify-content-between align-items-start">
                    <div className="ms-2 me-auto">
                      <div className="fw-bold">
                        {getAgentIcon(message.from)} {message.from} → {message.to}
                      </div>
                      <div className="text-muted">{message.type}</div>
                      <div className="small">{message.content}</div>
                    </div>
                    <Badge bg="light" text="dark">
                      {message.timestamp.toLocaleTimeString()}
                    </Badge>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card>
            <Card.Header>
              <h5>System Health</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <div className="d-flex justify-content-between">
                  <span>WebSocket Connection</span>
                  <Badge bg={connected ? 'success' : 'danger'}>
                    {connected ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>
              </div>
              
              <div className="mb-3">
                <div className="d-flex justify-content-between">
                  <span>Active Agents</span>
                  <Badge bg="success">
                    {Object.values(agents).filter(a => a.status === 'active').length}/4
                  </Badge>
                </div>
              </div>
              
              <div className="mb-3">
                <div className="d-flex justify-content-between">
                  <span>Total Messages</span>
                  <Badge bg="primary">
                    {Object.values(agents).reduce((sum, agent) => sum + agent.messagesProcessed, 0)}
                  </Badge>
                </div>
              </div>
              
              <div className="mb-3">
                <div className="d-flex justify-content-between">
                  <span>System Uptime</span>
                  <Badge bg="info">99.8%</Badge>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AgentStatus;