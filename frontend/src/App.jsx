import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import useStore from './store/useStore';

// Layout
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';

// Pages
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import History from './pages/History';
import Analytics from './pages/Analytics';
import Profile from './pages/Profile';
import api from './api/client';

const Login = () => {
  const { setUser } = useStore();
  const [email, setEmail] = React.useState('test@test.com');
  const [password, setPassword] = React.useState('password');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // Create user if not exists (auto-register for demo)
      try {
        await api.post('/users/register', { name: "Demo User", email, password });
      } catch (e) { /* ignore if exists */ }
      
      const res = await api.post('/users/login', { email, password });
      setUser(res.data);
    } catch (err) {
      alert("Login failed");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <form onSubmit={handleLogin} className="glass-panel p-8 space-y-4 max-w-sm w-full">
        <h2 className="text-2xl font-bold text-center text-textMain">Knowledge Agent Login</h2>
        <input 
          className="w-full p-3 bg-background border border-surfaceHighlight rounded-xl text-textMain"
          type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required 
        />
        <input 
          className="w-full p-3 bg-background border border-surfaceHighlight rounded-xl text-textMain"
          type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required 
        />
        <button className="w-full p-3 bg-primary text-white rounded-xl font-bold hover:bg-primaryHover">Enter</button>
      </form>
    </div>
  );
};

const ProtectedRoute = ({ children }) => {
  const user = useStore((state) => state.user);
  if (!user) {
    return <Login />;
  }
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden bg-background">
        {useStore((state) => state.user) && <Sidebar />}
        <div className="flex-1 flex flex-col min-w-0">
          {useStore((state) => state.user) && <TopBar />}
          <main className="flex-1 overflow-y-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
              <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
