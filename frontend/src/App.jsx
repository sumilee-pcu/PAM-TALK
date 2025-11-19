/**
 * PAM-TALK Main App Component
 * 프로페셔널 메인 앱
 */

import React from 'react';
import AppRouter from './routes/AppRouter';
import { AuthProvider } from './hooks/useAuth';
import './styles/global.css';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}

export default App;
