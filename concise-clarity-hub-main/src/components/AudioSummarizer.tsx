import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from "@/hooks/use-toast";
import { processAudio } from '@/utils/api';

const AudioSummarizer: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<null | any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const validTypes = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'];
      const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
      
      if (!validTypes.some(type => fileExtension.endsWith(type))) {
        toast({
          title: "Invalid file type",
          description: "Please upload a supported audio file format",
          variant: "destructive"
        });
        return;
      }
      
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      toast({
        title: "Error",
        description: "Please select an audio file to upload",
        variant: "destructive"
      });
      return;
    }
    
    // Check file size (limit to 25MB)
    if (file.size > 25 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please select an audio file smaller than 25MB",
        variant: "destructive"
      });
      return;
    }
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await processAudio(file);
      setResult(data);
      toast({
        title: "Success",
        description: "Audio successfully processed",
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

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Audio Summarizer</h2>
        <p className="text-lightGray">
          Upload any audio file to transcribe and summarize its content.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="audio-file">Upload Audio</Label>
          <Input
            id="audio-file"
            type="file"
            onChange={handleFileChange}
            accept=".mp3,.wav,.m4a,.ogg,.flac,.aac"
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">Supported formats: MP3, WAV, M4A, OGG, FLAC, AAC (Max 25MB)</p>
        </div>
        
        {file && (
          <div className="p-4 bg-jetBlack rounded-md flex items-center">
            <div className="w-8 h-8 bg-vibrantOrange bg-opacity-10 rounded-lg flex items-center justify-center mr-3">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-vibrantOrange">
                <path d="M9 18V5l12-2v13"></path>
                <circle cx="6" cy="18" r="3"></circle>
                <circle cx="18" cy="16" r="3"></circle>
              </svg>
            </div>
            <div className="flex-1 truncate">
              <p className="text-white text-sm font-medium truncate">{file.name}</p>
              <p className="text-lightGray text-xs">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
          </div>
        )}
        
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
            "Transcribe & Summarize"
          )}
        </Button>
      </form>
      
      {result && (
        <div className="rounded-md bg-darkGray p-4 border border-muted animate-fade-in">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-vibrantOrange mr-2"></span>
            Results
          </h3>
          <div className="divider mb-4"></div>
          
          {result.transcript && (
            <div className="mb-6">
              <h4 className="text-md font-medium text-white mb-2">Transcript</h4>
              <div className="max-h-60 overflow-y-auto bg-jetBlack p-3 rounded-md text-white text-sm whitespace-pre-line">
                {result.transcript}
              </div>
            </div>
          )}
          
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

export default AudioSummarizer;