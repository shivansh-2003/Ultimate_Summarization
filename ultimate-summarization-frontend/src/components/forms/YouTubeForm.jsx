import React, { useState } from 'react'
import './FormStyles.css'
import LoadingSpinner from './LoadingSpinner'
import SummaryResponse from './SummaryResponse'
import { summarizeYouTube } from '../../utils/api'

const YouTubeForm = () => {
  const [url, setUrl] = useState('')
  const [query, setQuery] = useState('Summarize this video')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [previewId, setPreviewId] = useState(null)

  const extractYouTubeId = (url) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/
    const match = url.match(regExp)
    return (match && match[2].length === 11) ? match[2] : null
  }

  const handleUrlChange = (e) => {
    const newUrl = e.target.value
    setUrl(newUrl)
    setError('')
    
    // Extract and set YouTube ID for preview
    const youtubeId = extractYouTubeId(newUrl)
    setPreviewId(youtubeId)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url) {
      setError('Please enter a YouTube URL')
      return
    }

    const youtubeId = extractYouTubeId(url)
    if (!youtubeId) {
      setError('Invalid YouTube URL')
      return
    }

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await summarizeYouTube(url, query)
      setResult(response)
    } catch (err) {
      setError(err.message || 'An error occurred during YouTube video analysis')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>YouTube URL</label>
          <input
            type="url"
            className="form-control"
            value={url}
            onChange={handleUrlChange}
            placeholder="https://www.youtube.com/watch?v=..."
            required
          />
        </div>

        {previewId && (
          <div className="video-preview">
            <iframe
              width="100%"
              height="315"
              src={`https://www.youtube.com/embed/${previewId}`}
              title="YouTube video preview"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
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

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="btn btn-primary" disabled={isLoading || !url}>
          Summarize YouTube Video
        </button>
      </form>

      {isLoading && <LoadingSpinner message="Analyzing YouTube video..." />}
      
      {result && <SummaryResponse response={result.summary} title="YouTube Video Summary" />}
    </div>
  )
}

export default YouTubeForm 