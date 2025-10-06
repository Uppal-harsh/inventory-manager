"""
Supply Agent - Monitors supply chains and manages supplier relationships
"""
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from models import Order, Supplier, AgentMessage, MessageType, AgentType
from agent_communication import AgentCommunication

logger = logging.getLogger(__name__)

class SupplyAgent(AgentCommunication):
    """Agent responsible for supply chain monitoring and supplier management"""
    
    def __init__(self, message_broker, suppliers: List[Supplier], warehouses: Dict[str, any]):
        super().__init__(AgentType.SUPPLY, message_broker)
        self.suppliers = {s.supplier_id: s for s in suppliers}
        self.warehouses = warehouses
        self.monitored_orders: Dict[str, Order] = {}
        self.supplier_reliability_history: Dict[str, List[float]] = {}
        self.alert_thresholds = {
            "low_stock": 0.2,  # 20% of min stock level
            "delivery_delay": 1.5,  # 150% of expected lead time
            "supplier_reliability": 0.7  # 70% reliability threshold
        }
        
    def _setup_message_handlers(self):
        """Set up message handlers for supply agent"""
        self.register_handler(MessageType.DEMAND_FORECAST, self._handle_demand_forecast)
        self.register_handler(MessageType.LOGISTICS_REQUEST, self._handle_logistics_request)
        self.register_handler(MessageType.INVENTORY_UPDATE, self._handle_inventory_update)
    
    async def start(self):
        """Start the supply agent"""
        await super().start()
        # Start the monitoring loop
        asyncio.create_task(self._monitoring_loop())
        logger.info("Supply Agent started")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for supply chain"""
        while True:
            try:
                await self._check_supplier_reliability()
                await self._monitor_order_status()
                await self._check_stock_levels()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in supply monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _check_supplier_reliability(self):
        """Monitor supplier reliability and performance"""
        for supplier_id, supplier in self.suppliers.items():
            # Simulate reliability tracking
            current_reliability = supplier.reliability_score
            
            # Add some variation based on current conditions
            if supplier.current_delay_days > 0:
                current_reliability *= 0.9  # Reduce reliability for delays
            
            # Update reliability history
            if supplier_id not in self.supplier_reliability_history:
                self.supplier_reliability_history[supplier_id] = []
            
            self.supplier_reliability_history[supplier_id].append(current_reliability)
            
            # Keep only recent history (last 30 days)
            if len(self.supplier_reliability_history[supplier_id]) > 30:
                self.supplier_reliability_history[supplier_id] = \
                    self.supplier_reliability_history[supplier_id][-30:]
            
            # Alert if reliability drops below threshold
            if current_reliability < self.alert_thresholds["supplier_reliability"]:
                await self.broadcast_message(
                    MessageType.SUPPLY_ALERT,
                    {
                        "alert_type": "supplier_reliability",
                        "supplier_id": supplier_id,
                        "reliability_score": current_reliability,
                        "threshold": self.alert_thresholds["supplier_reliability"],
                        "message": f"Supplier {supplier_id} reliability below threshold"
                    },
                    priority=2
                )
    
    async def _monitor_order_status(self):
        """Monitor outstanding orders and delivery status"""
        current_time = datetime.now()
        
        for order_id, order in self.monitored_orders.items():
            # Check for delayed orders
            expected_delivery = order.created_at + timedelta(days=order.lead_time_days)
            days_overdue = (current_time - expected_delivery).days
            
            if days_overdue > 0:
                # Order is delayed
                await self.broadcast_message(
                    MessageType.SUPPLY_ALERT,
                    {
                        "alert_type": "delivery_delay",
                        "order_id": order_id,
                        "sku_id": order.sku_id,
                        "supplier_id": order.supplier_id,
                        "days_overdue": days_overdue,
                        "message": f"Order {order_id} is {days_overdue} days overdue"
                    },
                    priority=3
                )
            
            # Check if order should be delivered
            elif current_time >= expected_delivery:
                # Simulate order delivery
                await self._process_order_delivery(order)
                del self.monitored_orders[order_id]
    
    async def _process_order_delivery(self, order: Order):
        """Process a delivered order"""
        logger.info(f"Processing delivery for order {order.order_id}")
        
        # Update inventory
        await self.broadcast_message(
            MessageType.INVENTORY_UPDATE,
            {
                "sku_id": order.sku_id,
                "warehouse_id": order.warehouse_id,
                "quantity_received": order.quantity,
                "order_id": order.order_id,
                "message": f"Received {order.quantity} units of {order.sku_id}"
            }
        )
        
        # Update supplier reliability based on delivery performance
        supplier = self.suppliers.get(order.supplier_id)
        if supplier:
            actual_lead_time = (datetime.now() - order.created_at).days
            expected_lead_time = order.lead_time_days
            
            if actual_lead_time <= expected_lead_time:
                # On-time delivery - improve reliability
                supplier.reliability_score = min(1.0, supplier.reliability_score + 0.01)
            else:
                # Late delivery - reduce reliability
                supplier.reliability_score = max(0.1, supplier.reliability_score - 0.02)
    
    async def _check_stock_levels(self):
        """Check inventory levels and trigger reorders if needed"""
        # This would typically check against actual inventory data
        # For simulation, we'll generate some alerts
        
        # Simulate low stock detection
        import random
        if random.random() < 0.1:  # 10% chance of low stock alert
            sku_id = f"SKU{random.randint(1, 10):03d}"
            warehouse_id = random.choice(list(self.warehouses.keys()))
            
            await self.broadcast_message(
                MessageType.SUPPLY_ALERT,
                {
                    "alert_type": "low_stock",
                    "sku_id": sku_id,
                    "warehouse_id": warehouse_id,
                    "current_stock": random.randint(1, 10),
                    "min_stock_level": 20,
                    "message": f"Low stock alert for {sku_id} in {warehouse_id}"
                },
                priority=3
            )
    
    async def _handle_demand_forecast(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle demand forecasts from demand agent"""
        content = message.content
        forecast = content.get("forecast", {})
        urgency = content.get("urgency", "low")
        
        sku_id = forecast.get("sku_id")
        forecasted_demand = forecast.get("forecasted_demand", 0)
        
        if sku_id and urgency in ["high", "medium"]:
            # Check if we need to trigger reorders based on forecast
            await self._evaluate_reorder_needs(sku_id, forecasted_demand, urgency)
        
        return {"status": "processed", "action_taken": urgency in ["high", "medium"]}
    
    async def _evaluate_reorder_needs(self, sku_id: str, forecasted_demand: float, urgency: str):
        """Evaluate if reorders are needed based on demand forecast"""
        # Find best supplier for this SKU
        best_supplier = self._find_best_supplier(sku_id)
        
        if best_supplier:
            # Calculate optimal order quantity
            order_quantity = self._calculate_optimal_order_quantity(sku_id, forecasted_demand)
            
            if order_quantity > 0:
                # Create order
                order = Order(
                    sku_id=sku_id,
                    warehouse_id="central",  # Default warehouse
                    supplier_id=best_supplier.supplier_id,
                    quantity=order_quantity,
                    unit_price=10.0,  # Simplified pricing
                    lead_time_days=best_supplier.lead_time_days + best_supplier.current_delay_days,
                    carbon_footprint=order_quantity * best_supplier.carbon_factor
                )
                
                self.monitored_orders[order.order_id] = order
                
                await self.broadcast_message(
                    MessageType.OPTIMIZATION_RESULT,
                    {
                        "sku_id": sku_id,
                        "recommended_action": "order",
                        "recommended_quantity": order_quantity,
                        "supplier_id": best_supplier.supplier_id,
                        "estimated_cost": order.total_cost,
                        "estimated_carbon_footprint": order.carbon_footprint,
                        "reasoning": f"High demand forecast ({forecasted_demand:.1f}) with {urgency} urgency"
                    }
                )
    
    def _find_best_supplier(self, sku_id: str) -> Optional[Supplier]:
        """Find the best supplier for a given SKU based on reliability, cost, and carbon footprint"""
        available_suppliers = [
            s for s in self.suppliers.values() 
            if sku_id in s.available_skus or not s.available_skus  # If no restrictions, assume available
        ]
        
        if not available_suppliers:
            return None
        
        # Score suppliers based on multiple factors
        best_supplier = None
        best_score = -1
        
        for supplier in available_suppliers:
            # Calculate composite score
            reliability_score = supplier.reliability_score
            cost_score = 1 / supplier.price_multiplier  # Lower price is better
            carbon_score = 1 / supplier.carbon_factor   # Lower carbon is better
            lead_time_score = 1 / (supplier.lead_time_days + supplier.current_delay_days + 1)
            
            composite_score = (
                0.4 * reliability_score +
                0.3 * cost_score +
                0.2 * carbon_score +
                0.1 * lead_time_score
            )
            
            if composite_score > best_score:
                best_score = composite_score
                best_supplier = supplier
        
        return best_supplier
    
    def _calculate_optimal_order_quantity(self, sku_id: str, forecasted_demand: float) -> int:
        """Calculate optimal order quantity using EOQ-like logic"""
        # Simplified EOQ calculation
        # In practice, this would consider holding costs, ordering costs, etc.
        
        base_quantity = max(50, int(forecasted_demand * 7))  # 1 week of demand
        return min(base_quantity, 500)  # Cap at 500 units
    
    async def _handle_logistics_request(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle logistics requests from logistics agent"""
        content = message.content
        request_type = content.get("request_type")
        
        if request_type == "inventory_transfer":
            # Evaluate if transfer is feasible and cost-effective
            from_warehouse = content.get("from_warehouse")
            to_warehouse = content.get("to_warehouse")
            sku_id = content.get("sku_id")
            quantity = content.get("quantity", 0)
            
            # Simulate transfer feasibility check
            feasible = quantity > 0 and from_warehouse != to_warehouse
            
            return {
                "status": "processed",
                "feasible": feasible,
                "estimated_cost": quantity * 2.0,  # $2 per unit transfer cost
                "estimated_carbon_footprint": quantity * 0.1  # Simplified carbon calculation
            }
        
        return {"status": "processed"}
    
    async def _handle_inventory_update(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle inventory updates"""
        content = message.content
        sku_id = content.get("sku_id")
        warehouse_id = content.get("warehouse_id")
        quantity_received = content.get("quantity_received", 0)
        
        logger.info(f"Inventory update: {quantity_received} units of {sku_id} received in {warehouse_id}")
        
        return {"status": "processed"}
    
    def simulate_supplier_delay(self, supplier_id: str, delay_days: int):
        """Simulate a supplier delay for testing"""
        if supplier_id in self.suppliers:
            self.suppliers[supplier_id].current_delay_days = delay_days
            logger.info(f"Simulated {delay_days}-day delay for supplier {supplier_id}")
    
    def get_supplier_summary(self) -> Dict[str, Any]:
        """Get summary of supplier status"""
        return {
            "total_suppliers": len(self.suppliers),
            "monitored_orders": len(self.monitored_orders),
            "avg_reliability": np.mean([s.reliability_score for s in self.suppliers.values()]) 
                           if self.suppliers else 0,
            "suppliers": {
                supplier_id: {
                    "name": supplier.name,
                    "reliability": supplier.reliability_score,
                    "current_delay": supplier.current_delay_days,
                    "carbon_factor": supplier.carbon_factor
                }
                for supplier_id, supplier in self.suppliers.items()
            }
        }
