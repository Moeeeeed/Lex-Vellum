import React, { useState } from 'react';
const Login = ({ onLoginSuccess }) => {
  const [isResetting, setIsResetting] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isResetting) {
        const response = await fetch(`http://localhost:8000/api/auth/reset-password?email=${email}`, {
          method: 'POST',
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Reset failed');
        setError('Success: Check your email for a reset link.');
        setIsResetting(false);
      } else {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        const response = await fetch(`http://localhost:8000/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: formData,
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Authentication failed');
        localStorage.setItem('token', data.access_token);
        onLoginSuccess(data.access_token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="brand-title">LexVellum</h1>
          <p className="brand-subtitle">Differential compliance engine</p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          <h2 className="form-title">{isResetting ? 'Reset Password' : 'Welcome Back'}</h2>
          {error && <div className={`message ${error.includes('Success') ? 'success' : 'error'}`}>{error}</div>}
          <div className="input-group">
            <label>Email Address</label>
            <input
              type="email"
              placeholder="legal@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          {!isResetting && (
            <div className="input-group">
              <label>Password</label>
              <div className="password-input-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button 
                  type="button" 
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                  )}
                </button>
              </div>
            </div>
          )}
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Processing...' : (isResetting ? 'Request Reset' : 'Access Platform')}
          </button>
        </form>
        <div className="login-footer">
          <button 
            className="toggle-button" 
            onClick={() => setIsResetting(!isResetting)}
          >
            {isResetting ? 'Back to Login' : 'Forgot Password?'}
          </button>
        </div>
      </div>
      <style>{`
        .login-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background-color: #000;
          color: #fff;
          font-family: 'Inter', sans-serif;
        }
        .login-card {
          width: 100%;
          max-width: 400px;
          padding: 40px;
          background: #111;
          border: 1px solid #333;
          border-radius: 8px;
          box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        .login-header {
          text-align: center;
          margin-bottom: 40px;
        }
        .brand-title {
          font-size: 2rem;
          font-weight: 800;
          letter-spacing: -1px;
          margin: 0;
          text-transform: uppercase;
        }
        .brand-subtitle {
          font-size: 0.8rem;
          color: #666;
          margin-top: 5px;
        }
        .form-title {
          font-size: 1.2rem;
          margin-bottom: 25px;
          font-weight: 500;
        }
        .input-group {
          margin-bottom: 20px;
        }
        .input-group label {
          display: block;
          font-size: 0.75rem;
          text-transform: uppercase;
          color: #888;
          margin-bottom: 8px;
          letter-spacing: 1px;
        }
        .input-group input {
          width: 100%;
          padding: 12px;
          background: #000;
          border: 1px solid #333;
          border-radius: 4px;
          color: #fff;
          outline: none;
          transition: border-color 0.2s;
        }
        .input-group input:focus {
          border-color: #fff;
        }
        .password-input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }
        .password-toggle {
          position: absolute;
          right: 12px;
          background: none;
          border: none;
          color: #666;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          transition: color 0.2s;
        }
        .password-toggle:hover {
          color: #fff;
        }
        .login-button {
          width: 100%;
          padding: 14px;
          background: #fff;
          color: #000;
          border: none;
          border-radius: 4px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
          margin-top: 10px;
        }
        .login-button:hover {
          background: #ccc;
        }
        .login-button:disabled {
          background: #333;
          color: #666;
          cursor: not-allowed;
        }
        .message {
          padding: 10px;
          border-radius: 4px;
          font-size: 0.85rem;
          margin-bottom: 20px;
        }
        .message.error {
          background: rgba(255, 0, 0, 0.1);
          color: #ff5555;
          border: 1px solid #ff5555;
        }
        .message.success {
          background: rgba(0, 255, 0, 0.1);
          color: #55ff55;
          border: 1px solid #55ff55;
        }
        .login-footer {
          margin-top: 25px;
          text-align: center;
        }
        .toggle-button {
          background: none;
          border: none;
          color: #888;
          font-size: 0.8rem;
          cursor: pointer;
          transition: color 0.2s;
        }
        .toggle-button:hover {
          color: #fff;
        }
      `}</style>
    </div>
  );
};
export default Login;
