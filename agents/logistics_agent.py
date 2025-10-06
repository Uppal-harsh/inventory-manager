"""
Logistics Agent - Optimizes shipping routes and inventory transfers
"""
import asyncio
from datetime import datetime, timedelta
from models import Shipment, Order, InventoryLevel, AgentMessage, MessageType, AgentType, OrderStatus
from typing import Dict, List, Optional, Tuple, Any
from agent_communication import AgentCommunication

logger = logging.getLogger(__name__)

class LogisticsAgent(AgentCommunication):
    """Agent responsible for logistics optimization and route planning"""
    
    def __init__(self, message_broker, warehouses: Dict[str, any]):
        super().__init__(AgentType.LOGISTICS, message_broker)
        self.warehouses = warehouses
        self.active_shipments: Dict[str, Shipment] = {}
        self.route_cache: Dict[str, Dict[str, float]] = {}  # Cache for route calculations
        self.optimization_history: List[Dict] = []
        
    def _setup_message_handlers(self):
        """Set up message handlers for logistics agent"""
        self.register_handler(MessageType.SUPPLY_ALERT, self._handle_supply_alert)
        self.register_handler(MessageType.DEMAND_FORECAST, self._handle_demand_forecast)
        self.register_handler(MessageType.INVENTORY_UPDATE, self._handle_inventory_update)
    
    async def start(self):
        """Start the logistics agent"""
        await super().start()
        # Initialize route cache
        await self._initialize_route_cache()
        # Start the optimization loop
        asyncio.create_task(self._optimization_loop())
        logger.info("Logistics Agent started")
    
    async def _initialize_route_cache(self):
        """Initialize route distances between warehouses"""
        warehouse_ids = list(self.warehouses.keys())
        
        for i, warehouse1 in enumerate(warehouse_ids):
            self.route_cache[warehouse1] = {}
            for j, warehouse2 in enumerate(warehouse_ids):
                if i != j:
                    # Calculate distance between warehouses (simplified)
                    distance = self._calculate_distance(
                        self.warehouses[warehouse1].location,
                        self.warehouses[warehouse2].location
                    )
                    self.route_cache[warehouse1][warehouse2] = distance
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance between two locations using Haversine formula"""
        import math
        
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    async def _optimization_loop(self):
        """Main optimization loop for logistics"""
        while True:
            try:
                await self._optimize_inventory_distribution()
                await self._optimize_shipment_routes()
                await self._monitor_active_shipments()
                await asyncio.sleep(120)  # Optimize every 2 minutes
            except Exception as e:
                logger.error(f"Error in logistics optimization loop: {e}")
                await asyncio.sleep(10)
    
    async def _optimize_inventory_distribution(self):
        """Optimize inventory distribution across warehouses"""
        # Simulate inventory rebalancing logic
        import random
        
        if random.random() < 0.3:  # 30% chance of optimization opportunity
            # Find warehouses with imbalance
            from_warehouse = random.choice(list(self.warehouses.keys()))
            to_warehouse = random.choice([w for w in self.warehouses.keys() if w != from_warehouse])
            sku_id = f"SKU{random.randint(1, 10):03d}"
            transfer_quantity = random.randint(10, 50)
            
            # Request transfer from supply agent
            response = await self.send_message(
                AgentType.SUPPLY,
                MessageType.LOGISTICS_REQUEST,
                {
                    "request_type": "inventory_transfer",
                    "from_warehouse": from_warehouse,
                    "to_warehouse": to_warehouse,
                    "sku_id": sku_id,
                    "quantity": transfer_quantity,
                    "reason": "inventory_balancing"
                },
                requires_response=True
            )
            
            if response and response.get("feasible"):
                await self._execute_inventory_transfer(
                    from_warehouse, to_warehouse, sku_id, transfer_quantity
                )
    
    async def _execute_inventory_transfer(self, from_warehouse: str, to_warehouse: str, 
                                        sku_id: str, quantity: int):
        """Execute an inventory transfer between warehouses"""
        # Create shipment
        shipment = Shipment(
            from_warehouse=from_warehouse,
            to_warehouse=to_warehouse,
            orders=[],  # No external orders, just internal transfer
            status=OrderStatus.PENDING
        )
        
        # Calculate delivery time based on distance
        distance = self.route_cache.get(from_warehouse, {}).get(to_warehouse, 100)
        estimated_hours = distance / 80  # Assume 80 km/h average speed
        shipment.estimated_arrival = datetime.now() + timedelta(hours=estimated_hours)
        
        # Calculate carbon footprint
        shipment.carbon_footprint = distance * quantity * 0.02  # 0.02 kg CO2 per km per unit
        
        self.active_shipments[shipment.shipment_id] = shipment
        
        logger.info(f"Executing transfer: {quantity} units of {sku_id} from {from_warehouse} to {to_warehouse}")
        
        # Broadcast transfer information
        await self.broadcast_message(
            MessageType.LOGISTICS_REQUEST,
            {
                "action": "inventory_transfer",
                "shipment_id": shipment.shipment_id,
                "from_warehouse": from_warehouse,
                "to_warehouse": to_warehouse,
                "sku_id": sku_id,
                "quantity": quantity,
                "estimated_arrival": shipment.estimated_arrival,
                "carbon_footprint": shipment.carbon_footprint
            }
        )
        
        # Record optimization
        self.optimization_history.append({
            "timestamp": datetime.now(),
            "action": "inventory_transfer",
            "from_warehouse": from_warehouse,
            "to_warehouse": to_warehouse,
            "quantity": quantity,
            "carbon_savings": shipment.carbon_footprint * 0.1  # Assume 10% savings
        })
    
    async def _optimize_shipment_routes(self):
        """Optimize shipment routes for cost and carbon efficiency"""
        # Simulate route optimization
        import random
        
        if random.random() < 0.2:  # 20% chance of route optimization
            # Find potential route improvements
            route_improvements = []
            
            for shipment_id, shipment in self.active_shipments.items():
                if shipment.status == OrderStatus.SHIPPED:
                    # Check for route optimization opportunities
                    current_route = shipment.from_warehouse
                    optimized_route = self._find_optimized_route(shipment)
                    
                    if optimized_route != current_route:
                        savings = self._calculate_route_savings(shipment, optimized_route)
                        route_improvements.append({
                            "shipment_id": shipment_id,
                            "current_route": current_route,
                            "optimized_route": optimized_route,
                            "savings": savings
                        })
            
            # Apply route improvements
            for improvement in route_improvements:
                await self._apply_route_optimization(improvement)
    
    def _find_optimized_route(self, shipment: Shipment) -> Optional[str]:
        """Find an optimized route for a shipment"""
        # Simplified route optimization logic
        available_routes = [w for w in self.warehouses.keys() if w != shipment.from_warehouse]
        
        if not available_routes:
            return None
        
        # Find route with minimum carbon footprint
        best_route = None
        min_carbon = float('inf')
        
        for route in available_routes:
            distance = self.route_cache.get(shipment.from_warehouse, {}).get(route, 1000)
            carbon_per_unit = distance * 0.02
            
            if carbon_per_unit < min_carbon:
                min_carbon = carbon_per_unit
                best_route = route
        
        return best_route
    
    def _calculate_route_savings(self, shipment: Shipment, optimized_route: str) -> Dict[str, float]:
        """Calculate savings from route optimization"""
        current_distance = self.route_cache.get(shipment.from_warehouse, {}).get(shipment.to_warehouse, 100)
        optimized_distance = self.route_cache.get(shipment.from_warehouse, {}).get(optimized_route, 100)
        
        distance_savings = current_distance - optimized_distance
        carbon_savings = distance_savings * len(shipment.orders) * 0.02
        cost_savings = distance_savings * 0.5  # $0.5 per km savings
        
        return {
            "distance_savings": distance_savings,
            "carbon_savings": carbon_savings,
            "cost_savings": cost_savings
        }
    
    async def _apply_route_optimization(self, improvement: Dict):
        """Apply route optimization to a shipment"""
        shipment_id = improvement["shipment_id"]
        shipment = self.active_shipments.get(shipment_id)
        
        if shipment:
            # Update shipment route
            shipment.to_warehouse = improvement["optimized_route"]
            shipment.carbon_footprint *= 0.9  # Assume 10% carbon reduction
            
            logger.info(f"Applied route optimization to shipment {shipment_id}")
            
            # Broadcast optimization result
            await self.broadcast_message(
                MessageType.OPTIMIZATION_RESULT,
                {
                    "shipment_id": shipment_id,
                    "optimization_type": "route_optimization",
                    "savings": improvement["savings"],
                    "new_route": improvement["optimized_route"]
                }
            )
    
    async def _monitor_active_shipments(self):
        """Monitor active shipments and update their status"""
        current_time = datetime.now()
        
        for shipment_id, shipment in list(self.active_shipments.items()):
            if shipment.status == OrderStatus.SHIPPED and shipment.estimated_arrival:
                if current_time >= shipment.estimated_arrival:
                    # Shipment arrived
                    shipment.status = OrderStatus.DELIVERED
                    
                    # Broadcast delivery notification
                    await self.broadcast_message(
                        MessageType.INVENTORY_UPDATE,
                        {
                            "shipment_id": shipment_id,
                            "status": "delivered",
                            "to_warehouse": shipment.to_warehouse,
                            "carbon_footprint": shipment.carbon_footprint,
                            "message": f"Shipment {shipment_id} delivered to {shipment.to_warehouse}"
                        }
                    )
                    
                    # Remove from active shipments
                    del self.active_shipments[shipment_id]
    
    async def _handle_supply_alert(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle supply alerts that may require logistics intervention"""
        content = message.content
        alert_type = content.get("alert_type")
        
        if alert_type == "low_stock":
            sku_id = content.get("sku_id")
            warehouse_id = content.get("warehouse_id")
            
            # Check if other warehouses have excess stock
            excess_warehouse = await self._find_excess_stock_warehouse(sku_id, warehouse_id)
            
            if excess_warehouse:
                transfer_quantity = content.get("min_stock_level", 20) - content.get("current_stock", 0)
                
                await self._execute_inventory_transfer(
                    excess_warehouse, warehouse_id, sku_id, transfer_quantity
                )
                
                return {
                    "status": "processed",
                    "action_taken": "inventory_transfer",
                    "from_warehouse": excess_warehouse,
                    "quantity": transfer_quantity
                }
        
        return {"status": "processed"}
    
    async def _find_excess_stock_warehouse(self, sku_id: str, exclude_warehouse: str) -> Optional[str]:
        """Find a warehouse with excess stock of a SKU"""
        # Simplified logic - in practice would check actual inventory levels
        import random
        
        available_warehouses = [w for w in self.warehouses.keys() if w != exclude_warehouse]
        
        if available_warehouses and random.random() < 0.7:  # 70% chance of finding excess stock
            return random.choice(available_warehouses)
        
        return None
    
    async def _handle_demand_forecast(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle demand forecasts for proactive logistics planning"""
        content = message.content
        forecast = content.get("forecast", {})
        urgency = content.get("urgency", "low")
        
        if urgency == "high":
            # Proactively prepare logistics for high demand
            sku_id = forecast.get("sku_id")
            
            # Check if we need to pre-position inventory
            await self._evaluate_prepositioning(sku_id, forecast.get("forecasted_demand", 0))
        
        return {"status": "processed"}
    
    async def _evaluate_prepositioning(self, sku_id: str, forecasted_demand: float):
        """Evaluate if inventory prepositioning is needed"""
        # Simplified prepositioning logic
        if forecasted_demand > 20:  # High demand threshold
            # Find best warehouse for prepositioning
            target_warehouse = await self._find_best_prepositioning_warehouse(sku_id)
            
            if target_warehouse:
                preposition_quantity = int(forecasted_demand * 0.5)  # Preposition 50% of forecasted demand
                
                await self.broadcast_message(
                    MessageType.LOGISTICS_REQUEST,
                    {
                        "action": "prepositioning_recommendation",
                        "sku_id": sku_id,
                        "target_warehouse": target_warehouse,
                        "quantity": preposition_quantity,
                        "reason": "high_demand_forecast"
                    }
                )
    
    async def _find_best_prepositioning_warehouse(self, sku_id: str) -> Optional[str]:
        """Find the best warehouse for prepositioning inventory"""
        # Simplified logic - would consider demand patterns, capacity, etc.
        import random
        
        available_warehouses = list(self.warehouses.keys())
        if available_warehouses:
            return random.choice(available_warehouses)
        
        return None
    
    async def _handle_inventory_update(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle inventory updates"""
        content = message.content
        shipment_id = content.get("shipment_id")
        
        if shipment_id and shipment_id in self.active_shipments:
            shipment = self.active_shipments[shipment_id]
            shipment.status = OrderStatus.DELIVERED
            
            logger.info(f"Shipment {shipment_id} status updated to delivered")
        
        return {"status": "processed"}
    
    def get_logistics_summary(self) -> Dict[str, Any]:
        """Get summary of logistics operations"""
        total_distance = sum(
            self.route_cache.get(shipment.from_warehouse, {}).get(shipment.to_warehouse, 0)
            for shipment in self.active_shipments.values()
        )
        
        total_carbon = sum(shipment.carbon_footprint for shipment in self.active_shipments.values())
        
        return {
            "active_shipments": len(self.active_shipments),
            "total_distance_km": total_distance,
            "total_carbon_footprint": total_carbon,
            "optimization_cycles": len(self.optimization_history),
            "route_cache_size": len(self.route_cache),
            "recent_optimizations": self.optimization_history[-5:] if self.optimization_history else []
        }
