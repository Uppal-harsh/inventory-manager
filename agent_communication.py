"""
Agent Communication System for the Autonomous Inventory Orchestrator
"""
import asyncio
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict, deque
import logging

from models import AgentMessage, MessageType, AgentType

logger = logging.getLogger(__name__)

class MessageBroker:
    """Central message broker for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[AgentType, List[Callable]] = defaultdict(list)
        self.message_queue: deque = deque()
        self.message_history: List[AgentMessage] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.message_timeout = 30  # seconds
        
    async def subscribe(self, agent_type: AgentType, callback: Callable):
        """Subscribe an agent to receive messages"""
        self.subscribers[agent_type].append(callback)
        logger.info(f"Agent {agent_type} subscribed to message broker")
        
    async def publish(self, message: AgentMessage) -> Optional[Any]:
        """Publish a message to the broker"""
        self.message_queue.append(message)
        self.message_history.append(message)
        
        logger.info(f"Published message: {message.message_type} from {message.from_agent} to {message.to_agent}")
        
        # Handle direct message routing
        if message.to_agent in self.subscribers:
            for callback in self.subscribers[message.to_agent]:
                try:
                    result = await callback(message)
                    if message.requires_response:
                        return result
                except Exception as e:
                    logger.error(f"Error in message callback: {e}")
        
        # Handle broadcast messages (when to_agent is None)
        if message.to_agent is None:
            for agent_type, callbacks in self.subscribers.items():
                if agent_type != message.from_agent:  # Don't send to sender
                    for callback in callbacks:
                        try:
                            await callback(message)
                        except Exception as e:
                            logger.error(f"Error in broadcast callback: {e}")
        
        return None
    
    async def request_response(self, message: AgentMessage, timeout: int = None) -> Any:
        """Send a message and wait for a response"""
        if timeout is None:
            timeout = self.message_timeout
            
        future = asyncio.Future()
        correlation_id = message.message_id
        self.pending_responses[correlation_id] = future
        
        message.correlation_id = correlation_id
        message.requires_response = True
        
        await self.publish(message)
        
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Message {correlation_id} timed out")
            return None
        finally:
            self.pending_responses.pop(correlation_id, None)
    
    async def respond_to_message(self, original_message_id: str, response_content: Dict[str, Any]):
        """Respond to a specific message"""
        if original_message_id in self.pending_responses:
            future = self.pending_responses[original_message_id]
            if not future.done():
                future.set_result(response_content)
    
    def get_message_history(self, agent_type: Optional[AgentType] = None, 
                          message_type: Optional[MessageType] = None,
                          limit: int = 100) -> List[AgentMessage]:
        """Get filtered message history"""
        messages = self.message_history
        
        if agent_type:
            messages = [m for m in messages if m.from_agent == agent_type or m.to_agent == agent_type]
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        return messages[-limit:]
    
    def get_communication_metrics(self) -> Dict[str, Any]:
        """Get communication metrics"""
        total_messages = len(self.message_history)
        agent_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for message in self.message_history:
            agent_counts[message.from_agent] += 1
            type_counts[message.message_type] += 1
        
        return {
            "total_messages": total_messages,
            "messages_by_agent": dict(agent_counts),
            "messages_by_type": dict(type_counts),
            "active_subscribers": len(self.subscribers)
        }

class AgentCommunication:
    """Base class for agent communication capabilities"""
    
    def __init__(self, agent_type: AgentType, message_broker: MessageBroker):
        self.agent_type = agent_type
        self.broker = message_broker
        self.message_handlers: Dict[MessageType, Callable] = {}
        self._setup_message_handlers()
        
    def _setup_message_handlers(self):
        """Override in subclasses to set up message handlers"""
        pass
    
    async def send_message(self, to_agent: AgentType, message_type: MessageType, 
                          content: Dict[str, Any], priority: int = 1, 
                          requires_response: bool = False) -> Optional[Any]:
        """Send a message to another agent"""
        message = AgentMessage(
            from_agent=self.agent_type,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            priority=priority,
            requires_response=requires_response
        )
        
        if requires_response:
            return await self.broker.request_response(message)
        else:
            await self.broker.publish(message)
            return None
    
    async def broadcast_message(self, message_type: MessageType, 
                               content: Dict[str, Any], priority: int = 1):
        """Broadcast a message to all agents"""
        message = AgentMessage(
            from_agent=self.agent_type,
            to_agent=None,  # None means broadcast
            message_type=message_type,
            content=content,
            priority=priority
        )
        
        await self.broker.publish(message)
    
    async def handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Handle incoming messages"""
        if message.message_type in self.message_handlers:
            try:
                result = await self.message_handlers[message.message_type](message)
                if message.requires_response and message.correlation_id:
                    await self.broker.respond_to_message(message.correlation_id, result)
                return result
            except Exception as e:
                logger.error(f"Error handling message {message.message_type}: {e}")
                return {"error": str(e)}
        
        logger.warning(f"No handler for message type: {message.message_type}")
        return None
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
    
    async def start(self):
        """Start the agent communication"""
        await self.broker.subscribe(self.agent_type, self.handle_message)
        logger.info(f"Agent {self.agent_type} started communication")
    
    async def stop(self):
        """Stop the agent communication"""
        logger.info(f"Agent {self.agent_type} stopped communication")
