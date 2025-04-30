import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from "@/hooks/use-toast";
import { summarizeVideo } from '@/utils/api';

const VideoSummarizer: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('Summarize this video');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<null | any>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const validTypes = ['.mp4', '.mov', '.avi', '.mkv', '.webm'];
      const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
      
      if (!validTypes.some(type => fileExtension.endsWith(type))) {
        toast({
          title: "Invalid file type",
          description: "Please upload a supported video file format",
          variant: "destructive"
        });
        return;
      }
      
      // Check file size (limit to 100MB)
      if (selectedFile.size > 100 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Please select a video file smaller than 100MB",
          variant: "destructive"
        });
        return;
      }
      
      setFile(selectedFile);
      
      // Create a preview URL for the video
      const previewUrl = URL.createObjectURL(selectedFile);
      setVideoPreview(previewUrl);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      toast({
        title: "Error",
        description: "Please select a video file to upload",
        variant: "destructive"
      });
      return;
    }
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await summarizeVideo(file, query);
      setResult(data);
      toast({
        title: "Success",
        description: "Video successfully processed and summarized",
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during processing';
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

  // Clean up the preview URL when component unmounts or when file changes
  React.useEffect(() => {
    return () => {
      if (videoPreview) {
        URL.revokeObjectURL(videoPreview);
      }
    };
  }, [videoPreview]);

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Video Summarizer</h2>
        <p className="text-lightGray">
          Upload a video file to generate a concise summary of its content.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="video-file">Upload Video</Label>
          <Input
            id="video-file"
            type="file"
            onChange={handleFileChange}
            accept=".mp4,.mov,.avi,.mkv,.webm"
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">Supported formats: MP4, MOV, AVI, MKV, WEBM (Max 100MB)</p>
        </div>
        
        {videoPreview && (
          <div className="mt-4 rounded-md overflow-hidden">
            <video 
              controls 
              width="100%" 
              height="auto" 
              className="max-h-[300px]"
            >
              <source src={videoPreview} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}
        
        <div className="space-y-2">
          <Label htmlFor="query">Custom Query (Optional)</Label>
          <Textarea
            id="query"
            placeholder="Ask a specific question about the video..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange min-h-[100px]"
          />
          <p className="text-xs text-lightGray">
            Default: "Summarize this video". You can ask specific questions like "What are the main points?" or "Explain the technical aspects."
          </p>
        </div>
        
        <Button
          type="submit"
          disabled={isLoading || !file}
          className={cn(
            "w-full bg-vibrantOrange hover:bg-opacity-90 text-white",
            isLoading && "opacity-80"
          )}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Processing...
            </div>
          ) : (
            "Summarize Video"
          )}
        </Button>
      </form>
      
      {result && (
        <div className="rounded-md bg-darkGray p-4 border border-muted animate-fade-in">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-vibrantOrange mr-2"></span>
            Summary Result
          </h3>
          <div className="divider mb-4"></div>
          
          {result.summary && (
            <div className="mb-4">
              <h4 className="text-md font-medium text-white mb-2">Summary</h4>
              <div className="text-white whitespace-pre-line">
                {result.summary}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoSummarizer; 