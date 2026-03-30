import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Terminal, 
  LogOut, 
  Play, 
  Cpu,
  Zap,
  ChevronRight
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

function App() {
  const [token, setToken] = useState(localStorage.getItem('heartbeat_token'));
  const [loading, setLoading] = useState(false);
  const [digests, setDigests] = useState([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (token) {
      fetchDigests();
    }
  }, [token]);

  const fetchDigests = async () => {
    try {
      const res = await axios.get(`${API_BASE}/digests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDigests(res.data);
    } catch (err) {
      if (err.response?.status === 401) handleLogout();
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const endpoint = isRegister ? "/register" : "/token";
      let res;
      if (isRegister) {
        res = await axios.post(`${API_BASE}${endpoint}`, { email, password });
      } else {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        res = await axios.post(`${API_BASE}${endpoint}`, formData);
      }
      const newToken = res.data.access_token;
      setToken(newToken);
      localStorage.setItem('heartbeat_token', newToken);
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('heartbeat_token');
  };

  const triggerHeartbeat = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/heartbeat/trigger`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchDigests();
    } catch (err) {
      setError("Failed to trigger heartbeat");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4 text-center">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full"
        >
          <div className="mb-4 flex justify-center">
            <div className="p-3 rounded-full bg-indigo-500/10 text-indigo-400">
              <Zap size={32} className="pulse" />
            </div>
          </div>
          <h1 className="text-2xl font-bold mb-1">Heartbeat</h1>
          <p className="text-secondary text-sm mb-6">Founder Intelligence</p>
          
          <form onSubmit={handleAuth} className="space-y-3">
            <input 
              type="email" 
              placeholder="Email" 
              className="w-full bg-white/5 border border-white/10 rounded-xl p-2.5 text-sm outline-none focus:border-indigo-500/50"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input 
              type="password" 
              placeholder="Password" 
              className="w-full bg-white/5 border border-white/10 rounded-xl p-2.5 text-sm outline-none focus:border-indigo-500/50"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button className="button-primary w-full py-3 text-sm">
              {loading ? "..." : isRegister ? "Create Account" : "Sign In"}
            </button>
          </form>

          {error && <p className="text-red-400 mt-3 text-xs">{error}</p>}
          
          <button 
            onClick={() => setIsRegister(!isRegister)} 
            className="mt-6 text-xs text-indigo-400 hover:text-indigo-300"
          >
            {isRegister ? "Already have an account? Sign In" : "Don't have an account? Register"}
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Mini Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-indigo-400" strokeWidth={3} />
          <span className="font-bold text-sm tracking-tight text-white">HEARTBEAT</span>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={triggerHeartbeat} 
            disabled={loading} 
            className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 transition-colors"
            title="Trigger Manual Scan"
          >
            <Play size={14} fill="currentColor" className={loading ? "animate-spin" : ""} />
          </button>
          <button 
            onClick={handleLogout} 
            className="p-2 rounded-lg bg-white/5 text-secondary hover:text-white transition-colors"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>

      {/* System Health Strip */}
      <div className="flex justify-between items-center px-3 py-2 bg-indigo-500/5 rounded-xl mb-4 border border-indigo-500/10">
        <div className="flex items-center gap-2 text-[10px] font-bold text-indigo-300/80 uppercase">
          <Cpu size={12} /> System Health
        </div>
        <div className="flex gap-2">
          <div className="status-dot green scale-75" title="Engine Ready"></div>
          <div className="status-dot green scale-75" title="AI Active"></div>
          <div className="status-dot yellow scale-75" title="7 Connectors"></div>
        </div>
      </div>

      {/* Feed Container */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-3 custom-scrollbar">
        <AnimatePresence mode='popLayout'>
          {digests.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center py-12 text-center text-secondary opacity-40"
            >
              <Terminal size={32} className="mb-2" />
              <p className="text-xs">No active signals.<br/>Trigger a scan to begin.</p>
            </motion.div>
          ) : (
            digests.map((d, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel p-3 border-l-2 border-l-indigo-500/50"
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[9px] font-mono text-indigo-400/80">
                    {new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span className="text-[9px] text-secondary/60 font-bold uppercase tracking-widest">{d.source_type}</span>
                </div>
                <div className="text-[11px] leading-relaxed">
                  {d.content.split('\n').map((line, i) => {
                    if (line.includes('🔴')) return <div key={i} className="text-red-400 font-bold my-1 flex items-start gap-1">{line}</div>;
                    if (line.includes('🟡')) return <div key={i} className="text-yellow-400 font-bold my-1 flex items-start gap-1">{line}</div>;
                    if (line.includes('✅')) return <div key={i} className="text-green-400 font-bold my-1 flex items-start gap-1">{line}</div>;
                    if (line.includes('📌')) return <div key={i} className="mt-2 p-1.5 rounded bg-white/5 border border-white/5 text-[10px] italic">{line}</div>;
                    return <div key={i} className="text-white/80">{line}</div>;
                  })}
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      <div className="mt-4 pt-2 border-t border-white/5 text-center">
        <p className="text-[9px] text-secondary/40 font-medium">Logged in as {email}</p>
      </div>
    </div>
  );
}

export default App;
