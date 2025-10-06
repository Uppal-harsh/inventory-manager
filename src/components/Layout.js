import React from 'react';
import { Badge } from 'react-bootstrap';

const SidebarLink = ({ label, icon, isActive, onClick }) => {
  return (
    <button 
      className={`sidebar-link ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <span className="sidebar-icon" aria-hidden>{icon}</span>
      <span>{label}</span>
    </button>
  );
};

const Layout = ({ activeTab, setActiveTab, children }) => {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="sidebar-brand">
          <span className="brand-emoji">⚙️</span>
          <div className="brand-text">
            <div className="brand-title">A.I. Orchestrator</div>
            <div className="brand-sub">Industrial Operations</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <SidebarLink 
            label="Dashboard" 
            icon="📈" 
            isActive={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')} 
          />
          <SidebarLink 
            label="Agents" 
            icon="🤖" 
            isActive={activeTab === 'agents'}
            onClick={() => setActiveTab('agents')} 
          />
          <SidebarLink 
            label="Inventory" 
            icon="📦" 
            isActive={activeTab === 'inventory'}
            onClick={() => setActiveTab('inventory')} 
          />
          <SidebarLink 
            label="Sustainability" 
            icon="🌿" 
            isActive={activeTab === 'sustainability'}
            onClick={() => setActiveTab('sustainability')} 
          />
        </nav>

        <div className="sidebar-footer">
          <span className="status-text">STATUS: ONLINE</span>
          <Badge bg="success" className="ms-auto">LIVE</Badge>
        </div>
      </aside>

      <main className="app-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;