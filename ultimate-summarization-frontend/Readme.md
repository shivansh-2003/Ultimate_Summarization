# Ultimate Summarization Frontend

A modern, clean, and responsive React frontend for the Ultimate Summarization API. This application provides a user-friendly interface for summarizing and analyzing various types of content.

## Features

- **Document Summarization**: Process and summarize general documents (PDF, DOCX, TXT)
- **Legal Document Analysis**: Specialized analysis for legal documents
- **Resume Evaluation**: Extract structured information from resumes with optional ATS compatibility analysis
- **Audio Processing**: Transcribe and summarize audio files
- **Video Summarization**: Process YouTube videos and uploaded video files
- **Website Content Extraction**: Extract and summarize content from any website

## Tech Stack

- React
- CSS (with custom variables for theming)
- Fetch API for backend communication

## Getting Started

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Installation

1. Clone the repository
```bash
git clone https://github.com/username/Ultimate_Summarization.git
cd Ultimate_Summarization/ultimate-summarization-frontend
```

2. Install dependencies
```bash
npm install
# or
yarn
```

3. Start the development server
```bash
npm run dev
# or
yarn dev
```

4. Open your browser and navigate to `http://localhost:5173`

## Backend Connection

The frontend connects to the Ultimate Summarization API deployed at:
```
https://ultimate-summarization.onrender.com
```

## Project Structure

- `/src/components` - React components
  - `/src/components/forms` - Form components for different summarization types
- `/src/utils` - Utility functions including API calls

## Deployment

To build the application for production:

```bash
npm run build
# or
yarn build
```

The built files will be in the `dist` directory, ready for deployment to any static hosting service.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request