import React from 'react';

const MetricCard = ({ label, value, icon }) => {
  return (
    <div className="metric-card-industrial">
      <div className="metric-icon-industrial">{icon}</div>
      <div className="metric-content-industrial">
        <div className="metric-label-industrial">{label}</div>
        <div className="metric-value-industrial">{value}</div>
      </div>
    </div>
  );
};

export default MetricCard;