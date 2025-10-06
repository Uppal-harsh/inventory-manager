"""
Demand Agent - Forecasts demand and identifies demand patterns
"""
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import logging

from models import DemandForecast, AgentMessage, MessageType, AgentType, SKU
from agent_communication import AgentCommunication

logger = logging.getLogger(__name__)

class DemandAgent(AgentCommunication):
    """Agent responsible for demand forecasting and pattern recognition"""
    
    def __init__(self, message_broker, skus: Dict[str, SKU]):
        super().__init__(AgentType.DEMAND, message_broker)
        self.skus = skus
        self.demand_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.forecasts: Dict[str, DemandForecast] = {}
        self.forecast_interval = 60  # seconds
        
    def _setup_message_handlers(self):
        """Set up message handlers for demand agent"""
        self.register_handler(MessageType.INVENTORY_UPDATE, self._handle_inventory_update)
        self.register_handler(MessageType.SUPPLY_ALERT, self._handle_supply_alert)
    
    async def start(self):
        """Start the demand agent"""
        await super().start()
        # Start the forecasting loop
        asyncio.create_task(self._forecasting_loop())
        logger.info("Demand Agent started")
    
    async def _forecasting_loop(self):
        """Main forecasting loop"""
        while True:
            try:
                await self._generate_forecasts()
                await asyncio.sleep(self.forecast_interval)
            except Exception as e:
                logger.error(f"Error in forecasting loop: {e}")
                await asyncio.sleep(10)
    
    async def _generate_forecasts(self):
        """Generate demand forecasts for all SKUs"""
        for sku_id, sku in self.skus.items():
            forecast = await self._calculate_forecast(sku_id, sku)
            self.forecasts[sku_id] = forecast
            
            # Broadcast forecast to other agents
            await self.broadcast_message(
                MessageType.DEMAND_FORECAST,
                {
                    "forecast": forecast.dict(),
                    "sku_id": sku_id,
                    "urgency": self._calculate_urgency(forecast)
                }
            )
    
    async def _calculate_forecast(self, sku_id: str, sku: SKU) -> DemandForecast:
        """Calculate demand forecast for a specific SKU"""
        # Get historical demand data
        history = self.demand_history.get(sku_id, [])
        
        # If no history, use base demand rate
        if not history:
            forecasted_demand = sku.base_demand_rate * sku.current_demand_multiplier
            confidence = 0.3  # Low confidence for new SKUs
        else:
            # Calculate trend and seasonality
            recent_data = [d for d, _ in history[-30:]]  # Last 30 data points
            recent_demands = [d for _, d in history[-30:]]
            
            if len(recent_demands) >= 7:
                # Calculate moving average with trend
                forecasted_demand = np.mean(recent_demands[-7:])  # 7-day moving average
                
                # Add trend component
                if len(recent_demands) >= 14:
                    trend = np.mean(recent_demands[-7:]) - np.mean(recent_demands[-14:-7])
                    forecasted_demand += trend * 0.5
                
                # Add seasonality (simplified)
                day_of_week = datetime.now().weekday()
                seasonality_factor = 1.0 + 0.1 * np.sin(2 * np.pi * day_of_week / 7)
                forecasted_demand *= seasonality_factor
                
                confidence = min(0.95, 0.5 + len(recent_demands) * 0.02)
            else:
                forecasted_demand = sku.base_demand_rate * sku.current_demand_multiplier
                confidence = 0.4
        
        # Apply current demand multiplier (for simulation spikes)
        forecasted_demand *= sku.current_demand_multiplier
        
        return DemandForecast(
            sku_id=sku_id,
            warehouse_id="",  # Will be filled by warehouse-specific forecasts
            forecasted_demand=forecasted_demand,
            confidence_level=confidence,
            forecast_horizon_days=7,
            factors={
                "base_rate": sku.base_demand_rate,
                "current_multiplier": sku.current_demand_multiplier,
                "trend": self._calculate_trend(sku_id),
                "seasonality": self._get_seasonality_factor(),
                "volatility": self._calculate_volatility(sku_id)
            }
        )
    
    def _calculate_trend(self, sku_id: str) -> float:
        """Calculate demand trend"""
        history = self.demand_history.get(sku_id, [])
        if len(history) < 14:
            return 0.0
        
        recent = [d for _, d in history[-7:]]
        older = [d for _, d in history[-14:-7]]
        
        if len(recent) == 7 and len(older) == 7:
            return np.mean(recent) - np.mean(older)
        return 0.0
    
    def _get_seasonality_factor(self) -> float:
        """Get seasonality factor based on current time"""
        now = datetime.now()
        # Simple seasonality based on day of week and hour
        day_factor = 1.0 + 0.2 * np.sin(2 * np.pi * now.weekday() / 7)
        hour_factor = 1.0 + 0.1 * np.sin(2 * np.pi * now.hour / 24)
        return day_factor * hour_factor
    
    def _calculate_volatility(self, sku_id: str) -> float:
        """Calculate demand volatility"""
        history = self.demand_history.get(sku_id, [])
        if len(history) < 7:
            return 0.5  # Default volatility
        
        demands = [d for _, d in history[-7:]]
        if len(demands) > 1:
            return np.std(demands) / np.mean(demands) if np.mean(demands) > 0 else 0.5
        return 0.5
    
    def _calculate_urgency(self, forecast: DemandForecast) -> str:
        """Calculate forecast urgency"""
        volatility = forecast.factors.get("volatility", 0.5)
        confidence = forecast.confidence_level
        
        if volatility > 0.8 or confidence < 0.4:
            return "high"
        elif volatility > 0.5 or confidence < 0.7:
            return "medium"
        else:
            return "low"
    
    async def _handle_inventory_update(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle inventory update messages"""
        content = message.content
        sku_id = content.get("sku_id")
        actual_demand = content.get("actual_demand", 0)
        timestamp = content.get("timestamp", datetime.now())
        
        if sku_id:
            # Record actual demand
            if sku_id not in self.demand_history:
                self.demand_history[sku_id] = []
            
            self.demand_history[sku_id].append((timestamp, actual_demand))
            
            # Keep only recent history (last 90 days)
            cutoff = timestamp - timedelta(days=90)
            self.demand_history[sku_id] = [
                (t, d) for t, d in self.demand_history[sku_id] 
                if t > cutoff
            ]
            
            logger.info(f"Recorded demand for {sku_id}: {actual_demand}")
        
        return {"status": "processed"}
    
    async def _handle_supply_alert(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle supply alerts that might affect demand patterns"""
        content = message.content
        sku_id = content.get("sku_id")
        alert_type = content.get("alert_type")
        
        if alert_type == "stockout_risk":
            # Increase demand multiplier for affected SKU
            if sku_id in self.skus:
                self.skus[sku_id].current_demand_multiplier *= 1.2
                logger.info(f"Increased demand multiplier for {sku_id} due to stockout risk")
        
        return {"status": "processed"}
    
    def simulate_demand_spike(self, sku_id: str, multiplier: float = 2.0, duration_hours: int = 24):
        """Simulate a demand spike for testing"""
        if sku_id in self.skus:
            self.skus[sku_id].current_demand_multiplier = multiplier
            logger.info(f"Simulated demand spike for {sku_id}: {multiplier}x for {duration_hours}h")
            
            # Schedule return to normal
            asyncio.create_task(self._restore_normal_demand(sku_id, duration_hours))
    
    async def _restore_normal_demand(self, sku_id: str, delay_hours: int):
        """Restore normal demand after a spike"""
        await asyncio.sleep(delay_hours * 3600)  # Convert hours to seconds
        if sku_id in self.skus:
            self.skus[sku_id].current_demand_multiplier = 1.0
            logger.info(f"Restored normal demand for {sku_id}")
    
    def get_forecast_summary(self) -> Dict[str, Any]:
        """Get summary of current forecasts"""
        return {
            "total_forecasts": len(self.forecasts),
            "high_urgency_count": sum(1 for f in self.forecasts.values() 
                                    if self._calculate_urgency(f) == "high"),
            "avg_confidence": np.mean([f.confidence_level for f in self.forecasts.values()]) 
                           if self.forecasts else 0,
            "forecasts": {sku_id: f.dict() for sku_id, f in self.forecasts.items()}
        }
