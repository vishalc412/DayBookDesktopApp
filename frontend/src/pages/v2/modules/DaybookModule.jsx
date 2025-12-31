/**
 * Daybook Module
 * Traditional double-entry bookkeeping (V1 functionality)
 */

import React from 'react';
import Dashboard from '../../Dashboard';
import '../../../styles/DaybookModule.css';

const DaybookModule = () => {
  return (
    <div className="daybook-module-wrapper">
      <Dashboard hideNavigation={true} />
    </div>
  );
};

export default DaybookModule;
