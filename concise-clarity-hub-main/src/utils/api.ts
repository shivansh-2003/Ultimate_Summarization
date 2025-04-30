// API Configuration
export const API_BASE_URL = 'https://ultimate-summarization.onrender.com';

// Error handling utility
export const handleApiError = async (response: Response) => {
  if (!response.ok) {
    try {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Error: ${response.status} ${response.statusText}`);
    } catch (e) {
      if (e instanceof SyntaxError) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      throw e;
    }
  }
  return response;
};

// General document summarization
export const summarizeGeneralDocument = async (file: File, options?: {
  conciseness?: string;
  extract_topics?: boolean;
  extract_key_points?: boolean;
  include_statistics?: boolean;
  summary_length_percentage?: number;
}) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (options) {
    if (options.conciseness) formData.append('conciseness', options.conciseness);
    if (options.extract_topics !== undefined) formData.append('extract_topics', options.extract_topics.toString());
    if (options.extract_key_points !== undefined) formData.append('extract_key_points', options.extract_key_points.toString());
    if (options.include_statistics !== undefined) formData.append('include_statistics', options.include_statistics.toString());
    if (options.summary_length_percentage) formData.append('summary_length_percentage', options.summary_length_percentage.toString());
  }

  const response = await fetch(`${API_BASE_URL}/api/general/summarize`, {
    method: 'POST',
    body: formData,
  });
  
  await handleApiError(response);
  return response.json();
};

// Legal document summarization
export const summarizeLegalDocument = async (file: File, customQuestion?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (customQuestion) {
    formData.append('custom_question', customQuestion);
  }

  const response = await fetch(`${API_BASE_URL}/api/legal/summarize`, {
    method: 'POST',
    body: formData,
  });
  
  await handleApiError(response);
  return response.json();
};

// Resume analysis
export const analyzeResume = async (file: File, jobDescription?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (jobDescription) {
    formData.append('job_description', jobDescription);
  }

  const response = await fetch(`${API_BASE_URL}/api/resume/analyze`, {
    method: 'POST',
    body: formData,
  });
  
  await handleApiError(response);
  return response.json();
};

// Audio processing
export const processAudio = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/process-audio`, {
    method: 'POST',
    body: formData,
  });
  
  await handleApiError(response);
  return response.json();
};

// YouTube video summarization
export const summarizeYouTube = async (url: string, query: string = "Summarize this video") => {
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
  
  await handleApiError(response);
  return response.json();
};

// Video file summarization
export const summarizeVideo = async (file: File, query: string = "Summarize this video") => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('query', query);

  const response = await fetch(`${API_BASE_URL}/summarize/video`, {
    method: 'POST',
    body: formData,
  });
  
  await handleApiError(response);
  return response.json();
};

// Website summarization
export const summarizeWebsite = async (url: string, summaryLength: string = "Medium") => {
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
  
  await handleApiError(response);
  return response.json();
};
