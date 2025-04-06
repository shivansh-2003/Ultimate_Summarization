import React from 'react'
import './Main.css'
import DocumentForm from './forms/DocumentForm'
import LegalForm from './forms/LegalForm'
import ResumeForm from './forms/ResumeForm'
import AudioForm from './forms/AudioForm'
import YouTubeForm from './forms/YouTubeForm'
import VideoForm from './forms/VideoForm'
import WebsiteForm from './forms/WebsiteForm'

const Main = ({ activeTab }) => {
  const renderForm = () => {
    switch (activeTab) {
      case 'document':
        return <DocumentForm />
      case 'legal':
        return <LegalForm />
      case 'resume':
        return <ResumeForm />
      case 'audio':
        return <AudioForm />
      case 'youtube':
        return <YouTubeForm />
      case 'video':
        return <VideoForm />
      case 'website':
        return <WebsiteForm />
      default:
        return <DocumentForm />
    }
  }

  return (
    <main className="main-content">
      <div className="content-header">
        <h2>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Summarization</h2>
        <p className="description">
          {getDescription(activeTab)}
        </p>
      </div>
      <div className="form-container">
        {renderForm()}
      </div>
    </main>
  )
}

const getDescription = (activeTab) => {
  const descriptions = {
    document: 'Upload any document (PDF, DOCX, TXT) to generate a concise summary.',
    legal: 'Analyze legal documents with specialized processing for contracts, agreements, and more.',
    resume: 'Evaluate resumes and compare them against job descriptions for compatibility.',
    audio: 'Transcribe and summarize audio files to extract key information.',
    youtube: 'Summarize YouTube videos by providing the video URL.',
    video: 'Upload and analyze video files to generate summaries.',
    website: 'Extract and summarize content from any website URL.'
  }

  return descriptions[activeTab] || descriptions.document
}

export default Main 