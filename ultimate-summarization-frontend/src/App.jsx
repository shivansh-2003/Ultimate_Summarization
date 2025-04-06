import { useState } from 'react'
import './App.css'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Main from './components/Main'

function App() {
  const [activeTab, setActiveTab] = useState('document')

  return (
    <div className="app-container">
      <Header />
      <div className="content-container">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <Main activeTab={activeTab} />
      </div>
    </div>
  )
}

export default App
