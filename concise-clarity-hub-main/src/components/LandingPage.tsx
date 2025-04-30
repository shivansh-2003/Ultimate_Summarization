import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, User, Mic, Play, Video, Globe } from 'lucide-react';
import { Button } from '@/components/ui/button';

const LandingPage: React.FC = () => {
  return (
    <div className="bg-jetBlack min-h-screen">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 w-full bg-jetBlack bg-opacity-95 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="text-xl font-bold">
              <span className="text-white">Ultimate</span>{" "}
              <span className="text-vibrantOrange">Summarizer</span>
            </Link>
            
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-white hover:text-vibrantOrange transition-colors">Features</a>
            </div>
            
            <Link to="/app/document">
              <Button className="bg-vibrantOrange hover:bg-opacity-90 text-white orange-glow">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>
      
      {/* Hero Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="md:w-1/2 space-y-6">
              <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight animate-enter">
                Transform Content <br />
                into <span className="text-vibrantOrange">Clarity</span>
              </h1>
              <p className="text-xl text-lightGray">
                Instantly summarize documents, websites, videos, and more with our advanced AI summarization technology.
              </p>
              <div className="pt-4">
                <Link to="/app/website">
                  <Button size="lg" className="bg-vibrantOrange hover:bg-opacity-90 text-white orange-glow text-lg px-8">
                    Try Now
                  </Button>
                </Link>
              </div>
            </div>
            
            <div className="md:w-1/2 relative">
              <div className="relative bg-darkGray p-6 rounded-lg border border-muted shadow-xl">
                <div className="absolute -top-2 -left-2 w-24 h-24 bg-vibrantOrange opacity-10 rounded-full blur-xl"></div>
                <div className="absolute -bottom-5 -right-5 w-32 h-32 bg-vibrantOrange opacity-10 rounded-full blur-xl"></div>
                
                <div className="relative z-10 space-y-4">
                  <div className="flex items-center gap-2 text-white">
                    <div className="w-3 h-3 rounded-full bg-vibrantOrange"></div>
                    <div className="w-3 h-3 rounded-full bg-gray-500"></div>
                    <div className="w-3 h-3 rounded-full bg-gray-500"></div>
                  </div>
                  
                  <div className="h-12 bg-jetBlack rounded flex items-center px-3">
                    <div className="w-full bg-transparent text-lightGray text-sm">https://example.com/long-article</div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="h-3 bg-jetBlack rounded w-full"></div>
                    <div className="h-3 bg-jetBlack rounded w-5/6"></div>
                    <div className="h-3 bg-jetBlack rounded w-4/6"></div>
                  </div>
                  
                  <div className="border-t border-muted pt-4 mt-6">
                    <div className="text-white font-medium mb-2">Summary:</div>
                    <div className="space-y-2">
                      <div className="h-3 bg-vibrantOrange bg-opacity-20 rounded w-full"></div>
                      <div className="h-3 bg-vibrantOrange bg-opacity-20 rounded w-5/6"></div>
                      <div className="h-3 bg-vibrantOrange bg-opacity-20 rounded w-4/6"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section id="features" className="py-16 bg-darkGray">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Powerful Summarization <span className="text-vibrantOrange">Features</span>
            </h2>
            <p className="text-lightGray max-w-2xl mx-auto">
              Our platform provides multiple ways to extract insights from various content formats.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: FileText, title: "Document Summarization", description: "Quickly summarize PDFs, Word docs, and text files" },
              { icon: FileText, title: "Legal Document Analysis", description: "Extract key clauses and simplify legal jargon" },
              { icon: User, title: "Resume Analysis", description: "Identify key qualifications and experience from CVs" },
              { icon: Mic, title: "Audio Summarization", description: "Convert and summarize audio recordings and podcasts" },
              { icon: Play, title: "YouTube Video Summaries", description: "Get key points from any YouTube video" },
              { icon: Video, title: "Video Summarization", description: "Extract insights from uploaded video content" },
              { icon: Globe, title: "Website Summarization", description: "Summarize any webpage with a single URL" },
            ].map((feature, i) => (
              <div 
                key={i} 
                className="bg-jetBlack p-6 rounded-lg border border-muted hover:border-vibrantOrange transition-colors hover-scale"
              >
                <div className="w-12 h-12 bg-vibrantOrange bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-vibrantOrange" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-lightGray">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* How It Works */}
      <section id="how-it-works" className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              How It <span className="text-vibrantOrange">Works</span>
            </h2>
            <p className="text-lightGray max-w-2xl mx-auto">
              Our summarization process is simple, fast, and highly effective.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { number: "01", title: "Upload or Link", description: "Input your content by uploading a file, pasting a URL, or linking media" },
              { number: "02", title: "Process Content", description: "Our AI analyzes the content to identify key points and main ideas" },
              { number: "03", title: "Get Summary", description: "Receive a clear, concise summary that captures the essence of the content" }
            ].map((step, i) => (
              <div key={i} className="relative">
                <div className="text-4xl font-bold text-vibrantOrange opacity-30 mb-4">{step.number}</div>
                <h3 className="text-xl font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-lightGray">{step.description}</p>
                
                {i < 2 && (
                  <div className="hidden md:block absolute top-6 right-0 w-24 h-px bg-vibrantOrange opacity-30"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Call to Action */}
      <section className="py-16 bg-gradient-to-b from-jetBlack to-darkGray">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Save Time and Gain Clarity?
          </h2>
          <p className="text-lightGray max-w-2xl mx-auto mb-8">
            Join thousands of professionals who are already using our summarization tools to work smarter.
          </p>
          <Link to="/app/website">
            <Button size="lg" className="bg-vibrantOrange hover:bg-opacity-90 text-white orange-glow text-lg px-8">
              Start Summarizing Now
            </Button>
          </Link>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-8 bg-jetBlack border-t border-muted">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-lg font-semibold mb-4 md:mb-0">
              <span className="text-white">Ultimate</span>{" "}
              <span className="text-vibrantOrange">Summarizer</span>
            </div>
            <div className="text-sm text-lightGray">
              © {new Date().getFullYear()} Ultimate Summarizer. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
