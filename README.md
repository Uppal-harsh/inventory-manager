
# Autonomous Inventory Orchestrator

A multi-agent AI system for autonomous inventory management across distributed warehouses. It responds to demand shifts, delivery delays, and supplier variability while optimizing across cost, service level, and carbon footprint.

## Features

**Multi-Agent Architecture**
Four specialized agents work in concert:
- **Demand Agent** — Forecasts demand patterns and detects spikes early
- **Supply Agent** — Tracks supplier reliability and manages reorders
- **Logistics Agent** — Optimizes shipping routes and inter-warehouse transfers
- **Negotiation Agent** — Handles supplier negotiations and cost reduction

**Real-Time Optimization**
Inventory rebalances continuously based on live signals. Supplier selection, reorder points, and routing decisions update dynamically — no manual intervention required.

**Sustainability**
Carbon footprint is a first-class metric. The system tracks emissions, prefers local suppliers, monitors renewable energy usage, and surfaces waste reduction opportunities.

**Live Dashboard**
A real-time interface for monitoring inventory levels, agent activity, system alerts, and sustainability performance.

---

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+

### Setup

```bash
git clone <repository-url>
cd autonomous-inventory-orchestrator
pip install -r requirements.txt
python start.py
```

The startup script handles dependency checks, frontend builds, and launches both the FastAPI backend and React dev server.

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| WebSocket | ws://localhost:8000/ws |

---

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  React UI    │◄──►│  FastAPI     │◄──►│  WebSocket   │
│  Dashboard   │    │  Backend     │    │  Real-time   │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                    ┌──────▼──────┐
                    │ Agent System │
                    │─────────────│
                    │ Demand      │
                    │ Supply      │
                    │ Logistics   │
                    │ Negotiation │
                    └─────────────┘
```

---

## Demo Scenarios

**Demand Spike** — Click "Simulate Demand Spike" to watch the Demand Agent detect and respond. The Supply Agent triggers reorders, Logistics rebalances inventory, and Negotiation seeks better pricing — all in real time.

**Supplier Delay** — Click "Simulate Delay" to trigger rerouting. The system finds alternative suppliers and adjusts inventory targets automatically.

**Sustainability Optimization** — Open the Sustainability tab to explore carbon tracking, supplier environmental ratings, and local sourcing metrics.

---

## Key Metrics

| Category | Metric |
|---|---|
| Performance | Service level, inventory turnover, cost efficiency |
| Sustainability | Carbon footprint, local sourcing %, renewable energy usage |
| Agents | Forecast accuracy, supplier reliability, negotiation success rate |

---

## Configuration

Warehouse locations, SKU definitions, supplier data, and optimization weights live in `config.py`.

Agent behavior is controlled per-agent:
- `agents/demand_agent.py` — Forecasting algorithms
- `agents/supply_agent.py` — Supplier selection logic
- `agents/logistics_agent.py` — Route optimization
- `agents/negotiation_agent.py` — Negotiation tactics

---

## Development

```bash
# Run backend tests
cd backend && python -m pytest

# Run frontend tests
npm test

# Development servers
uvicorn main:app --reload   # backend
npm start                   # frontend
```

---

## Roadmap

- ML-enhanced demand forecasting
- Blockchain-based supply chain traceability
- IoT warehouse sensor integration
- Microservices decomposition and Kubernetes deployment
- Persistent storage and historical analytics

---

## License

MIT — see [LICENSE](LICENSE) for details.

---
