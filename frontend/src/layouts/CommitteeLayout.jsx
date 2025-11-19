import React from 'react';
import { Outlet } from 'react-router-dom';

function CommitteeLayout() {
  return (
    <div className="committee-layout">
      <header style={{ padding: '1rem 2rem', background: '#2196F3', color: 'white' }}>
        <h2>위원회 포털</h2>
      </header>
      <main style={{ padding: '2rem' }}>
        <Outlet />
      </main>
    </div>
  );
}

export default CommitteeLayout;
