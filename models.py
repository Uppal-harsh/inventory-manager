"""
Data models for the Autonomous Inventory Orchestrator
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

class MessageType(str, Enum):
    DEMAND_FORECAST = "demand_forecast"
    SUPPLY_ALERT = "supply_alert"
    LOGISTICS_REQUEST = "logistics_request"
    NEGOTIATION_OFFER = "negotiation_offer"
    INVENTORY_UPDATE = "inventory_update"
    OPTIMIZATION_RESULT = "optimization_result"

class AgentType(str, Enum):
    DEMAND = "demand"
    SUPPLY = "supply"
    LOGISTICS = "logistics"
    NEGOTIATION = "negotiation"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class InventoryLevel(BaseModel):
    sku_id: str
    warehouse_id: str
    current_stock: int
    reserved_stock: int
    available_stock: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def model_post_init(self, __context: Any) -> None:
        self.available_stock = self.current_stock - self.reserved_stock

class DemandForecast(BaseModel):
    sku_id: str
    warehouse_id: str
    forecasted_demand: float
    confidence_level: float  # 0-1
    forecast_horizon_days: int
    generated_at: datetime = Field(default_factory=datetime.now)
    factors: Dict[str, float] = Field(default_factory=dict)  # Seasonality, trends, etc.

class SupplierOffer(BaseModel):
    supplier_id: str
    sku_id: str
    quantity: int
    unit_price: float
    lead_time_days: int
    carbon_footprint: float
    reliability_score: float
    total_cost: float = Field(computed=True)
    
    def model_post_init(self, __context: Any) -> None:
        self.total_cost = self.quantity * self.unit_price

class Order(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sku_id: str
    warehouse_id: str
    supplier_id: str
    quantity: int
    unit_price: float
    total_cost: float = Field(computed=True)
    lead_time_days: int
    carbon_footprint: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    expected_delivery: datetime = Field(computed=True)
    
    def model_post_init(self, __context: Any) -> None:
        self.total_cost = self.quantity * self.unit_price
        self.expected_delivery = self.created_at + timedelta(days=self.lead_time_days)

class Shipment(BaseModel):
    shipment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    orders: List[str]  # Order IDs
    from_warehouse: Optional[str] = None
    to_warehouse: str
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    estimated_arrival: Optional[datetime] = None
    carbon_footprint: float = 0.0

class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: AgentType
    to_agent: AgentType
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = 1  # 1=low, 2=medium, 3=high
    requires_response: bool = False
    correlation_id: Optional[str] = None

class OptimizationResult(BaseModel):
    sku_id: str
    warehouse_id: str
    recommended_action: str  # "order", "transfer", "hold"
    recommended_quantity: int
    estimated_cost: float
    estimated_carbon_footprint: float
    confidence_score: float
    reasoning: str
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.now)

class SystemMetrics(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    total_inventory_value: float
    total_carbon_footprint: float
    service_level: float  # 0-1
    stockout_incidents: int
    overstock_incidents: int
    cost_efficiency: float
    agent_communication_volume: int
    optimization_cycles_completed: int

class Warehouse(BaseModel):
    warehouse_id: str
    name: str
    location: Tuple[float, float]
    capacity: int
    current_utilization: float = 0.0
    carbon_factor: float
    inventory: Dict[str, InventoryLevel] = Field(default_factory=dict)
    incoming_orders: List[Order] = Field(default_factory=list)
    outgoing_shipments: List[Shipment] = Field(default_factory=list)

class SKU(BaseModel):
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
    current_demand_multiplier: float = 1.0  # For simulating demand spikes

class Supplier(BaseModel):
    supplier_id: str
    name: str
    location: Tuple[float, float]
    reliability_score: float
    carbon_factor: float
    lead_time_days: int
    price_multiplier: float
    current_delay_days: int = 0  # For simulating delays
    available_skus: List[str] = Field(default_factory=list)
