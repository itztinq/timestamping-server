import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Upload from './components/Upload';
import Verify from './components/Verify';
import Timestamps from './components/Timestamps';
import Certificate from './components/Certificate';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
    return (
        <BrowserRouter>
            <Navigation />
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
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
                            <Timestamps all={false} /> {/* Мои записи */}
                        </PrivateRoute>
                    }
                />
                <Route
                    path="/all-timestamps"
                    element={
                        <PrivateRoute>
                            <Timestamps all={true} /> {/* Сите записи */}
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
                <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;