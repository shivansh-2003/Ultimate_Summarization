import React from 'react'
import '../Main.css'

const SummaryResponse = ({ response, title = "Summary Results" }) => {
  if (!response) return null

  return (
    <div className="response-container">
      <div className="response-header">
        <h3>{title}</h3>
      </div>
      
      {typeof response === 'string' ? (
        <div className="summary-text">{response}</div>
      ) : (
        <div className="summary-text">
          {Object.entries(response).map(([key, value]) => {
            // Skip rendering if the value is null, undefined, or an empty string
            if (value === null || value === undefined || value === '') return null
            
            // Handle nested objects
            if (typeof value === 'object' && value !== null) {
              return (
                <div key={key} className="response-section">
                  <h4>{formatKey(key)}</h4>
                  <pre>{JSON.stringify(value, null, 2)}</pre>
                </div>
              )
            }
            
            // Handle simple key-value pairs
            return (
              <div key={key} className="response-section">
                <h4>{formatKey(key)}</h4>
                <p>{value}</p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// Helper function to format keys as readable titles
const formatKey = (key) => {
  return key
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
}

export default SummaryResponse 