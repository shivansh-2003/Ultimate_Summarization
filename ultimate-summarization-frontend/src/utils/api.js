const API_BASE_URL = 'https://ultimate-summarization.onrender.com';

// General document summarization
export const summarizeGeneralDocument = async (file, options) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (options) {
    if (options.conciseness) formData.append('conciseness', options.conciseness);
    if (options.extract_topics !== undefined) formData.append('extract_topics', options.extract_topics);
    if (options.extract_key_points !== undefined) formData.append('extract_key_points', options.extract_key_points);
    if (options.include_statistics !== undefined) formData.append('include_statistics', options.include_statistics);
    if (options.summary_length_percentage) formData.append('summary_length_percentage', options.summary_length_percentage);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/general/summarize`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to summarize document');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error summarizing document:', error);
    throw error;
  }
};

// Legal document summarization
export const summarizeLegalDocument = async (file, customQuestion) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (customQuestion) {
    formData.append('custom_question', customQuestion);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/legal/summarize`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to summarize legal document');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error summarizing legal document:', error);
    throw error;
  }
};

// Resume analysis
export const analyzeResume = async (file, jobDescription) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (jobDescription) {
    formData.append('job_description', jobDescription);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/resume/analyze`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to analyze resume');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error analyzing resume:', error);
    throw error;
  }
};

// Audio processing
export const processAudio = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${API_BASE_URL}/api/process-audio`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to process audio');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error processing audio:', error);
    throw error;
  }
};

// YouTube video summarization
export const summarizeYouTube = async (url, query = "Summarize this video") => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/summarize/youtube`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url,
        query,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to summarize YouTube video');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error summarizing YouTube video:', error);
    throw error;
  }
};

// Video file summarization
export const summarizeVideo = async (file, query = "Summarize this video") => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('query', query);

  try {
    const response = await fetch(`${API_BASE_URL}/summarize/video`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to summarize video');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error summarizing video:', error);
    throw error;
  }
};

// Website summarization
export const summarizeWebsite = async (url, summaryLength = "Medium") => {
  try {
    const response = await fetch(`${API_BASE_URL}/summarize/website`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url,
        summary_length: summaryLength,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to summarize website');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error summarizing website:', error);
    throw error;
  }
}; 