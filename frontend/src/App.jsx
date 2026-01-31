import { useState, useEffect } from 'react'
import Login from './components/Login'
import Register from './components/Register'
import Dashboard from './components/Dashboard'
import { isAuthenticated } from './utils/api'
import './App.css'

function App() {
  // State to track which page to show
  const [currentView, setCurrentView] = useState('login') // 'login', 'register', or 'dashboard'
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // Check if user is already logged in on component mount
  useEffect(() => {
    if (isAuthenticated()) {
      setIsLoggedIn(true)
      setCurrentView('dashboard')
    }
  }, [])

  // Handle successful login
  const handleLoginSuccess = () => {
    setIsLoggedIn(true)
    setCurrentView('dashboard')
  }

  // Handle successful registration
  const handleRegisterSuccess = () => {
    setCurrentView('login')
  }

  // Handle logout
  const handleLogout = () => {
    setIsLoggedIn(false)
    setCurrentView('login')
  }

  // Switch between login and register
  const switchToLogin = () => setCurrentView('login')
  const switchToRegister = () => setCurrentView('register')

  // Render the appropriate view
  if (isLoggedIn && currentView === 'dashboard') {
    return <Dashboard onLogout={handleLogout} />
  }

  if (currentView === 'register') {
    return (
      <Register 
        onSwitchToLogin={switchToLogin}
        onRegisterSuccess={handleRegisterSuccess}
      />
    )
  }

  // Default to login
  return (
    <Login 
      onSwitchToRegister={switchToRegister}
      onLoginSuccess={handleLoginSuccess}
    />
  )
}

export default App