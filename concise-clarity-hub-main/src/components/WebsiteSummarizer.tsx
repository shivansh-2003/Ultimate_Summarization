
import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { toast } from "@/hooks/use-toast";
import { summarizeWebsite } from '@/utils/api';

const WebsiteSummarizer: React.FC = () => {
  const [url, setUrl] = useState('');
  const [length, setLength] = useState('medium');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<null | string>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url) {
      toast({
        title: "Error",
        description: "Please enter a website URL",
        variant: "destructive"
      });
      return;
    }
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await summarizeWebsite(url, length);
      setResult(data.summary);
      toast({
        title: "Success",
        description: "Website successfully summarized",
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
        <h2 className="text-2xl font-bold text-white mb-2">Website Summarizer</h2>
        <p className="text-lightGray">
          Paste any website URL below to generate a concise summary of its content.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="url">Website URL</Label>
          <Input
            id="url"
            type="url"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">Include http:// or https:// in the URL</p>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="length">Summary Length</Label>
          <Select value={length} onValueChange={setLength}>
            <SelectTrigger id="length" className="bg-darkGray border-muted text-white focus:border-vibrantOrange">
              <SelectValue placeholder="Select length" />
            </SelectTrigger>
            <SelectContent className="bg-darkGray text-white border-muted">
              <SelectItem value="short">Short</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="long">Long</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-lightGray">Choose how detailed you want your summary to be</p>
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
            "Summarize Website"
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

export default WebsiteSummarizer;
