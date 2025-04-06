import React, { useState } from 'react'
import './FormStyles.css'
import FileUpload from './FileUpload'
import LoadingSpinner from './LoadingSpinner'
import SummaryResponse from './SummaryResponse'
import { summarizeGeneralDocument } from '../../utils/api'

const DocumentForm = () => {
  const [file, setFile] = useState(null)
  const [conciseness, setConciseness] = useState('balanced')
  const [extractTopics, setExtractTopics] = useState(true)
  const [extractKeyPoints, setExtractKeyPoints] = useState(true)
  const [includeStatistics, setIncludeStatistics] = useState(false)
  const [summaryLengthPercentage, setSummaryLengthPercentage] = useState(30)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile)
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please upload a document file')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const options = {
        conciseness,
        extract_topics: extractTopics,
        extract_key_points: extractKeyPoints,
        include_statistics: includeStatistics,
        summary_length_percentage: summaryLengthPercentage
      }

      const response = await summarizeGeneralDocument(file, options)
      setResult(response)
    } catch (err) {
      setError(err.message || 'An error occurred during summarization')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <FileUpload 
          accept=".pdf,.docx,.txt" 
          onFileSelect={handleFileSelect}
          label="Drop your document here (PDF, DOCX, TXT)"
        />

        <div className="form-group">
          <label>Conciseness Level</label>
          <select 
            className="form-control"
            value={conciseness}
            onChange={(e) => setConciseness(e.target.value)}
          >
            <option value="concise">Concise</option>
            <option value="balanced">Balanced</option>
            <option value="detailed">Detailed</option>
          </select>
        </div>

        <div className="form-group">
          <label>Summary Length (% of original)</label>
          <input
            type="range"
            min="10"
            max="50"
            step="5"
            value={summaryLengthPercentage}
            onChange={(e) => setSummaryLengthPercentage(Number(e.target.value))}
            className="form-control"
          />
          <div className="range-value">{summaryLengthPercentage}%</div>
        </div>

        <div className="form-group">
          <label>Options</label>
          <div className="options-container">
            <div className="checkbox-group">
              <input 
                type="checkbox" 
                id="extractTopics"
                checked={extractTopics}
                onChange={(e) => setExtractTopics(e.target.checked)}
              />
              <label htmlFor="extractTopics">Extract Topics</label>
            </div>

            <div className="checkbox-group">
              <input 
                type="checkbox" 
                id="extractKeyPoints"
                checked={extractKeyPoints}
                onChange={(e) => setExtractKeyPoints(e.target.checked)}
              />
              <label htmlFor="extractKeyPoints">Extract Key Points</label>
            </div>

            <div className="checkbox-group">
              <input 
                type="checkbox" 
                id="includeStatistics"
                checked={includeStatistics}
                onChange={(e) => setIncludeStatistics(e.target.checked)}
              />
              <label htmlFor="includeStatistics">Include Statistics</label>
            </div>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={isLoading || !file}>
          Summarize Document
        </button>
      </form>

      {isLoading && <LoadingSpinner message="Analyzing document..." />}
      
      {result && <SummaryResponse response={result} title="Document Summary" />}
    </div>
  )
}

export default DocumentForm 