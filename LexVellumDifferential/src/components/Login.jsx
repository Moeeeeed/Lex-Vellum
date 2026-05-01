import React, { useState } from 'react';

const Login = ({ onLoginSuccess }) => {
  const [isResetting, setIsResetting] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isResetting) {
        const response = await fetch(`http://localhost:8000/api/auth/reset-password-request?email=${encodeURIComponent(email)}`, {
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
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
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
