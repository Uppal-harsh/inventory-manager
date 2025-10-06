"""
Negotiation Agent - Handles supplier negotiations and cost optimization
"""
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import logging

from models import Supplier, AgentMessage, MessageType, AgentType
from agent_communication import AgentCommunication

logger = logging.getLogger(__name__)

class NegotiationAgent(AgentCommunication):
    """Agent responsible for supplier negotiations and cost optimization"""
    
    def __init__(self, message_broker, suppliers: List[Supplier]):
        super().__init__(AgentType.NEGOTIATION, message_broker)
        self.suppliers = {s.supplier_id: s for s in suppliers}
        self.active_negotiations: Dict[str, Dict] = {}
        self.negotiation_history: List[Dict] = []
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.negotiation_strategies = {
            "volume_discount": 0.15,  # 15% discount for bulk orders
            "loyalty_bonus": 0.05,   # 5% bonus for loyal suppliers
            "carbon_incentive": 0.08, # 8% incentive for low-carbon suppliers
            "reliability_bonus": 0.10  # 10% bonus for reliable suppliers
        }
        
    def _setup_message_handlers(self):
        """Set up message handlers for negotiation agent"""
        self.register_handler(MessageType.SUPPLY_ALERT, self._handle_supply_alert)
        self.register_handler(MessageType.DEMAND_FORECAST, self._handle_demand_forecast)
        self.register_handler(MessageType.OPTIMIZATION_RESULT, self._handle_optimization_result)
    
    async def start(self):
        """Start the negotiation agent"""
        await super().start()
        # Start the negotiation monitoring loop
        asyncio.create_task(self._negotiation_loop())
        logger.info("Negotiation Agent started")
    
    async def _negotiation_loop(self):
        """Main negotiation monitoring loop"""
        while True:
            try:
                await self._monitor_price_trends()
                await self._evaluate_negotiation_opportunities()
                await self._process_active_negotiations()
                await asyncio.sleep(180)  # Check every 3 minutes
            except Exception as e:
                logger.error(f"Error in negotiation loop: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_price_trends(self):
        """Monitor price trends across suppliers"""
        current_time = datetime.now()
        
        for supplier_id, supplier in self.suppliers.items():
            # Simulate price monitoring
            base_price = 10.0  # Simplified base price
            current_price = base_price * supplier.price_multiplier
            
            # Add some price variation
            price_variation = np.random.normal(0, 0.05)  # 5% standard deviation
            current_price *= (1 + price_variation)
            
            # Record price history
            if supplier_id not in self.price_history:
                self.price_history[supplier_id] = []
            
            self.price_history[supplier_id].append((current_time, current_price))
            
            # Keep only recent history (last 30 days)
            cutoff = current_time - timedelta(days=30)
            self.price_history[supplier_id] = [
                (t, p) for t, p in self.price_history[supplier_id] if t > cutoff
            ]
            
            # Detect significant price changes
            if len(self.price_history[supplier_id]) >= 2:
                recent_prices = [p for _, p in self.price_history[supplier_id][-7:]]  # Last 7 prices
                if len(recent_prices) >= 2:
                    price_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
                    
                    if abs(price_change) > 0.1:  # 10% price change
                        await self.broadcast_message(
                            MessageType.SUPPLY_ALERT,
                            {
                                "alert_type": "price_change",
                                "supplier_id": supplier_id,
                                "price_change_percent": price_change * 100,
                                "current_price": current_price,
                                "message": f"Significant price change detected for {supplier_id}"
                            },
                            priority=2
                        )
    
    async def _evaluate_negotiation_opportunities(self):
        """Evaluate opportunities for new negotiations"""
        import random
        
        if random.random() < 0.2:  # 20% chance of negotiation opportunity
            # Find a supplier for negotiation
            target_supplier_id = random.choice(list(self.suppliers.keys()))
            supplier = self.suppliers[target_supplier_id]
            
            # Determine negotiation type
            negotiation_types = ["volume_discount", "loyalty_bonus", "carbon_incentive", "reliability_bonus"]
            negotiation_type = random.choice(negotiation_types)
            
            # Start negotiation
            await self._initiate_negotiation(target_supplier_id, negotiation_type)
    
    async def _initiate_negotiation(self, supplier_id: str, negotiation_type: str):
        """Initiate a negotiation with a supplier"""
        supplier = self.suppliers.get(supplier_id)
        if not supplier:
            return
        
        negotiation_id = f"neg_{supplier_id}_{int(datetime.now().timestamp())}"
        
        # Calculate negotiation parameters
        base_discount = self.negotiation_strategies.get(negotiation_type, 0.05)
        
        # Adjust discount based on supplier characteristics
        reliability_bonus = supplier.reliability_score * 0.1
        carbon_bonus = (1 - supplier.carbon_factor) * 0.05  # Lower carbon factor = higher bonus
        
        proposed_discount = base_discount + reliability_bonus + carbon_bonus
        proposed_discount = min(proposed_discount, 0.25)  # Cap at 25% discount
        
        negotiation = {
            "negotiation_id": negotiation_id,
            "supplier_id": supplier_id,
            "negotiation_type": negotiation_type,
            "proposed_discount": proposed_discount,
            "status": "active",
            "created_at": datetime.now(),
            "deadline": datetime.now() + timedelta(hours=24),
            "counter_offers": [],
            "success_probability": self._calculate_success_probability(supplier, negotiation_type)
        }
        
        self.active_negotiations[negotiation_id] = negotiation
        
        logger.info(f"Initiating {negotiation_type} negotiation with {supplier_id}")
        
        # Broadcast negotiation initiation
        await self.broadcast_message(
            MessageType.NEGOTIATION_OFFER,
            {
                "negotiation_id": negotiation_id,
                "supplier_id": supplier_id,
                "negotiation_type": negotiation_type,
                "proposed_discount": proposed_discount,
                "success_probability": negotiation["success_probability"],
                "message": f"Initiating {negotiation_type} negotiation with {supplier_id}"
            }
        )
    
    def _calculate_success_probability(self, supplier: Supplier, negotiation_type: str) -> float:
        """Calculate the probability of negotiation success"""
        base_probability = 0.6  # 60% base success rate
        
        # Adjust based on supplier reliability
        reliability_factor = supplier.reliability_score * 0.3
        
        # Adjust based on negotiation type
        type_factors = {
            "volume_discount": 0.8,    # High success rate
            "loyalty_bonus": 0.9,      # Very high success rate
            "carbon_incentive": 0.7,   # Medium success rate
            "reliability_bonus": 0.75  # Medium-high success rate
        }
        
        type_factor = type_factors.get(negotiation_type, 0.6)
        
        success_probability = base_probability + reliability_factor + (type_factor - 0.6)
        return min(max(success_probability, 0.1), 0.95)  # Clamp between 10% and 95%
    
    async def _process_active_negotiations(self):
        """Process active negotiations and handle outcomes"""
        current_time = datetime.now()
        
        for negotiation_id, negotiation in list(self.active_negotiations.items()):
            if negotiation["status"] == "active":
                # Check if negotiation deadline passed
                if current_time >= negotiation["deadline"]:
                    await self._resolve_negotiation(negotiation_id, "timeout")
                
                # Simulate supplier response
                elif np.random.random() < 0.3:  # 30% chance of response per cycle
                    await self._simulate_supplier_response(negotiation_id)
    
    async def _simulate_supplier_response(self, negotiation_id: str):
        """Simulate supplier response to negotiation"""
        negotiation = self.active_negotiations.get(negotiation_id)
        if not negotiation:
            return
        
        supplier_id = negotiation["supplier_id"]
        supplier = self.suppliers.get(supplier_id)
        
        if not supplier:
            return
        
        # Determine response based on success probability
        success_probability = negotiation["success_probability"]
        
        if np.random.random() < success_probability:
            # Successful negotiation
            accepted_discount = negotiation["proposed_discount"] * np.random.uniform(0.8, 1.0)
            
            # Update supplier price multiplier
            supplier.price_multiplier *= (1 - accepted_discount)
            supplier.price_multiplier = max(supplier.price_multiplier, 0.7)  # Minimum 70% of base price
            
            # Record successful negotiation
            negotiation["status"] = "accepted"
            negotiation["accepted_discount"] = accepted_discount
            negotiation["resolved_at"] = datetime.now()
            
            self.negotiation_history.append(negotiation)
            
            logger.info(f"Successful negotiation with {supplier_id}: {accepted_discount:.1%} discount")
            
            # Broadcast success
            await self.broadcast_message(
                MessageType.NEGOTIATION_OFFER,
                {
                    "negotiation_id": negotiation_id,
                    "supplier_id": supplier_id,
                    "status": "accepted",
                    "discount": accepted_discount,
                    "new_price_multiplier": supplier.price_multiplier,
                    "message": f"Negotiation successful with {supplier_id}: {accepted_discount:.1%} discount"
                }
            )
            
        else:
            # Negotiation failed
            await self._resolve_negotiation(negotiation_id, "rejected")
    
    async def _resolve_negotiation(self, negotiation_id: str, outcome: str):
        """Resolve a negotiation with given outcome"""
        negotiation = self.active_negotiations.get(negotiation_id)
        if not negotiation:
            return
        
        negotiation["status"] = outcome
        negotiation["resolved_at"] = datetime.now()
        
        self.negotiation_history.append(negotiation)
        del self.active_negotiations[negotiation_id]
        
        logger.info(f"Negotiation {negotiation_id} resolved: {outcome}")
        
        # Broadcast resolution
        await self.broadcast_message(
            MessageType.NEGOTIATION_OFFER,
            {
                "negotiation_id": negotiation_id,
                "supplier_id": negotiation["supplier_id"],
                "status": outcome,
                "message": f"Negotiation with {negotiation['supplier_id']} resolved: {outcome}"
            }
        )
    
    async def _handle_supply_alert(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle supply alerts that may trigger negotiations"""
        content = message.content
        alert_type = content.get("alert_type")
        
        if alert_type == "low_stock":
            sku_id = content.get("sku_id")
            
            # Check if we should negotiate better prices for emergency orders
            await self._evaluate_emergency_negotiation(sku_id)
        
        elif alert_type == "price_change":
            supplier_id = content.get("supplier_id")
            price_change = content.get("price_change_percent", 0)
            
            if price_change > 10:  # Significant price increase
                # Consider alternative suppliers
                await self._evaluate_supplier_alternatives(supplier_id)
        
        return {"status": "processed"}
    
    async def _evaluate_emergency_negotiation(self, sku_id: str):
        """Evaluate if emergency negotiation is needed for low stock"""
        # Find best suppliers for emergency orders
        best_suppliers = self._rank_suppliers_for_emergency()
        
        for supplier in best_suppliers[:2]:  # Negotiate with top 2 suppliers
            await self._initiate_negotiation(supplier.supplier_id, "volume_discount")
    
    def _rank_suppliers_for_emergency(self) -> List[Supplier]:
        """Rank suppliers for emergency orders"""
        # Score suppliers based on reliability, speed, and carbon footprint
        scored_suppliers = []
        
        for supplier in self.suppliers.values():
            # Emergency score favors reliability and speed over cost
            emergency_score = (
                0.5 * supplier.reliability_score +
                0.3 * (1 / (supplier.lead_time_days + supplier.current_delay_days + 1)) +
                0.2 * (1 / supplier.carbon_factor)
            )
            
            scored_suppliers.append((supplier, emergency_score))
        
        # Sort by score (descending)
        scored_suppliers.sort(key=lambda x: x[1], reverse=True)
        
        return [supplier for supplier, _ in scored_suppliers]
    
    async def _evaluate_supplier_alternatives(self, current_supplier_id: str):
        """Evaluate alternative suppliers when current supplier raises prices"""
        current_supplier = self.suppliers.get(current_supplier_id)
        if not current_supplier:
            return
        
        # Find suppliers with better pricing
        alternatives = []
        for supplier_id, supplier in self.suppliers.items():
            if supplier_id != current_supplier_id:
                # Check if alternative is cheaper
                if supplier.price_multiplier < current_supplier.price_multiplier * 0.95:  # 5% cheaper
                    alternatives.append(supplier)
        
        if alternatives:
            # Initiate negotiations with alternatives
            for alternative in alternatives[:2]:  # Negotiate with top 2 alternatives
                await self._initiate_negotiation(alternative.supplier_id, "volume_discount")
    
    async def _handle_demand_forecast(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle demand forecasts for proactive negotiations"""
        content = message.content
        forecast = content.get("forecast", {})
        urgency = content.get("urgency", "low")
        
        if urgency == "high":
            sku_id = forecast.get("sku_id")
            forecasted_demand = forecast.get("forecasted_demand", 0)
            
            # Proactive negotiation for high demand
            if forecasted_demand > 50:  # High volume threshold
                await self._initiate_bulk_negotiation(sku_id, forecasted_demand)
        
        return {"status": "processed"}
    
    async def _initiate_bulk_negotiation(self, sku_id: str, forecasted_demand: float):
        """Initiate bulk order negotiations for high demand items"""
        # Find suppliers suitable for bulk orders
        bulk_suppliers = self._find_bulk_suppliers()
        
        for supplier in bulk_suppliers:
            # Calculate bulk discount potential
            volume_tier = min(forecasted_demand / 100, 5)  # Up to 5x base discount for very large orders
            bulk_discount = min(0.05 + (volume_tier * 0.03), 0.20)  # 5-20% discount
            
            await self._initiate_negotiation(supplier.supplier_id, "volume_discount")
    
    def _find_bulk_suppliers(self) -> List[Supplier]:
        """Find suppliers suitable for bulk orders"""
        # Filter suppliers based on capacity and reliability
        bulk_suppliers = [
            supplier for supplier in self.suppliers.values()
            if supplier.reliability_score > 0.8  # High reliability requirement for bulk orders
        ]
        
        # Sort by reliability and carbon efficiency
        bulk_suppliers.sort(key=lambda s: (s.reliability_score, -s.carbon_factor), reverse=True)
        
        return bulk_suppliers
    
    async def _handle_optimization_result(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle optimization results that may require negotiations"""
        content = message.content
        recommended_action = content.get("recommended_action")
        
        if recommended_action == "order":
            sku_id = content.get("sku_id")
            quantity = content.get("recommended_quantity", 0)
            
            # Evaluate if we should negotiate for this order
            if quantity > 100:  # Large order threshold
                await self._evaluate_order_negotiation(sku_id, quantity)
        
        return {"status": "processed"}
    
    async def _evaluate_order_negotiation(self, sku_id: str, quantity: int):
        """Evaluate if we should negotiate for a specific order"""
        # Find best suppliers for this order
        order_suppliers = self._rank_suppliers_for_order(quantity)
        
        # Negotiate with top supplier
        if order_suppliers:
            await self._initiate_negotiation(order_suppliers[0].supplier_id, "volume_discount")
    
    def _rank_suppliers_for_order(self, quantity: int) -> List[Supplier]:
        """Rank suppliers for a specific order"""
        scored_suppliers = []
        
        for supplier in self.suppliers.values():
            # Score based on multiple factors
            score = (
                0.3 * supplier.reliability_score +
                0.2 * (1 / supplier.price_multiplier) +
                0.2 * (1 / (supplier.lead_time_days + supplier.current_delay_days + 1)) +
                0.1 * (1 / supplier.carbon_factor) +
                0.2 * (quantity / 1000)  # Bonus for large orders
            )
            
            scored_suppliers.append((supplier, score))
        
        # Sort by score (descending)
        scored_suppliers.sort(key=lambda x: x[1], reverse=True)
        
        return [supplier for supplier, _ in scored_suppliers]
    
    def get_negotiation_summary(self) -> Dict[str, Any]:
        """Get summary of negotiation activities"""
        successful_negotiations = [
            n for n in self.negotiation_history 
            if n.get("status") == "accepted"
        ]
        
        total_savings = sum(
            n.get("accepted_discount", 0) * 10000  # Assume $10k base order value
            for n in successful_negotiations
        )
        
        return {
            "active_negotiations": len(self.active_negotiations),
            "completed_negotiations": len(self.negotiation_history),
            "successful_negotiations": len(successful_negotiations),
            "success_rate": len(successful_negotiations) / len(self.negotiation_history) 
                          if self.negotiation_history else 0,
            "total_savings": total_savings,
            "avg_discount": np.mean([n.get("accepted_discount", 0) for n in successful_negotiations])
                          if successful_negotiations else 0,
            "price_history_entries": sum(len(history) for history in self.price_history.values())
        }
