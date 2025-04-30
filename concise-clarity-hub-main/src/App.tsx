import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import AppLayout from './components/AppLayout';
import DocumentSummarizer from './components/DocumentSummarizer';
import YouTubeSummarizer from './components/YouTubeSummarizer';
import LegalSummarizer from './components/LegalSummarizer';
import ResumeSummarizer from './components/ResumeSummarizer';
import AudioSummarizer from './components/AudioSummarizer';
import VideoSummarizer from './components/VideoSummarizer';
import WebsiteSummarizer from './components/WebsiteSummarizer';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        
        <Route path="/app" element={<AppLayout />}>
          <Route path="document" element={<DocumentSummarizer />} />
          <Route path="youtube" element={<YouTubeSummarizer />} />
          <Route path="legal" element={<LegalSummarizer />} />
          <Route path="resume" element={<ResumeSummarizer />} />
          <Route path="audio" element={<AudioSummarizer />} />
          <Route path="video" element={<VideoSummarizer />} />
          <Route path="website" element={<WebsiteSummarizer />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
