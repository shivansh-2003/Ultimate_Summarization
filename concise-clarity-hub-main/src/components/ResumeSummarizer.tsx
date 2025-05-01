import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from "@/hooks/use-toast";
import { analyzeResume } from '@/utils/api';

const ResumeSummarizer: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<null | any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF file for resume analysis",
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
        description: "Please select a resume to upload",
        variant: "destructive"
      });
      return;
    }
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await analyzeResume(file, jobDescription || undefined);
      setResult(data);
      toast({
        title: "Success",
        description: "Resume successfully analyzed",
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during analysis';
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

  const formatKey = (key: string) => {
    return key
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (str) => str.toUpperCase());
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Resume Analyzer</h2>
        <p className="text-lightGray">
          Upload a resume (PDF format) for analysis and optionally compare against a job description.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="resume-file">Upload Resume</Label>
          <Input
            id="resume-file"
            type="file"
            onChange={handleFileChange}
            accept=".pdf"
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">Supported format: PDF</p>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="job-description">Job Description (Optional)</Label>
          <Textarea
            id="job-description"
            placeholder="Paste the job description to compare with the resume..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange min-h-[150px]"
          />
          <p className="text-xs text-lightGray">
            If provided, the resume will be compared against this job description for compatibility analysis.
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
              Analyzing...
            </div>
          ) : (
            "Analyze Resume"
          )}
        </Button>
      </form>
      
      {result && (
        <div className="rounded-md bg-darkGray p-4 border border-muted animate-fade-in">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-vibrantOrange mr-2"></span>
            Resume Analysis
          </h3>
          <div className="divider mb-4"></div>
          
          {Object.entries(result).map(([key, value]) => {
            // Skip rendering if the value is null, undefined, or an empty string/array
            if (
              value === null || 
              value === undefined || 
              value === '' || 
              (Array.isArray(value) && value.length === 0)
            ) return null;
            
            // Handle special case for match_percentage
            if (key === 'match_percentage') {
              return (
                <div key={key} className="mb-4">
                  <h4 className="text-md font-medium text-white mb-1">{formatKey(key)}</h4>
                  <div className="mt-2">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-white">Match Score</span>
                      <span className="text-white">{String(value)}%</span>
                    </div>
                    <div className="w-full bg-jetBlack rounded-full h-2.5">
                      <div 
                        className="bg-vibrantOrange h-2.5 rounded-full" 
                        style={{ width: `${Number(value)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            }
            
            // Handle arrays (skills, improvement_suggestions)
            if (Array.isArray(value)) {
              // Special case for skills
              if (key === 'skills') {
                return (
                  <div key={key} className="mb-4">
                    <h4 className="text-md font-medium text-white mb-1">{formatKey(key)}</h4>
                    <div className="flex flex-wrap gap-2">
                      {value.map((skill: string, idx: number) => (
                        <span key={idx} className="bg-jetBlack text-white text-xs px-2 py-1 rounded-full">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              }
              
              // Other arrays
              return (
                <div key={key} className="mb-4">
                  <h4 className="text-md font-medium text-white mb-1">{formatKey(key)}</h4>
                  <ul className="list-disc list-inside space-y-1 text-white">
                    {value.map((item: string, idx: number) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              );
            }
            
            // Handle objects
            if (typeof value === 'object' && value !== null) {
              return (
                <div key={key} className="mb-4">
                  <h4 className="text-md font-medium text-white mb-1">{formatKey(key)}</h4>
                  <pre className="text-white text-sm overflow-x-auto">
                    {JSON.stringify(value, null, 2)}
                  </pre>
                </div>
              );
            }
            
            // Handle text content
            return (
              <div key={key} className="mb-4">
                <h4 className="text-md font-medium text-white mb-1">{formatKey(key)}</h4>
                <div className="text-white whitespace-pre-line">
                  {String(value)}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ResumeSummarizer; 