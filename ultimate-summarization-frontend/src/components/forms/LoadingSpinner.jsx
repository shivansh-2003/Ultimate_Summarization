import React from 'react'
import '../Main.css'

const LoadingSpinner = ({ message = "Processing your request..." }) => {
  return (
    <div className="loader">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  )
}

export default LoadingSpinner 