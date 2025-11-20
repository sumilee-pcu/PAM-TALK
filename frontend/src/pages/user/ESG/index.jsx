/**
 * ESG Module Router
 * Handles routing for ESG Activity Certification pages
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ESGPage from './ESGPage';
import ESGCapturePage from './ESGCapturePage';

function ESGRouter() {
  return (
    <Routes>
      <Route index element={<ESGPage />} />
      <Route path="capture" element={<ESGCapturePage />} />
      <Route path="*" element={<Navigate to="/esg" replace />} />
    </Routes>
  );
}

export default ESGRouter;
