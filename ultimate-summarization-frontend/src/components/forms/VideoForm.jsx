import React, { useState } from 'react'
import './FormStyles.css'
import FileUpload from './FileUpload'
import LoadingSpinner from './LoadingSpinner'
import SummaryResponse from './SummaryResponse'
import { summarizeVideo } from '../../utils/api'

const VideoForm = () => {
  const [file, setFile] = useState(null)
  const [query, setQuery] = useState('Summarize this video')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [videoPreview, setVideoPreview] = useState(null)

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile)
    setError('')
    
    // Create a preview URL
    if (selectedFile) {
      const previewUrl = URL.createObjectURL(selectedFile)
      setVideoPreview(previewUrl)
    } else {
      setVideoPreview(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please upload a video file')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await summarizeVideo(file, query)
      setResult(response)
    } catch (err) {
      setError(err.message || 'An error occurred during video analysis')
    } finally {
      setIsLoading(false)
    }
  }
  
  // Clean up the preview URL when component unmounts
  React.useEffect(() => {
    return () => {
      if (videoPreview) {
        URL.revokeObjectURL(videoPreview)
      }
    }
  }, [videoPreview])

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <FileUpload 
          accept="video/*" 
          onFileSelect={handleFileSelect}
          label="Drop your video file here (MP4, MOV, etc.)"
        />

        {videoPreview && (
          <div className="video-preview">
            <video
              width="100%"
              height="auto"
              src={videoPreview}
              controls
            ></video>
          </div>
        )}

        <div className="form-group">
          <label>Specific Query (Optional)</label>
          <input
            type="text"
            className="form-control"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a specific question about the video..."
          />
          <small className="form-text">
            Default: "Summarize this video". You can ask specific questions like "What are the main points?" or "Explain the technical aspects."
          </small>
        </div>

        <p className="info-text">
          Video processing may take some time depending on the video length and complexity.
        </p>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={isLoading || !file}>
          Analyze Video
        </button>
      </form>

      {isLoading && <LoadingSpinner message="Processing video..." />}
      
      {result && <SummaryResponse response={result.summary} title="Video Summary" />}
    </div>
  )
}

export default VideoForm 