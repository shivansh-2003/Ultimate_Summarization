import React, { useState } from 'react'
import './FormStyles.css'
import LoadingSpinner from './LoadingSpinner'
import SummaryResponse from './SummaryResponse'
import { summarizeWebsite } from '../../utils/api'

const WebsiteForm = () => {
  const [url, setUrl] = useState('')
  const [summaryLength, setSummaryLength] = useState('Medium')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url) {
      setError('Please enter a website URL')
      return
    }

    // Basic URL validation
    try {
      new URL(url)
    } catch (err) {
      setError('Please enter a valid URL (including https://)')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await summarizeWebsite(url, summaryLength)
      setResult(response)
    } catch (err) {
      setError(err.message || 'An error occurred during website analysis')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Website URL</label>
          <input
            type="url"
            className="form-control"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            required
          />
          <small className="form-text">
            Enter the full URL including the protocol (https://)
          </small>
        </div>

        <div className="form-group">
          <label>Summary Length</label>
          <select 
            className="form-control"
            value={summaryLength}
            onChange={(e) => setSummaryLength(e.target.value)}
          >
            <option value="Short">Short (about 100 words)</option>
            <option value="Medium">Medium (about 300 words)</option>
            <option value="Long">Long (about 500 words)</option>
          </select>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={isLoading || !url}>
          Summarize Website
        </button>
      </form>

      {isLoading && <LoadingSpinner message="Extracting website content..." />}
      
      {result && (
        <SummaryResponse 
          response={{
            summary: result.summary,
            url: result.url,
            summary_length: result.summary_length
          }} 
          title="Website Summary" 
        />
      )}
    </div>
  )
}

export default WebsiteForm 