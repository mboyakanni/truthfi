/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react/no-unescaped-entities */
'use client';

import { useState, useEffect } from 'react';
import { Search, AlertCircle, CheckCircle, AlertTriangle, TrendingUp, Shield, BarChart3, RefreshCw, ExternalLink } from 'lucide-react';

interface AnalysisResult {
  score: number;
  risk_level: string;
  red_flags: string[];
  analyzed_posts: number;
  metrics: {
    content_scam_score: number;
    account_credibility: number;
    coordination_risk: number;
    engagement_quality: number;
    sentiment: string;
  };
  breakdown: {
    high_risk_posts: number;
    suspicious_accounts: number;
    coordinated: boolean;
    low_quality_engagement: number;
  };
  recommendation: {
    recommendation: string;
    message: string;
    actions: string[];
  };
  sources: {
    reddit: number;
    telegram: number;
    twitter: number;
  };
}

interface TrendingToken {
  symbol: string;
  mentions: number;
}

export default function TruthFiDashboard() {
  const [tokenSymbol, setTokenSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState('');
  const [trending, setTrending] = useState<TrendingToken[]>([]);
  const [showTrending, setShowTrending] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [loadingStatus, setLoadingStatus] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    // Load recent searches from localStorage
    try {
      const saved = localStorage.getItem('truthfi_recent_searches');
      if (saved) {
        setRecentSearches(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Failed to load recent searches:', error);
    }
  }, []);

  const saveRecentSearch = (token: string) => {
    try {
      const updated = [token, ...recentSearches.filter(t => t !== token)].slice(0, 5);
      setRecentSearches(updated);
      localStorage.setItem('truthfi_recent_searches', JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to save recent search:', error);
    }
  };

  const analyzeToken = async () => {
    if (!tokenSymbol.trim()) {
      setError('Please enter a token symbol');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setLoadingStatus('🔍 Searching Reddit posts...');

    // Update status messages
    const statusTimer1 = setTimeout(() => {
      setLoadingStatus('📊 Analyzing content patterns...');
    }, 3000);
    
    const statusTimer2 = setTimeout(() => {
      setLoadingStatus('🧮 Calculating Truth Score...');
    }, 6000);
    
    const statusTimer3 = setTimeout(() => {
      setLoadingStatus('⚡ Almost done...');
    }, 9000);

    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          token_symbol: tokenSymbol.toUpperCase(),
          post_limit: 50  // Reduced from 100 for faster analysis
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
      saveRecentSearch(tokenSymbol.toUpperCase());
    } catch (err: any) {
      setError(err.message || 'Failed to analyze token. Make sure the backend is running.');
    } finally {
      clearTimeout(statusTimer1);
      clearTimeout(statusTimer2);
      clearTimeout(statusTimer3);
      setLoading(false);
      setLoadingStatus('');
    }
  };

  const loadTrending = async () => {
    try {
      const response = await fetch(`${API_URL}/api/trending`);
      const data = await response.json();
      setTrending(data.trending.slice(0, 10));
      setShowTrending(true);
    } catch (err) {
      console.error('Failed to load trending tokens');
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskBgColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-50 border-green-200';
      case 'medium': return 'bg-yellow-50 border-yellow-200';
      case 'high': return 'bg-orange-50 border-orange-200';
      case 'critical': return 'bg-red-50 border-red-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'low': return <CheckCircle className="w-8 h-8" />;
      case 'medium': return <AlertTriangle className="w-8 h-8" />;
      default: return <AlertCircle className="w-8 h-8" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return '#10b981';
    if (score >= 55) return '#f59e0b';
    if (score >= 35) return '#f97316';
    return '#ef4444';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="w-12 h-12 md:w-16 md:h-16 text-purple-400" />
            <h1 className="text-4xl md:text-6xl font-bold text-white">
              Truth<span className="text-purple-400">Fi</span>
            </h1>
          </div>
          <p className="text-lg md:text-xl text-gray-300 mb-2">
            AI-Powered Crypto Scam Detection
          </p>
          <p className="text-sm text-gray-400">
            Protecting traders from misinformation and manipulation
          </p>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-2xl shadow-2xl p-6 md:p-8 mb-6">
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <input
              type="text"
              placeholder="Enter token symbol (e.g., BTC, ETH, DOGE)"
              value={tokenSymbol}
              onChange={(e) => setTokenSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && analyzeToken()}
              className="flex-1 px-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:outline-none focus:border-purple-500 transition uppercase"
            />
            <button
              onClick={analyzeToken}
              disabled={loading || !tokenSymbol.trim()}
              className="px-8 py-4 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Analyze
                </>
              )}
            </button>
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            <button
              onClick={loadTrending}
              className="text-purple-600 hover:text-purple-700 font-medium text-sm flex items-center gap-2"
            >
              <TrendingUp className="w-4 h-4" />
              View Trending
            </button>
            
            {recentSearches.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-gray-500 text-sm">Recent:</span>
                {recentSearches.map((token) => (
                  <button
                    key={token}
                    onClick={() => {
                      setTokenSymbol(token);
                      setError('');
                    }}
                    className="px-3 py-1 bg-purple-100 text-purple-700 rounded-lg text-sm hover:bg-purple-200 transition"
                  >
                    ${token}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          {error && (
            <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded">
              <p className="text-red-700 text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                {error}
              </p>
            </div>
          )}
        </div>

        {/* Trending Tokens */}
        {showTrending && trending.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-6 animate-in slide-in-from-top">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                Trending on Reddit
              </h3>
              <button
                onClick={() => setShowTrending(false)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >
                ✕
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {trending.map((token) => (
                <button
                  key={token.symbol}
                  onClick={() => {
                    setTokenSymbol(token.symbol);
                    setShowTrending(false);
                    setError('');
                  }}
                  className="p-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition text-left group"
                >
                  <div className="font-bold text-purple-900 group-hover:text-purple-700">
                    ${token.symbol}
                  </div>
                  <div className="text-xs text-gray-600">{token.mentions} mentions</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center animate-in fade-in">
            <RefreshCw className="w-16 h-16 text-purple-600 animate-spin mx-auto mb-6" />
            <h3 className="text-2xl font-semibold text-gray-900 mb-3">
              Analyzing ${tokenSymbol}
            </h3>
            <p className="text-gray-600 text-lg mb-6">
              {loadingStatus}
            </p>
            
            {/* Progress Bar */}
            <div className="max-w-md mx-auto">
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-purple-600 to-purple-400 h-3 rounded-full transition-all duration-1000 ease-out animate-pulse"
                  style={{
                    width: loadingStatus.includes('Searching') ? '33%' :
                           loadingStatus.includes('Analyzing') ? '66%' :
                           loadingStatus.includes('Calculating') ? '85%' : '95%'
                  }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-3">
                This may take 10-15 seconds...
              </p>
            </div>

            {/* Fun Facts While Waiting */}
            <div className="mt-8 p-4 bg-purple-50 rounded-lg max-w-md mx-auto">
              <p className="text-sm text-purple-900">
                💡 <strong>Did you know?</strong> We're analyzing dozens of Reddit posts,
                checking for scam patterns, and calculating credibility scores in real-time!
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-6 animate-in fade-in">
            {/* Truth Score Card */}
            <div className={`rounded-2xl shadow-xl p-6 md:p-8 border-2 ${getRiskBgColor(result.risk_level)}`}>
              <div className="flex flex-col md:flex-row items-center gap-6 md:gap-8">
                {/* Score Circle */}
                <div className="relative flex-shrink-0">
                  <svg className="transform -rotate-90 w-40 h-40">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="#e5e7eb"
                      strokeWidth="12"
                      fill="none"
                    />
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke={getScoreColor(result.score)}
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={`${result.score * 4.4} 440`}
                      strokeLinecap="round"
                      className="transition-all duration-1000"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-5xl font-bold text-gray-900">
                        {Math.round(result.score)}
                      </div>
                      <div className="text-sm text-gray-600">Truth Score</div>
                    </div>
                  </div>
                </div>

                {/* Risk Info */}
                <div className="flex-1 text-center md:text-left">
                  <div className={`inline-flex items-center gap-3 mb-3 ${getRiskColor(result.risk_level)}`}>
                    {getRiskIcon(result.risk_level)}
                    <span className="text-2xl md:text-3xl font-bold uppercase">
                      {result.risk_level} Risk
                    </span>
                  </div>
                  <p className="text-gray-700 text-base md:text-lg mb-4">
                    {result.recommendation.message}
                  </p>
                  <div className="flex flex-wrap gap-3 justify-center md:justify-start">
                    <div className="inline-block px-4 py-2 bg-white rounded-lg shadow-sm">
                      <span className="text-sm text-gray-600">Analyzed: </span>
                      <span className="font-bold">{result.analyzed_posts} posts</span>
                    </div>
                    <div className="inline-block px-4 py-2 bg-white rounded-lg shadow-sm">
                      <span className="text-sm text-gray-600">Source: </span>
                      <span className="font-bold">Reddit</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition">
                <div className="text-gray-600 text-sm mb-1">Scam Indicators</div>
                <div className="text-3xl font-bold text-red-600">
                  {Math.round(result.metrics.content_scam_score)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-red-600 h-2 rounded-full transition-all duration-1000"
                    style={{width: `${result.metrics.content_scam_score}%`}}
                  />
                </div>
              </div>
              
              <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition">
                <div className="text-gray-600 text-sm mb-1">Account Trust</div>
                <div className="text-3xl font-bold text-green-600">
                  {Math.round(result.metrics.account_credibility)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full transition-all duration-1000"
                    style={{width: `${result.metrics.account_credibility}%`}}
                  />
                </div>
              </div>
              
              <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition">
                <div className="text-gray-600 text-sm mb-1">Coordination Risk</div>
                <div className="text-3xl font-bold text-orange-600">
                  {Math.round(result.metrics.coordination_risk)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-orange-600 h-2 rounded-full transition-all duration-1000"
                    style={{width: `${result.metrics.coordination_risk}%`}}
                  />
                </div>
              </div>
              
              <div className="bg-white rounded-xl p-5 shadow-lg hover:shadow-xl transition">
                <div className="text-gray-600 text-sm mb-1">Sentiment</div>
                <div className="text-xl font-bold text-purple-600 capitalize">
                  {result.metrics.sentiment.replace('_', ' ')}
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  Quality: {Math.round(result.metrics.engagement_quality)}%
                </div>
              </div>
            </div>

            {/* Red Flags */}
            {result.red_flags.length > 0 && (
              <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8">
                <h3 className="text-2xl font-bold mb-4 flex items-center gap-2 text-red-600">
                  <AlertCircle className="w-6 h-6" />
                  Red Flags Detected ({result.red_flags.length})
                </h3>
                <div className="space-y-2">
                  {result.red_flags.map((flag, idx) => (
                    <div 
                      key={idx} 
                      className="flex items-start gap-3 p-3 bg-red-50 rounded-lg hover:bg-red-100 transition"
                    >
                      <span className="text-red-600 font-bold text-xl flex-shrink-0">•</span>
                      <span className="text-gray-700">{flag}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-800 rounded-2xl shadow-xl p-6 md:p-8 text-white">
              <h3 className="text-2xl md:text-3xl font-bold mb-3">
                {result.recommendation.recommendation}
              </h3>
              <p className="text-purple-100 mb-6 text-base md:text-lg">
                {result.recommendation.message}
              </p>
              <div className="space-y-3">
                <h4 className="font-semibold text-purple-200 text-lg">Recommended Actions:</h4>
                {result.recommendation.actions.map((action, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-start gap-3 bg-purple-700 bg-opacity-50 p-3 md:p-4 rounded-lg hover:bg-opacity-70 transition"
                  >
                    <span className="text-purple-300 font-bold flex-shrink-0">→</span>
                    <span className="text-sm md:text-base">{action}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Breakdown */}
            <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                Detailed Analysis Breakdown
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <div className="text-4xl font-bold text-red-600 mb-1">
                    {result.breakdown.high_risk_posts}
                  </div>
                  <div className="text-sm text-gray-600">High Risk Posts</div>
                </div>
                
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-4xl font-bold text-orange-600 mb-1">
                    {result.breakdown.suspicious_accounts}
                  </div>
                  <div className="text-sm text-gray-600">Suspicious Accounts</div>
                </div>
                
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-4xl font-bold text-purple-600 mb-1">
                    {result.breakdown.coordinated ? 'YES' : 'NO'}
                  </div>
                  <div className="text-sm text-gray-600">Coordinated Activity</div>
                </div>
                
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-4xl font-bold text-yellow-600 mb-1">
                    {result.breakdown.low_quality_engagement}
                  </div>
                  <div className="text-sm text-gray-600">Low Quality Posts</div>
                </div>
              </div>
            </div>

            {/* Share Button */}
            <div className="text-center">
              <button 
                onClick={() => analyzeToken()}
                className="px-6 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition flex items-center gap-2 mx-auto"
              >
                <RefreshCw className="w-5 h-5" />
                Re-analyze ${tokenSymbol}
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-400 text-sm space-y-2">
          <p className="flex items-center justify-center gap-2">
            <Shield className="w-4 h-4" />
            TruthFi MVP • Free Edition • Data from Reddit
          </p>
          <p>Always do your own research. Not financial advice.</p>
          <p className="text-xs">
            Made with ❤️ for the crypto community
          </p>
        </div>
      </div>
    </div>
  );
}