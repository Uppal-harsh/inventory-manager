import React, { useState, useEffect } from 'react';
import { Row, Col, Card, ProgressBar, Badge, ListGroup, Table } from 'react-bootstrap';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { useSocket } from '../contexts/SocketContext';

const SustainabilityMetrics = ({ addAlert }) => {
  const { connected, messages } = useSocket();
  const [sustainabilityData, setSustainabilityData] = useState({
    totalCarbonFootprint: 2450,
    carbonReduction: 12.5,
    sustainableSuppliers: 3,
    totalSuppliers: 4,
    renewableEnergyUsage: 78,
    wasteReduction: 23,
    localSourcing: 65,
    carbonByCategory: [
      { name: 'Transportation', value: 1200, color: '#8884d8' },
      { name: 'Warehousing', value: 650, color: '#82ca9d' },
      { name: 'Packaging', value: 400, color: '#ffc658' },
      { name: 'Processing', value: 200, color: '#ff7c7c' }
    ],
    supplierRatings: [
      { name: 'East Coast Supply', carbonRating: 85, distance: 150, sustainability: 90 },
      { name: 'Central Distributors', carbonRating: 78, distance: 300, sustainability: 75 },
      { name: 'Southern Logistics', carbonRating: 82, distance: 200, sustainability: 85 },
      { name: 'West Coast Wholesale', carbonRating: 65, distance: 800, sustainability: 60 }
    ],
    monthlyTrends: [
      { month: 'Jan', carbon: 2800, reduction: 8 },
      { month: 'Feb', carbon: 2650, reduction: 12 },
      { month: 'Mar', carbon: 2500, reduction: 15 },
      { month: 'Apr', carbon: 2450, reduction: 18 },
      { month: 'May', carbon: 2400, reduction: 20 },
      { month: 'Jun', carbon: 2350, reduction: 22 }
    ]
  });

  useEffect(() => {
    // Process sustainability updates from WebSocket
    messages.forEach(message => {
      if (message.type === 'sustainability_update') {
        setSustainabilityData(prev => ({
          ...prev,
          ...message.data
        }));
        addAlert('success', 'Sustainability metrics updated');
      }
    });
  }, [messages, addAlert]);

  const getCarbonBadge = (rating) => {
    if (rating >= 80) return <Badge bg="success">Excellent</Badge>;
    if (rating >= 60) return <Badge bg="warning">Good</Badge>;
    return <Badge bg="danger">Needs Improvement</Badge>;
  };

  const getDistanceBadge = (distance) => {
    if (distance <= 200) return <Badge bg="success">Local</Badge>;
    if (distance <= 500) return <Badge bg="warning">Regional</Badge>;
    return <Badge bg="danger">Long Distance</Badge>;
  };

  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div>
      <Row className="mb-4">
        <Col>
          <h2>Sustainability Metrics</h2>
          <p className="text-muted">Carbon footprint optimization and environmental impact tracking</p>
        </Col>
      </Row>

      {/* Key Sustainability Metrics */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="metric-card text-white" style={{background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'}}>
            <Card.Body>
              <div className="metric-value">{sustainabilityData.totalCarbonFootprint}kg</div>
              <div className="metric-label">Total Carbon Footprint</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="metric-card text-white" style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}>
            <Card.Body>
              <div className="metric-value">{sustainabilityData.carbonReduction}%</div>
              <div className="metric-label">Carbon Reduction</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="metric-card text-white" style={{background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}}>
            <Card.Body>
              <div className="metric-value">{sustainabilityData.sustainableSuppliers}/{sustainabilityData.totalSuppliers}</div>
              <div className="metric-label">Sustainable Suppliers</div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="metric-card text-white" style={{background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}}>
            <Card.Body>
              <div className="metric-value">{sustainabilityData.renewableEnergyUsage}%</div>
              <div className="metric-label">Renewable Energy</div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Carbon Footprint Breakdown */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5>Carbon Footprint by Category</h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={sustainabilityData.carbonByCategory}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sustainabilityData.carbonByCategory.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5>Environmental Impact</h5>
            </Card.Header>
            <Card.Body>
              <div className="mb-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>Waste Reduction</span>
                  <Badge bg="success">{sustainabilityData.wasteReduction}%</Badge>
                </div>
                <ProgressBar variant="success" now={sustainabilityData.wasteReduction} />
              </div>
              
              <div className="mb-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>Local Sourcing</span>
                  <Badge bg="info">{sustainabilityData.localSourcing}%</Badge>
                </div>
                <ProgressBar variant="info" now={sustainabilityData.localSourcing} />
              </div>
              
              <div className="mb-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>Renewable Energy</span>
                  <Badge bg="success">{sustainabilityData.renewableEnergyUsage}%</Badge>
                </div>
                <ProgressBar variant="success" now={sustainabilityData.renewableEnergyUsage} />
              </div>
              
              <div className="alert alert-info">
                <small>
                  <strong>Carbon Offset:</strong> 245kg CO₂ equivalent offset through renewable energy investments
                </small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Supplier Sustainability Ratings */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Header>
              <h5>Supplier Sustainability Ratings</h5>
            </Card.Header>
            <Card.Body>
              <Table responsive striped>
                <thead>
                  <tr>
                    <th>Supplier</th>
                    <th>Carbon Rating</th>
                    <th>Distance (km)</th>
                    <th>Sustainability Score</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sustainabilityData.supplierRatings.map((supplier, index) => (
                    <tr key={index}>
                      <td><strong>{supplier.name}</strong></td>
                      <td>
                        <div className="d-flex align-items-center">
                          <ProgressBar 
                            variant={supplier.carbonRating >= 80 ? 'success' : supplier.carbonRating >= 60 ? 'warning' : 'danger'} 
                            now={supplier.carbonRating} 
                            style={{width: '60px', marginRight: '10px'}}
                          />
                          <span>{supplier.carbonRating}%</span>
                        </div>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <span>{supplier.distance}km</span>
                          <span className="ms-2">{getDistanceBadge(supplier.distance)}</span>
                        </div>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <ProgressBar 
                            variant={supplier.sustainability >= 80 ? 'success' : supplier.sustainability >= 60 ? 'warning' : 'danger'} 
                            now={supplier.sustainability} 
                            style={{width: '60px', marginRight: '10px'}}
                          />
                          <span>{supplier.sustainability}%</span>
                        </div>
                      </td>
                      <td>{getCarbonBadge(supplier.sustainability)}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Monthly Trends */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5>Monthly Carbon Footprint Trends</h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={sustainabilityData.monthlyTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="carbon" fill="#8884d8" name="Carbon Footprint (kg)" />
                </BarChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Sustainability Achievements */}
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>
              <h5>Sustainability Achievements</h5>
            </Card.Header>
            <Card.Body>
              <ListGroup variant="flush">
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>🌱 Carbon Neutral Operations</strong>
                    <div className="text-muted">Achieved through renewable energy and offset programs</div>
                  </div>
                  <Badge bg="success">Achieved</Badge>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>♻️ Zero Waste to Landfill</strong>
                    <div className="text-muted">All warehouse operations achieve zero waste targets</div>
                  </div>
                  <Badge bg="success">Achieved</Badge>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>🚛 Local Supplier Network</strong>
                    <div className="text-muted">75% of suppliers within 500km radius</div>
                  </div>
                  <Badge bg="warning">In Progress</Badge>
                </ListGroup.Item>
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>⚡ 100% Renewable Energy</strong>
                    <div className="text-muted">Transition all warehouses to renewable energy</div>
                  </div>
                  <Badge bg="info">Target: 2024</Badge>
                </ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SustainabilityMetrics;
