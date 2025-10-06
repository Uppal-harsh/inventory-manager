"""
Configuration settings for the Autonomous Inventory Orchestrator
"""
from typing import Tuple
from pydantic import BaseModel

class WarehouseConfig(BaseModel):
    name: str
    location: Tuple[float, float]  # (lat, lon)
    capacity: int
    carbon_factor: float  # Carbon footprint per unit distance

class SKUConfig(BaseModel):
    sku_id: str
    name: str
    category: str
    base_demand_rate: float
    lead_time_days: int
    unit_cost: float
    storage_cost_per_day: float
    stockout_cost: float
    min_stock_level: int
    max_stock_level: int

class SupplierConfig(BaseModel):
    supplier_id: str
    name: str
    location: Tuple[float, float]
    reliability_score: float  # 0-1
    carbon_factor: float
    lead_time_days: int
    price_multiplier: float  # Multiplier on base unit cost

# Simulation Configuration
SIMULATION_CONFIG = {
    "warehouses": [
        WarehouseConfig(
            name="Warehouse_North",
            location=(40.7128, -74.0060),  # NYC
            capacity=1000,
            carbon_factor=1.2
        ),
        WarehouseConfig(
            name="Warehouse_Central", 
            location=(41.8781, -87.6298),  # Chicago
            capacity=1200,
            carbon_factor=1.0
        ),
        WarehouseConfig(
            name="Warehouse_South",
            location=(29.7604, -95.3698),  # Houston
            capacity=800,
            carbon_factor=1.1
        )
    ],
    
    "skus": [
        SKUConfig(
            sku_id="SKU001",
            name="Premium Widget",
            category="Electronics",
            base_demand_rate=5.0,
            lead_time_days=7,
            unit_cost=25.0,
            storage_cost_per_day=0.5,
            stockout_cost=100.0,
            min_stock_level=20,
            max_stock_level=200
        ),
        SKUConfig(
            sku_id="SKU002",
            name="Basic Component",
            category="Hardware",
            base_demand_rate=8.0,
            lead_time_days=5,
            unit_cost=12.0,
            storage_cost_per_day=0.3,
            stockout_cost=50.0,
            min_stock_level=30,
            max_stock_level=300
        ),
        SKUConfig(
            sku_id="SKU003",
            name="Luxury Item",
            category="Premium",
            base_demand_rate=2.0,
            lead_time_days=14,
            unit_cost=150.0,
            storage_cost_per_day=2.0,
            stockout_cost=500.0,
            min_stock_level=5,
            max_stock_level=50
        ),
        SKUConfig(
            sku_id="SKU004",
            name="Standard Part",
            category="Mechanical",
            base_demand_rate=10.0,
            lead_time_days=4,
            unit_cost=8.0,
            storage_cost_per_day=0.2,
            stockout_cost=30.0,
            min_stock_level=40,
            max_stock_level=400
        ),
        SKUConfig(
            sku_id="SKU005",
            name="Specialty Tool",
            category="Tools",
            base_demand_rate=3.0,
            lead_time_days=10,
            unit_cost=75.0,
            storage_cost_per_day=1.0,
            stockout_cost=200.0,
            min_stock_level=10,
            max_stock_level=100
        ),
        SKUConfig(
            sku_id="SKU006",
            name="Bulk Material",
            category="Raw Materials",
            base_demand_rate=15.0,
            lead_time_days=3,
            unit_cost=5.0,
            storage_cost_per_day=0.1,
            stockout_cost=20.0,
            min_stock_level=50,
            max_stock_level=500
        ),
        SKUConfig(
            sku_id="SKU007",
            name="Custom Design",
            category="Custom",
            base_demand_rate=1.0,
            lead_time_days=21,
            unit_cost=300.0,
            storage_cost_per_day=3.0,
            stockout_cost=1000.0,
            min_stock_level=2,
            max_stock_level=20
        ),
        SKUConfig(
            sku_id="SKU008",
            name="Fast Moving",
            category="High Volume",
            base_demand_rate=20.0,
            lead_time_days=2,
            unit_cost=15.0,
            storage_cost_per_day=0.4,
            stockout_cost=60.0,
            min_stock_level=60,
            max_stock_level=600
        ),
        SKUConfig(
            sku_id="SKU009",
            name="Seasonal Item",
            category="Seasonal",
            base_demand_rate=4.0,
            lead_time_days=8,
            unit_cost=35.0,
            storage_cost_per_day=0.7,
            stockout_cost=140.0,
            min_stock_level=15,
            max_stock_level=150
        ),
        SKUConfig(
            sku_id="SKU010",
            name="Emergency Supply",
            category="Critical",
            base_demand_rate=6.0,
            lead_time_days=6,
            unit_cost=45.0,
            storage_cost_per_day=0.8,
            stockout_cost=300.0,
            min_stock_level=25,
            max_stock_level=250
        )
    ],
    
    "suppliers": [
        SupplierConfig(
            supplier_id="SUP001",
            name="East Coast Supply Co",
            location=(40.7128, -74.0060),  # NYC area
            reliability_score=0.95,
            carbon_factor=0.8,
            lead_time_days=3,
            price_multiplier=1.0
        ),
        SupplierConfig(
            supplier_id="SUP002", 
            name="Central Distributors",
            location=(41.8781, -87.6298),  # Chicago area
            reliability_score=0.88,
            carbon_factor=0.9,
            lead_time_days=4,
            price_multiplier=0.95
        ),
        SupplierConfig(
            supplier_id="SUP003",
            name="Southern Logistics",
            location=(29.7604, -95.3698),  # Houston area
            reliability_score=0.92,
            carbon_factor=0.85,
            lead_time_days=3,
            price_multiplier=1.05
        ),
        SupplierConfig(
            supplier_id="SUP004",
            name="West Coast Wholesale",
            location=(34.0522, -118.2437),  # LA area
            reliability_score=0.85,
            carbon_factor=1.2,
            lead_time_days=5,
            price_multiplier=0.90
        )
    ]
}

# Agent Communication Settings
AGENT_COMMUNICATION = {
    "message_timeout": 30,  # seconds
    "retry_attempts": 3,
    "coordination_window": 60  # seconds for coordination cycles
}

# Optimization Weights
OPTIMIZATION_WEIGHTS = {
    "cost_weight": 0.4,
    "carbon_weight": 0.2,
    "service_level_weight": 0.4
}

# Simulation Parameters
SIMULATION_PARAMS = {
    "time_step_minutes": 5,
    "demand_spike_probability": 0.1,
    "delay_probability": 0.05,
    "max_delay_days": 7
}
