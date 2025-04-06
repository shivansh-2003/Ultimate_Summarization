import React, { useState } from 'react'
import './FormStyles.css'
import FileUpload from './FileUpload'
import LoadingSpinner from './LoadingSpinner'
import SummaryResponse from './SummaryResponse'
import { summarizeLegalDocument } from '../../utils/api'

const LegalForm = () => {
  const [file, setFile] = useState(null)
  const [customQuestion, setCustomQuestion] = useState('')
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
      setError('Please upload a legal document (PDF)')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await summarizeLegalDocument(file, customQuestion)
      setResult(response)
    } catch (err) {
      setError(err.message || 'An error occurred during legal document analysis')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <FileUpload 
          accept=".pdf" 
          onFileSelect={handleFileSelect}
          label="Drop your legal document here (PDF only)"
        />

        <div className="form-group">
          <label>Custom Question (Optional)</label>
          <textarea
            className="form-control"
            value={customQuestion}
            onChange={(e) => setCustomQuestion(e.target.value)}
            placeholder="Ask a specific question about the legal document..."
            rows={3}
          />
          <small className="form-text">
            For example: "What are the termination conditions?" or "Explain the liability clauses."
          </small>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={isLoading || !file}>
          Analyze Legal Document
        </button>
      </form>

      {isLoading && <LoadingSpinner message="Analyzing legal document..." />}
      
      {result && (
        <SummaryResponse 
          response={{
            document_type: result.document_type,
            summary: result.summary,
            processing_time: `${result.processing_time.toFixed(2)} seconds`
          }} 
          title="Legal Document Analysis" 
        />
      )}
    </div>
  )
}

export default LegalForm 