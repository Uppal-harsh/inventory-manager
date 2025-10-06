
import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Table, Badge, Button, Form, Modal } from 'react-bootstrap';
import { useSocket } from '../contexts/SocketContext';

const InventoryView = ({ addAlert }) => {
  const { connected, messages, sendMessage } = useSocket();
  const [inventory, setInventory] = useState({});
  const [warehouses, setWarehouses] = useState([
    { id: 'north', name: 'North Warehouse', location: 'NYC', capacity: 1000, utilization: 78 },
    { id: 'central', name: 'Central Warehouse', location: 'Chicago', capacity: 1200, utilization: 65 },
    { id: 'south', name: 'South Warehouse', location: 'Houston', capacity: 800, utilization: 92 }
  ]);
  const [showReorderModal, setShowReorderModal] = useState(false);
  const [selectedSKU, setSelectedSKU] = useState(null);
  const [reorderQuantity, setReorderQuantity] = useState(0);

  // Sample inventory data
  useEffect(() => {
    const sampleInventory = {
      'SKU001': {
        name: 'Premium Widget',
        category: 'Electronics',
        unitCost: 25.0,
        currentStock: { north: 45, central: 78, south: 23 },
        minStock: 20,
        maxStock: 200,
        demandRate: 5.0,
        status: 'normal'
      },
      'SKU002': {
        name: 'Basic Component',
        category: 'Hardware',
        unitCost: 12.0,
        currentStock: { north: 156, central: 234, south: 89 },
        minStock: 30,
        maxStock: 300,
        demandRate: 8.0,
        status: 'normal'
      },
      'SKU003': {
        name: 'Luxury Item',
        category: 'Premium',
        unitCost: 150.0,
        currentStock: { north: 3, central: 7, south: 2 },
        minStock: 5,
        maxStock: 50,
        demandRate: 2.0,
        status: 'low_stock'
      },
      'SKU004': {
        name: 'Standard Part',
        category: 'Mechanical',
        unitCost: 8.0,
        currentStock: { north: 234, central: 345, south: 156 },
        minStock: 40,
        maxStock: 400,
        demandRate: 10.0,
        status: 'normal'
      },
      'SKU005': {
        name: 'Specialty Tool',
        category: 'Tools',
        unitCost: 75.0,
        currentStock: { north: 67, central: 89, south: 45 },
        minStock: 10,
        maxStock: 100,
        demandRate: 3.0,
        status: 'normal'
      }
    };
    setInventory(sampleInventory);
  }, []);

  useEffect(() => {
    // Process inventory updates from WebSocket
    messages.forEach(message => {
      if (message.type === 'inventory_update') {
        const data = message.data;
        setInventory(prev => ({
          ...prev,
          [data.sku_id]: {
            ...prev[data.sku_id],
            currentStock: {
              ...prev[data.sku_id]?.currentStock,
              [data.warehouse_id]: data.current_stock
            }
          }
        }));
        addAlert('info', `Inventory updated for ${data.sku_id} in ${data.warehouse_id}`);
      }
    });
  }, [messages, addAlert]);

  const getStockStatus = (sku, warehouseId) => {
    const stock = sku.currentStock[warehouseId] || 0;
    if (stock <= sku.minStock) return 'low_stock';
    if (stock >= sku.maxStock * 0.9) return 'overstock';
    return 'normal';
  };

  const getStockBadge = (status) => {
    const variants = {
      low_stock: { bg: 'danger', text: 'Low Stock' },
      overstock: { bg: 'warning', text: 'Overstock' },
      normal: { bg: 'success', text: 'Normal' }
    };
    const variant = variants[status] || variants.normal;
    return <Badge bg={variant.bg}>{variant.text}</Badge>;
  };

  const handleReorder = (skuId) => {
    setSelectedSKU(skuId);
    setReorderQuantity(inventory[skuId].minStock * 2);
    setShowReorderModal(true);
  };

  const confirmReorder = () => {
    if (selectedSKU && reorderQuantity > 0) {
      sendMessage('create_reorder', {
        sku_id: selectedSKU,
        quantity: reorderQuantity,
        priority: 'high'
      });
      addAlert('success', `Reorder request sent for ${selectedSKU}: ${reorderQuantity} units`);
      setShowReorderModal(false);
    }
  };

  const getTotalStock = (sku) => {
    return Object.values(sku.currentStock).reduce((sum, stock) => sum + stock, 0);
  };

  const getTotalValue = (sku) => {
    return getTotalStock(sku) * sku.unitCost;
  };

  return (
    <div>
      <Row className="mb-4">
        <Col>
          <h2>Inventory Management</h2>
          <p className="text-muted">Real-time inventory levels across all warehouses</p>
        </Col>
      </Row>

      {/* Warehouse Summary */}
      <Row className="mb-4">
        {warehouses.map(warehouse => (
          <Col md={4} key={warehouse.id}>
            <Card>
              <Card.Header>
                <h5>{warehouse.name}</h5>
                <small className="text-muted">{warehouse.location}</small>
              </Card.Header>
              <Card.Body>
                <div className="mb-2">
                  <strong>Capacity:</strong> {warehouse.capacity} units
                </div>
                <div className="mb-2">
                  <strong>Utilization:</strong> {warehouse.utilization}%
                </div>
                <div className="mb-2">
                  <strong>Available:</strong> {warehouse.capacity - Math.round(warehouse.capacity * warehouse.utilization / 100)} units
                </div>
                <Badge bg={warehouse.utilization > 80 ? 'danger' : warehouse.utilization > 60 ? 'warning' : 'success'}>
                  {warehouse.utilization > 80 ? 'High' : warehouse.utilization > 60 ? 'Medium' : 'Low'} Utilization
                </Badge>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Inventory Table */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5>SKU Inventory Levels</h5>
            </Card.Header>
            <Card.Body>
              <Table responsive striped hover>
                <thead>
                  <tr>
                    <th>SKU ID</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Unit Cost</th>
                    <th>North</th>
                    <th>Central</th>
                    <th>South</th>
                    <th>Total</th>
                    <th>Value</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(inventory).map(([skuId, sku]) => {
                    const totalStock = getTotalStock(sku);
                    const totalValue = getTotalValue(sku);
                    const overallStatus = totalStock <= sku.minStock ? 'low_stock' : 
                                        totalStock >= sku.maxStock * 0.9 ? 'overstock' : 'normal';
                    
                    return (
                      <tr key={skuId}>
                        <td><strong>{skuId}</strong></td>
                        <td>{sku.name}</td>
                        <td><Badge bg="secondary">{sku.category}</Badge></td>
                        <td>${sku.unitCost}</td>
                        <td>
                          <span className={getStockStatus(sku, 'north') === 'low_stock' ? 'text-danger fw-bold' : ''}>
                            {sku.currentStock.north || 0}
                          </span>
                        </td>
                        <td>
                          <span className={getStockStatus(sku, 'central') === 'low_stock' ? 'text-danger fw-bold' : ''}>
                            {sku.currentStock.central || 0}
                          </span>
                        </td>
                        <td>
                          <span className={getStockStatus(sku, 'south') === 'low_stock' ? 'text-danger fw-bold' : ''}>
                            {sku.currentStock.south || 0}
                          </span>
                        </td>
                        <td><strong>{totalStock}</strong></td>
                        <td>${totalValue.toLocaleString()}</td>
                        <td>{getStockBadge(overallStatus)}</td>
                        <td>
                          {overallStatus === 'low_stock' && (
                            <Button 
                              size="sm" 
                              variant="warning" 
                              onClick={() => handleReorder(skuId)}
                            >
                              Reorder
                            </Button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Reorder Modal */}
      <Modal show={showReorderModal} onHide={() => setShowReorderModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create Reorder Request</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedSKU && inventory[selectedSKU] && (
            <>
              <p><strong>SKU:</strong> {selectedSKU} - {inventory[selectedSKU].name}</p>
              <p><strong>Current Stock:</strong> {getTotalStock(inventory[selectedSKU])}</p>
              <p><strong>Min Stock Level:</strong> {inventory[selectedSKU].minStock}</p>
              <p><strong>Unit Cost:</strong> ${inventory[selectedSKU].unitCost}</p>
              
              <Form.Group className="mb-3">
                <Form.Label>Reorder Quantity</Form.Label>
                <Form.Control
                  type="number"
                  value={reorderQuantity}
                  onChange={(e) => setReorderQuantity(parseInt(e.target.value) || 0)}
                  min={1}
                  max={inventory[selectedSKU].maxStock}
                />
              </Form.Group>
              
              <p><strong>Estimated Cost:</strong> ${(reorderQuantity * inventory[selectedSKU].unitCost).toLocaleString()}</p>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowReorderModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={confirmReorder}>
            Create Reorder
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default InventoryView;
