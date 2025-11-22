/**
 * ESG Module Router
 * Handles routing for ESG Activity Certification pages
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ESGPage from './ESGPage';
import ESGPreparePage from './ESGPreparePage';
import ESGCapturePage from './ESGCapturePage';
import ESGApplicationPage from './ESGApplicationPage';

function ESGRouter() {
  return (
    <Routes>
      <Route index element={<ESGPage />} />
      <Route path="prepare" element={<ESGPreparePage />} />
      <Route path="capture" element={<ESGCapturePage />} />
      <Route path="apply" element={<ESGApplicationPage />} />
      <Route path="*" element={<Navigate to="/esg" replace />} />
    </Routes>
  );
}

export default ESGRouter;
