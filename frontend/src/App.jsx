import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import PrivateRoute from './components/PrivateRoute';
import Dashboard from './components/Dashboard';
import Upload from './components/Upload';
import Verify from './components/Verify';
import Timestamps from './components/Timestamps';
import Certificate from './components/Certificate';
import Login from './components/Login';
import Register from './components/Register';
import VerifyOTP from './components/VerifyOTP';   // <-- 2FA: нова компонента

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />   {/* 2FA: нова рута */}

        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/upload"
          element={
            <PrivateRoute>
              <Upload />
            </PrivateRoute>
          }
        />
        <Route
          path="/verify"
          element={
            <PrivateRoute>
              <Verify />
            </PrivateRoute>
          }
        />
        <Route
          path="/timestamps"
          element={
            <PrivateRoute>
              <Timestamps />
            </PrivateRoute>
          }
        />
        <Route
          path="/all-timestamps"
          element={
            <PrivateRoute>
              <Timestamps all={true} />
            </PrivateRoute>
          }
        />
        <Route
          path="/certificate"
          element={
            <PrivateRoute>
              <Certificate />
            </PrivateRoute>
          }
        />
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;