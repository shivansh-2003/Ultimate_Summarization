import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from "@/hooks/use-toast";
import { summarizeGeneralDocument } from '@/utils/api';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';

interface SummarizerOptions {
  conciseness: 'detailed' | 'balanced' | 'concise';
  extract_topics: boolean;
  extract_key_points: boolean;
  include_statistics: boolean;
  summary_length_percentage: number;
}

interface SummaryResult {
  summary?: string;
  topics?: string[];
  key_points?: string[];
  statistics?: Record<string, any>;
  [key: string]: any;
}

const DocumentSummarizer: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SummaryResult | null>(null);
  const [options, setOptions] = useState<SummarizerOptions>({
    conciseness: 'balanced',
    extract_topics: true,
    extract_key_points: true,
    include_statistics: false,
    summary_length_percentage: 30
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const validTypes = ['.pdf', '.docx', '.txt'];
      const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
      
      if (!validTypes.includes(fileExtension)) {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF, DOCX, or TXT file",
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
        description: "Please select a document to upload",
        variant: "destructive"
      });
      return;
    }
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await summarizeGeneralDocument(file, options);
      setResult(data);
      toast({
        title: "Success",
        description: "Document successfully summarized",
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

  const formatKey = (key: string): string => {
    return key
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (str) => str.toUpperCase());
  };

  // Custom renderer for different result types
  const renderSummarySection = (key: string, value: any) => {
    // Skip rendering if the value is null, undefined, or an empty string/array
    if (
      value === null || 
      value === undefined || 
      value === '' || 
      (Array.isArray(value) && value.length === 0)
    ) return null;
    
    // Handle arrays (topics, key_points)
    if (Array.isArray(value)) {
      return (
        <div key={key} className="mb-6">
          <h4 className="text-md font-medium text-white mb-2">{formatKey(key)}</h4>
          <ul className="list-disc list-inside space-y-1 text-white">
            {value.map((item: string, idx: number) => (
              <li key={idx}>{String(item)}</li>
            ))}
          </ul>
        </div>
      );
    }
    
    // Handle objects (statistics)
    if (typeof value === 'object' && value !== null) {
      return (
        <div key={key} className="mb-6">
          <h4 className="text-md font-medium text-white mb-2">{formatKey(key)}</h4>
          <div className="grid grid-cols-2 gap-2 text-sm text-white">
            {Object.entries(value).map(([statKey, statValue]) => (
              <div key={statKey} className="flex justify-between">
                <span className="font-medium">{statKey.replace(/_/g, ' ')}:</span>
                <span>{String(statValue)}</span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    
    // Handle text content (summary)
    return (
      <div key={key} className="mb-6">
        <h4 className="text-md font-medium text-white mb-2">{formatKey(key)}</h4>
        <div className="text-white whitespace-pre-line">
          {String(value)}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Document Summarizer</h2>
        <p className="text-lightGray">
          Upload any document (PDF, DOCX, TXT) to generate a concise summary.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="document-file">Upload Document</Label>
          <Input
            id="document-file"
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt"
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">Supported formats: PDF, DOCX, TXT</p>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="conciseness">Conciseness Level</Label>
          <Select 
            value={options.conciseness} 
            onValueChange={(value: 'detailed' | 'balanced' | 'concise') => setOptions({...options, conciseness: value})}
          >
            <SelectTrigger id="conciseness" className="bg-darkGray border-muted text-white focus:border-vibrantOrange">
              <SelectValue placeholder="Select conciseness level" />
            </SelectTrigger>
            <SelectContent className="bg-darkGray text-white border-muted">
              <SelectItem value="detailed">Detailed</SelectItem>
              <SelectItem value="balanced">Balanced</SelectItem>
              <SelectItem value="concise">Concise</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="summary_length_percentage">Summary Length (% of original)</Label>
          <div className="flex items-center space-x-4">
            <Slider
              id="summary_length_percentage"
              min={10}
              max={50}
              step={5}
              value={[options.summary_length_percentage]}
              onValueChange={(value) => setOptions({...options, summary_length_percentage: value[0]})}
              className="flex-1"
            />
            <span className="text-white">{options.summary_length_percentage}%</span>
          </div>
        </div>
        
        <div className="space-y-4">
          <Label>Summary Options</Label>
          
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="extract_topics" 
              checked={options.extract_topics}
              onCheckedChange={(checked) => 
                setOptions({...options, extract_topics: checked === true})
              }
            />
            <label
              htmlFor="extract_topics"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-white"
            >
              Extract Topics
            </label>
          </div>
          
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="extract_key_points" 
              checked={options.extract_key_points}
              onCheckedChange={(checked) => 
                setOptions({...options, extract_key_points: checked === true})
              }
            />
            <label
              htmlFor="extract_key_points"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-white"
            >
              Extract Key Points
            </label>
          </div>
          
          <div className="flex items-center space-x-2">
            <Checkbox 
              id="include_statistics" 
              checked={options.include_statistics}
              onCheckedChange={(checked) => 
                setOptions({...options, include_statistics: checked === true})
              }
            />
            <label
              htmlFor="include_statistics"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-white"
            >
              Include Statistics
            </label>
          </div>
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
              Summarizing...
            </div>
          ) : (
            "Summarize Document"
          )}
        </Button>
      </form>
      
      {result && (
        <div className="rounded-md bg-darkGray p-4 border border-muted animate-fade-in">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-vibrantOrange mr-2"></span>
            Document Summary
          </h3>
          <div className="divider mb-4"></div>
          
          {/* Render summary first if it exists */}
          {result.summary && renderSummarySection('summary', result.summary)}
          
          {/* Render topics if they exist */}
          {result.topics && result.topics.length > 0 && renderSummarySection('topics', result.topics)}
          
          {/* Render key points if they exist */}
          {result.key_points && result.key_points.length > 0 && renderSummarySection('key_points', result.key_points)}
          
          {/* Render statistics if they exist */}
          {result.statistics && Object.keys(result.statistics).length > 0 && renderSummarySection('statistics', result.statistics)}
          
          {/* Render any other fields that might exist in the API response */}
          {Object.entries(result)
            .filter(([key]) => !['summary', 'topics', 'key_points', 'statistics'].includes(key))
            .map(([key, value]) => renderSummarySection(key, value))}
        </div>
      )}
    </div>
  );
};

export default DocumentSummarizer; 