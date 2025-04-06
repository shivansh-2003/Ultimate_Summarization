import React, { useState } from 'react'
import './FormStyles.css'
import FileUpload from './FileUpload'
import LoadingSpinner from './LoadingSpinner'
import SummaryResponse from './SummaryResponse'
import { processAudio } from '../../utils/api'

const AudioForm = () => {
  const [file, setFile] = useState(null)
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
      setError('Please upload an audio file')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await processAudio(file)
      setResult(response)
    } catch (err) {
      setError(err.message || 'An error occurred during audio processing')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <FileUpload 
          accept="audio/*" 
          onFileSelect={handleFileSelect}
          label="Drop your audio file here (MP3, WAV, etc.)"
        />

        <p className="info-text">
          Upload any audio file to transcribe its content and generate a summary.
          Common formats include MP3, WAV, M4A, and OGG.
        </p>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={isLoading || !file}>
          Process Audio
        </button>
      </form>

      {isLoading && <LoadingSpinner message="Processing audio..." />}
      
      {result && (
        <div>
          <SummaryResponse 
            response={{summary: result.summary}}
            title="Audio Summary" 
          />
          
          <div className="response-container">
            <div className="response-header">
              <h3>Full Transcript</h3>
            </div>
            <div className="summary-text">
              {result.transcript}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AudioForm 