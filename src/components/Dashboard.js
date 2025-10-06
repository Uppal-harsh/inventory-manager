import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Badge, ProgressBar } from 'react-bootstrap';
import MetricCard from './MetricCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useSocket } from '../contexts/SocketContext';

const Dashboard = ({ addAlert }) => {
  const { connected, messages, sendMessage } = useSocket();
  const [metrics, setMetrics] = useState({
    totalInventoryValue: 125000,
    totalCarbonFootprint: 2450,
    serviceLevel: 0.94,
    stockoutIncidents: 3,
    overstockIncidents: 7,
    costEfficiency: 0.87,
    agentCommunicationVolume: 156,
    optimizationCyclesCompleted: 42
  });

  const [demandData, setDemandData] = useState([]);
  const [inventoryData, setInventoryData] = useState([]);

  useEffect(() => {
    // Initialize with sample data
    const sampleDemandData = [];
    const sampleInventoryData = [];
    const now = new Date();

    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      sampleDemandData.push({
        time: time.toLocaleTimeString(),
        demand: Math.random() * 100 + 50,
        forecast: Math.random() * 100 + 50
      });
    }

    for (let i = 6; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      sampleInventoryData.push({
        date: date.toLocaleDateString(),
        north: Math.random() * 1000 + 500,
        central: Math.random() * 1200 + 600,
        south: Math.random() * 800 + 400
      });
    }

    setDemandData(sampleDemandData);
    setInventoryData(sampleInventoryData);
  }, []);

  useEffect(() => {
    // Process incoming messages
    messages.forEach(message => {
      if (message.type === 'system_metrics') {
        setMetrics(prev => ({ ...prev, ...message.data }));
      } else if (message.type === 'optimization_result') {
        addAlert('info', `Optimization completed for ${message.data.sku_id}`);
      }
    });
  }, [messages, addAlert]);

  const simulateDemandSpike = () => {
    sendMessage('simulate_demand_spike', { 
      sku_id: 'SKU001', 
      multiplier: 2.5, 
      duration_hours: 24 
    });
    addAlert('warning', 'Simulating demand spike for SKU001');
  };

  const simulateDelay = () => {
    sendMessage('simulate_delay', { 
      supplier_id: 'SUP001', 
      delay_days: 3 
    });
    addAlert('warning', 'Simulating supplier delay for SUP001');
  };

  const triggerOptimization = () => {
    sendMessage('trigger_optimization', {});
    addAlert('info', 'Triggering system-wide optimization cycle');
  };

  return (
    <div>
      <Row className="mb-4">
        <Col>
          <h2>System Dashboard</h2>
          <p className="text-muted">Real-time inventory optimization and agent coordination</p>
        </Col>
        <Col xs="auto">
          <div className="d-flex gap-2">
            <Button variant="outline-warning" onClick={simulateDemandSpike}>
              Simulate Demand Spike
            </Button>
            <Button variant="outline-danger" onClick={simulateDelay}>
              Simulate Delay
            </Button>
            <Button variant="primary" onClick={triggerOptimization}>
              Trigger Optimization
            </Button>
          </div>
        </Col>
      </Row>

      {/* Key Metrics */}
      <Row className="mb-4">
        <Col md={3}>
          <MetricCard 
            label="Total Inventory Value" 
            value={`$${metrics.totalInventoryValue.toLocaleString()}`} 
            gradient="linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)" 
          />
        </Col>
        <Col md={3}>
          <MetricCard 
            label="Carbon Footprint" 
            value={`${metrics.totalCarbonFootprint}kg`} 
            gradient="linear-gradient(135deg, #11998e 0%, #38ef7d 100%)" 
          />
        </Col>
        <Col md={3}>
          <MetricCard 
            label="Service Level" 
            value={`${(metrics.serviceLevel * 100).toFixed(1)}%`} 
            gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)" 
          />
        </Col>
        <Col md={3}>
          <MetricCard 
            label="Optimization Cycles" 
            value={metrics.optimizationCyclesCompleted} 
            gradient="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)" 
          />
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        <Col md={8}>
          <Card>
            <Card.Header>
              <h5>Demand vs Forecast (24h)</h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={demandData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis domain={[0, 'dataMax + 50']} />
                  <Tooltip />
                  <Line type="monotone" dataKey="demand" stroke="#8884d8" strokeWidth={2} />
                  <Line type="monotone" dataKey="forecast" stroke="#82ca9d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card>
            <Card.Header>
              <h5>Warehouse Utilization</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <div className="d-flex justify-content-between">
                  <span>North Warehouse</span>
                  <Badge bg="success">78%</Badge>
                </div>
                <ProgressBar variant="success" now={78} className="mb-2" />
              </div>
              <div className="mb-3">
                <div className="d-flex justify-content-between">
                  <span>Central Warehouse</span>
                  <Badge bg="warning">65%</Badge>
                </div>
                <ProgressBar variant="warning" now={65} className="mb-2" />
              </div>
              <div className="mb-3">
                <div className="d-flex justify-content-between">
                  <span>South Warehouse</span>
                  <Badge bg="danger">92%</Badge>
                </div>
                <ProgressBar variant="danger" now={92} className="mb-2" />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5>Inventory Levels by Warehouse (7 days)</h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={inventoryData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="north" fill="#8884d8" />
                  <Bar dataKey="central" fill="#82ca9d" />
                  <Bar dataKey="south" fill="#ffc658" />
                </BarChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5>Agent Communication</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center">
                  <span>Messages Today</span>
                  <Badge bg="primary">{metrics.agentCommunicationVolume}</Badge>
                </div>
              </div>
              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center">
                  <span>Stockout Incidents</span>
                  <Badge bg="danger">{metrics.stockoutIncidents}</Badge>
                </div>
              </div>
              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center">
                  <span>Overstock Incidents</span>
                  <Badge bg="warning">{metrics.overstockIncidents}</Badge>
                </div>
              </div>
              <div className="mb-3">
                <div className="d-flex justify-content-between align-items-center">
                  <span>Cost Efficiency</span>
                  <Badge bg="success">{(metrics.costEfficiency * 100).toFixed(1)}%</Badge>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;