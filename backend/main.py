"""
FastAPI Backend for Autonomous Inventory Orchestrator
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import *
from agent_communication import MessageBroker
from agents.demand_agent import DemandAgent
from config import SIMULATION_CONFIG, SIMULATION_PARAMS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
message_broker = MessageBroker()
agents = {}
connected_clients = []
simulation_data = {
    "warehouses": {},
    "inventory": {},
    "orders": [],
    "metrics": {}
}

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: dict):
        if self.active_connections:
            message_str = json.dumps(message, default=str)
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Autonomous Inventory Orchestrator...")
    
    # Initialize simulation data
    await initialize_simulation_data()
    
    # Initialize agents
    await initialize_agents()
    
    # Start simulation loop
    asyncio.create_task(simulation_loop())
    
    yield
    
    logger.info("Shutting down Autonomous Inventory Orchestrator...")

app = FastAPI(
    title="Autonomous Inventory Orchestrator",
    description="AI-powered inventory management system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def initialize_simulation_data():
    """Initialize simulation data from config"""
    global simulation_data
    
    # Initialize warehouses
    for warehouse_config in SIMULATION_CONFIG["warehouses"]:
        warehouse = Warehouse(
            warehouse_id=warehouse_config.name.lower().replace("_", "_"),
            name=warehouse_config.name,
            location=warehouse_config.location,
            capacity=warehouse_config.capacity,
            carbon_factor=warehouse_config.carbon_factor
        )
        simulation_data["warehouses"][warehouse.warehouse_id] = warehouse
    
    # Initialize inventory with random stock levels
    for sku_config in SIMULATION_CONFIG["skus"]:
        sku = SKU(
            sku_id=sku_config.sku_id,
            name=sku_config.name,
            category=sku_config.category,
            base_demand_rate=sku_config.base_demand_rate,
            lead_time_days=sku_config.lead_time_days,
            unit_cost=sku_config.unit_cost,
            storage_cost_per_day=sku_config.storage_cost_per_day,
            stockout_cost=sku_config.stockout_cost,
            min_stock_level=sku_config.min_stock_level,
            max_stock_level=sku_config.max_stock_level
        )
        
        # Initialize inventory levels for each warehouse
        for warehouse_id in simulation_data["warehouses"]:
            inventory_level = InventoryLevel(
                sku_id=sku.sku_id,
                warehouse_id=warehouse_id,
                current_stock=max(sku.min_stock_level, 
                                int(sku.max_stock_level * 0.6 + (sku.max_stock_level * 0.4 * (hash(sku.sku_id + warehouse_id) % 100) / 100))),
                reserved_stock=0
            )
            simulation_data["inventory"][f"{sku.sku_id}_{warehouse_id}"] = inventory_level

async def initialize_agents():
    """Initialize all agents"""
    global agents
    
    # Create SKU dictionary for demand agent
    skus = {}
    for sku_config in SIMULATION_CONFIG["skus"]:
        sku = SKU(
            sku_id=sku_config.sku_id,
            name=sku_config.name,
            category=sku_config.category,
            base_demand_rate=sku_config.base_demand_rate,
            lead_time_days=sku_config.lead_time_days,
            unit_cost=sku_config.unit_cost,
            storage_cost_per_day=sku_config.storage_cost_per_day,
            stockout_cost=sku_config.stockout_cost,
            min_stock_level=sku_config.min_stock_level,
            max_stock_level=sku_config.max_stock_level
        )
        skus[sku.sku_id] = sku
    
    # Initialize demand agent
    agents["demand"] = DemandAgent(message_broker, skus)
    await agents["demand"].start()
    
    logger.info("All agents initialized successfully")

async def simulation_loop():
    """Main simulation loop"""
    while True:
        try:
            # Update simulation metrics
            await update_system_metrics()
            
            # Broadcast metrics to clients
            await manager.broadcast({
                "type": "system_metrics",
                "data": simulation_data["metrics"]
            })
            
            # Simulate random events
            await simulate_random_events()
            
            await asyncio.sleep(SIMULATION_PARAMS["time_step_minutes"] * 60)
            
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
            await asyncio.sleep(10)

async def update_system_metrics():
    """Update system-wide metrics"""
    global simulation_data
    
    # Calculate total inventory value
    total_value = 0
    total_carbon = 0
    stockout_incidents = 0
    overstock_incidents = 0
    
    for inventory_key, inventory in simulation_data["inventory"].items():
        sku_id = inventory.sku_id
        sku_config = next((s for s in SIMULATION_CONFIG["skus"] if s.sku_id == sku_id), None)
        
        if sku_config:
            total_value += inventory.current_stock * sku_config.unit_cost
            
            # Check for stockouts and overstock
            if inventory.current_stock <= sku_config.min_stock_level:
                stockout_incidents += 1
            elif inventory.current_stock >= sku_config.max_stock_level * 0.9:
                overstock_incidents += 1
    
    # Calculate service level (simplified)
    total_inventory_items = len(simulation_data["inventory"])
    service_level = max(0, 1 - (stockout_incidents / total_inventory_items))
    
    simulation_data["metrics"] = {
        "totalInventoryValue": total_value,
        "totalCarbonFootprint": 2450 + (hash(str(datetime.now())) % 100),  # Simulate variation
        "serviceLevel": service_level,
        "stockoutIncidents": stockout_incidents,
        "overstockIncidents": overstock_incidents,
        "costEfficiency": 0.85 + (hash(str(datetime.now())) % 15) / 100,
        "agentCommunicationVolume": message_broker.get_communication_metrics()["total_messages"],
        "optimizationCyclesCompleted": len(simulation_data.get("orders", []))
    }

async def simulate_random_events():
    """Simulate random demand spikes and delays"""
    import random
    
    # Simulate demand spike
    if random.random() < SIMULATION_PARAMS["demand_spike_probability"]:
        sku_id = random.choice(SIMULATION_CONFIG["skus"]).sku_id
        multiplier = random.uniform(1.5, 3.0)
        
        # Update SKU demand multiplier
        if "demand" in agents:
            agents["demand"].simulate_demand_spike(sku_id, multiplier, 24)
        
        await manager.broadcast({
            "type": "demand_spike",
            "data": {
                "sku_id": sku_id,
                "multiplier": multiplier,
                "timestamp": datetime.now()
            }
        })
    
    # Simulate delay
    if random.random() < SIMULATION_PARAMS["delay_probability"]:
        supplier_id = random.choice(SIMULATION_CONFIG["suppliers"]).supplier_id
        delay_days = random.randint(1, SIMULATION_PARAMS["max_delay_days"])
        
        await manager.broadcast({
            "type": "supplier_delay",
            "data": {
                "supplier_id": supplier_id,
                "delay_days": delay_days,
                "timestamp": datetime.now()
            }
        })

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "simulate_demand_spike":
                sku_id = message.get("data", {}).get("sku_id")
                multiplier = message.get("data", {}).get("multiplier", 2.0)
                duration = message.get("data", {}).get("duration_hours", 24)
                
                if sku_id and "demand" in agents:
                    agents["demand"].simulate_demand_spike(sku_id, multiplier, duration)
                    await manager.broadcast({
                        "type": "demand_spike_simulation",
                        "data": {
                            "sku_id": sku_id,
                            "multiplier": multiplier,
                            "duration_hours": duration
                        }
                    })
            
            elif message.get("type") == "simulate_delay":
                supplier_id = message.get("data", {}).get("supplier_id")
                delay_days = message.get("data", {}).get("delay_days", 3)
                
                await manager.broadcast({
                    "type": "delay_simulation",
                    "data": {
                        "supplier_id": supplier_id,
                        "delay_days": delay_days
                    }
                })
            
            elif message.get("type") == "trigger_optimization":
                # Trigger system-wide optimization
                await manager.broadcast({
                    "type": "optimization_triggered",
                    "data": {
                        "timestamp": datetime.now(),
                        "message": "System-wide optimization cycle initiated"
                    }
                })
            
            elif message.get("type") == "create_reorder":
                sku_id = message.get("data", {}).get("sku_id")
                quantity = message.get("data", {}).get("quantity", 0)
                
                # Create a new order
                order = Order(
                    sku_id=sku_id,
                    warehouse_id="central",  # Default warehouse
                    supplier_id="SUP001",   # Default supplier
                    quantity=quantity,
                    unit_price=next((s.unit_cost for s in SIMULATION_CONFIG["skus"] if s.sku_id == sku_id), 10.0),
                    lead_time_days=7,
                    carbon_footprint=quantity * 0.5  # Simplified calculation
                )
                
                simulation_data["orders"].append(order)
                
                await manager.broadcast({
                    "type": "reorder_created",
                    "data": {
                        "order": order.dict(),
                        "message": f"Reorder created for {sku_id}: {quantity} units"
                    }
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# REST API endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/inventory")
async def get_inventory():
    return {"inventory": list(simulation_data["inventory"].values())}

@app.get("/api/warehouses")
async def get_warehouses():
    return {"warehouses": list(simulation_data["warehouses"].values())}

@app.get("/api/metrics")
async def get_metrics():
    return simulation_data["metrics"]

@app.get("/api/agents")
async def get_agents():
    agent_status = {}
    for agent_name, agent in agents.items():
        if hasattr(agent, 'get_forecast_summary'):
            agent_status[agent_name] = agent.get_forecast_summary()
        else:
            agent_status[agent_name] = {"status": "active", "last_activity": datetime.now()}
    
    return {"agents": agent_status}

# Serve React app
@app.get("/")
async def serve_react_app():
    return FileResponse("build/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
