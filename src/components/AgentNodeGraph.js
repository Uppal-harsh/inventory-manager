import React, { useEffect, useRef, useState } from 'react';

const AGENT_POSITIONS = {
  DEMAND: { x: 100, y: 100 },
  SUPPLY: { x: 400, y: 100 },
  LOGISTICS: { x: 100, y: 400 },
  NEGOTIATION: { x: 400, y: 400 },
};

const AgentNode = ({ agent, type }) => (
  <g transform={`translate(${agent.x}, ${agent.y})`}>
    <circle r="40" fill={`url(#grad-${type.toLowerCase()})`} />
    <text y="-50" textAnchor="middle" fill="white" fontSize="14" fontWeight="bold">
      {type}
    </text>
    <text y="5" textAnchor="middle" fill="white" fontSize="24">
      {agent.icon}
    </text>
  </g>
);

const MessageParticle = ({ from, to, id }) => {
  const particleRef = useRef(null);

  useEffect(() => {
    const particle = particleRef.current;
    if (particle) {
      particle.style.animation = 'none';
      void particle.offsetWidth; // Trigger reflow
      particle.style.animation = `move 1.5s ease-out forwards`;
    }
  }, [id]);

  return (
    <path
      ref={particleRef}
      d={`M${from.x},${from.y} Q${(from.x + to.x) / 2},${(from.y + to.y) / 2 - 100} ${to.x},${to.y}`}
      fill="none"
      stroke="none"
    >
      <circle cx="0" cy="0" r="5" fill="#0ea5e9">
        <animateMotion dur="1.5s" repeatCount="1" fill="freeze" rotate="auto">
          <mpath href={`#path-${id}`} />
        </animateMotion>
      </circle>
      <path id={`path-${id}`} d={`M${from.x},${from.y} Q${(from.x + to.x) / 2},${(from.y + to.y) / 2 - 100} ${to.x},${to.y}`} />
    </path>
  );
};

const AgentNodeGraph = ({ messages }) => {
  const [particles, setParticles] = useState([]);

  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.type === 'agent_message') {
        const { from_agent, to_agent } = lastMessage.data;
        if (from_agent && to_agent && AGENT_POSITIONS[from_agent] && AGENT_POSITIONS[to_agent]) {
          const newParticle = {
            id: lastMessage.data.message_id,
            from: AGENT_POSITIONS[from_agent],
            to: AGENT_POSITIONS[to_agent],
          };
          setParticles(prev => [...prev.slice(-5), newParticle]);
        }
      }
    }
  }, [messages]);

  const agents = {
    DEMAND: { ...AGENT_POSITIONS.DEMAND, icon: '📊' },
    SUPPLY: { ...AGENT_POSITIONS.SUPPLY, icon: '📦' },
    LOGISTICS: { ...AGENT_POSITIONS.LOGISTICS, icon: '🚚' },
    NEGOTIATION: { ...AGENT_POSITIONS.NEGOTIATION, icon: '🤝' },
  };

  return (
    <svg viewBox="0 0 500 500" width="100%" height="100%">
      <defs>
        <radialGradient id="grad-demand">
          <stop offset="0%" stopColor="#4ade80" />
          <stop offset="100%" stopColor="#166534" />
        </radialGradient>
        <radialGradient id="grad-supply">
          <stop offset="0%" stopColor="#0ea5e9" />
          <stop offset="100%" stopColor="#075985" />
        </radialGradient>
        <radialGradient id="grad-logistics">
          <stop offset="0%" stopColor="#facc15" />
          <stop offset="100%" stopColor="#713f12" />
        </radialGradient>
        <radialGradient id="grad-negotiation">
          <stop offset="0%" stopColor="#ef4444" />
          <stop offset="100%" stopColor="#7f1d1d" />
        </radialGradient>
      </defs>

      {/* Connections */}
      <line x1="100" y1="100" x2="400" y2="100" stroke="rgba(255,255,255,0.1)" />
      <line x1="100" y1="100" x2="100" y2="400" stroke="rgba(255,255,255,0.1)" />
      <line x1="400" y1="100" x2="400" y2="400" stroke="rgba(255,255,255,0.1)" />
      <line x1="100" y1="400" x2="400" y2="400" stroke="rgba(255,255,255,0.1)" />
      <line x1="100" y1="100" x2="400" y2="400" stroke="rgba(255,255,255,0.1)" />
      <line x1="400" y1="100" x2="100" y2="400" stroke="rgba(255,255,255,0.1)" />

      {Object.entries(agents).map(([type, agent]) => (
        <AgentNode key={type} agent={agent} type={type} />
      ))}

      {particles.map(p => (
        <MessageParticle key={p.id} from={p.from} to={p.to} id={p.id} />
      ))}
    </svg>
  );
};

export default AgentNodeGraph;
