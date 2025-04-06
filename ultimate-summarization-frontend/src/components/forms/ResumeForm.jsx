import React, { useState } from 'react'
import './FormStyles.css'
import FileUpload from './FileUpload'
import LoadingSpinner from './LoadingSpinner'
import SummaryResponse from './SummaryResponse'
import { analyzeResume } from '../../utils/api'

const ResumeForm = () => {
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
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
      setError('Please upload a resume (PDF)')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await analyzeResume(file, jobDescription)
      setResult(response)
    } catch (err) {
      setError(err.message || 'An error occurred during resume analysis')
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
          label="Drop your resume here (PDF only)"
        />

        <div className="form-group">
          <label>Job Description (Optional for ATS Compatibility Analysis)</label>
          <textarea
            className="form-control"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description to analyze how well your resume matches..."
            rows={5}
          />
          <small className="form-text">
            Adding a job description will enable ATS compatibility analysis to help optimize your resume.
          </small>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={isLoading || !file}>
          Analyze Resume
        </button>
      </form>

      {isLoading && <LoadingSpinner message="Analyzing resume..." />}
      
      {result && <SummaryResponse response={result} title="Resume Analysis" />}
    </div>
  )
}

export default ResumeForm 