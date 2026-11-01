import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import { ProtectedRoute } from './components/auth/ProtectedRoute.jsx';
import { PublicRoute } from './components/auth/PublicRoute.jsx';
import { Login } from './pages/Login.jsx';
import { Register } from './pages/Register.jsx';
import { Dashboard } from './pages/Dashboard.jsx';
import { DriverMonitor } from './pages/DriverMonitor.jsx';
import { VehicleManagement } from './pages/VehicleManagement.jsx';
import { DriverProfilePage } from './pages/DriverProfilePage.jsx';
import { NavigationMap } from './pages/NavigationMap.jsx';
import { ROUTE_PATHS } from './constants/routes.constants.js';

export const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Authentication Views */}
          <Route element={<PublicRoute />}>
            <Route path={ROUTE_PATHS.LOGIN} element={<Login />} />
            <Route path={ROUTE_PATHS.REGISTER} element={<Register />} />
          </Route>

          {/* Protected Main Views */}
          <Route element={<ProtectedRoute />}>
            <Route path={ROUTE_PATHS.DASHBOARD} element={<Dashboard />} />
            <Route path={ROUTE_PATHS.DRIVER_MONITOR} element={<DriverMonitor />} />
            <Route path={ROUTE_PATHS.VEHICLES} element={<VehicleManagement />} />
            <Route path={ROUTE_PATHS.PROFILE} element={<DriverProfilePage />} />
            <Route path={ROUTE_PATHS.NAV_MAP} element={<NavigationMap />} />
          </Route>

          {/* Root Redirection */}
          <Route path="/" element={<Navigate to={ROUTE_PATHS.DASHBOARD} replace />} />
          <Route path="*" element={<Navigate to={ROUTE_PATHS.LOGIN} replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;