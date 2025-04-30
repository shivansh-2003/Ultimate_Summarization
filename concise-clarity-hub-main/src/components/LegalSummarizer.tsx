import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from "@/hooks/use-toast";
import { summarizeLegalDocument } from '@/utils/api';

const LegalSummarizer: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [customQuestion, setCustomQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<null | any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF file for legal document analysis",
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
        description: "Please select a legal document to upload",
        variant: "destructive"
      });
      return;
    }
    
    setIsLoading(true);
    setResult(null);
    
    try {
      const data = await summarizeLegalDocument(file, customQuestion || undefined);
      setResult(data);
      toast({
        title: "Success",
        description: "Legal document successfully analyzed",
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

  return (
    <div className="w-full max-w-3xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Legal Document Analyzer</h2>
        <p className="text-lightGray">
          Upload a legal document (PDF format) for specialized analysis and summarization.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="legal-document">Upload Legal Document</Label>
          <Input
            id="legal-document"
            type="file"
            onChange={handleFileChange}
            accept=".pdf"
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange"
          />
          <p className="text-xs text-lightGray">Supported format: PDF</p>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="custom-question">Custom Question (Optional)</Label>
          <Textarea
            id="custom-question"
            placeholder="Ask a specific question about the legal document..."
            value={customQuestion}
            onChange={(e) => setCustomQuestion(e.target.value)}
            className="bg-darkGray border-muted text-white focus:border-vibrantOrange focus:ring-vibrantOrange min-h-[100px]"
          />
          <p className="text-xs text-lightGray">
            Optionally, you can ask a specific question about the legal document, like "What are the key clauses?" or "Explain the termination terms."
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
            "Analyze Legal Document"
          )}
        </Button>
      </form>
      
      {result && (
        <div className="rounded-md bg-darkGray p-4 border border-muted animate-fade-in">
          <h3 className="text-lg font-medium text-white mb-2 flex items-center">
            <span className="w-1.5 h-1.5 rounded-full bg-vibrantOrange mr-2"></span>
            Analysis Result
          </h3>
          <div className="divider mb-4"></div>
          
          {result.document_type && (
            <div className="mb-4">
              <h4 className="text-md font-medium text-white mb-1">Document Type</h4>
              <p className="text-white">{result.document_type}</p>
            </div>
          )}
          
          {result.summary && (
            <div className="mb-4">
              <h4 className="text-md font-medium text-white mb-1">Summary</h4>
              <div className="text-white whitespace-pre-line">
                {result.summary}
              </div>
            </div>
          )}
          
          {result.processing_time && (
            <div className="text-xs text-lightGray mt-4">
              Processed in {result.processing_time.toFixed(2)} seconds
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default LegalSummarizer; 