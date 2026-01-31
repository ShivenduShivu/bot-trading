import { useState } from 'react'
import './App.css'

function App() {
  // State to store message from backend
  const [message, setMessage] = useState('Click button to test backend connection')
  const [loading, setLoading] = useState(false)

  // Function to call backend API
  const testBackendConnection = async () => {
    setLoading(true)
    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/hello')
      const data = await response.json()
      
      // Update state with backend message
      setMessage(data.message)
    } catch (error) {
      setMessage('❌ Error: Could not connect to backend. Is it running?')
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <div className="container">
        <h1>📈 Paper Trading Platform</h1>
        <p className="subtitle">Checkpoint 0: Hello World</p>
        
        <div className="card">
          <h2>Backend Connection Test</h2>
          <p className="message">{message}</p>
          
          <button 
            onClick={testBackendConnection}
            disabled={loading}
            className="test-button"
          >
            {loading ? '⏳ Testing...' : '🔄 Test Backend Connection'}
          </button>
        </div>

        <div className="info">
          <h3>✅ What's Working:</h3>
          <ul>
            <li>React frontend running on port 5173</li>
            <li>Ready to connect to FastAPI backend</li>
            <li>Modern development setup with Vite</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default App
