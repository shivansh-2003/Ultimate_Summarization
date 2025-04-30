import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from "@/hooks/use-toast";
import { summarizeYouTube } from '@/utils/api';

const YouTubeSummarizer: React.FC = () => {
  const [url, setUrl] = useState('');
  const [query, setQuery] = useState('Summarize this video');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<null | string>(null);
  const [previewId, setPreviewId] = useState<null | string>(null);

  const extractYouTubeId = (url: string) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    
    // Extract and set YouTube ID for preview
    const youtubeId = extractYouTubeId(newUrl);
    setPreviewId(youtubeId);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url) {
      toast({
        title: "Error",
        description: "Please enter a YouTube URL",
        variant: "destructive"
      });
      return;
    }

    const youtubeId = extractYouTubeId(url);
    if (!youtubeId) {
      toast({
        title: "Error",
        description: "Invalid YouTube URL",
        variant: "destructive"
      });
      return;
    }
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await summarizeYouTube(url, query);
      setResult(data.summary);
      toast({
        title: "Success",
        description: "YouTube video successfully summarized",
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during summarization';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive"
      });
      console.error('API Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">YouTube Video Summarizer</h2>
        <p className="text-lightGray">
          Enter a YouTube URL to generate a concise summary of the video content.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="url">YouTube URL</Label>
          <Input
            id="url"
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={handleUrlChange}
            required
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">Enter a valid YouTube video URL</p>
        </div>
        
        {previewId && (
          <div className="mt-4 rounded-md overflow-hidden">
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
        
        <div className="space-y-2">
          <Label htmlFor="query">Custom Query (Optional)</Label>
          <Input
            id="query"
            type="text"
            placeholder="Ask a specific question about the video..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">
            Default: "Summarize this video". You can ask specific questions like "What are the main points?" or "Explain the technical aspects."
          </p>
        </div>
        
        <Button
          type="submit"
          disabled={isLoading || !url}
          className={cn(
            "w-full bg-vibrantOrange hover:bg-opacity-90 text-white",
            isLoading && "opacity-80"
          )}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Summarizing...
            </div>
          ) : (
            "Summarize YouTube Video"
          )}
        </Button>
      </form>
      
      {result && (
        <div className="rounded-md bg-darkGray p-4 border border-muted animate-fade-in">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-vibrantOrange mr-2"></span>
            Summary Result
          </h3>
          <div className="divider"></div>
          <div className="text-white whitespace-pre-line">
            {result}
          </div>
        </div>
      )}
    </div>
  );
};

export default YouTubeSummarizer; 