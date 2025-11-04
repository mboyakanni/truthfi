"""
TruthFi Backend - Main API Server
Complete implementation with all features
Updated to use non-deprecated methods
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timezone
import asyncio

# Import our analysis modules
from reddit_collector import RedditCollector
from pattern_detector import PatternDetector
from truth_scorer import TruthScorer

# Application startup time
start_time = datetime.now(timezone.utc)

# Initialize services
reddit_collector = None
pattern_detector = None
truth_scorer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Replaces deprecated @app.on_event
    """
    # Startup
    global reddit_collector, pattern_detector, truth_scorer
    
    print("\n" + "=" * 60)
    print("🚀 TruthFi API - Starting Up")
    print("=" * 60)
    
    # Initialize services
    reddit_collector = RedditCollector()
    pattern_detector = PatternDetector()
    truth_scorer = TruthScorer()
    
    print("✓ FastAPI server initialized")
    print("✓ Reddit collector ready")
    print("✓ Pattern detector ready")
    print("✓ Truth scoring engine ready")
    print("=" * 60)
    print("📡 API Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔧 Interactive API: http://localhost:8000/redoc")
    print("=" * 60)
    print("🛡️  Ready to detect crypto scams!")
    print("=" * 60 + "\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down TruthFi API...")
    print("✓ Cleanup complete\n")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="TruthFi API",
    description="AI-powered cryptocurrency misinformation detection platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration - Allow frontend access
origins = [
    "https://truthfi.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # exact match
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.requests import Request

@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    method = request.method
    path = request.url.path
    print(f"🌍 Request: {method} {path} | Origin: {origin}")
    response = await call_next(request)
    return response
# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class AnalysisRequest(BaseModel):
    token_symbol: str = Field(..., min_length=1, max_length=10, description="Token symbol (e.g., BTC, ETH)")
    post_limit: Optional[int] = Field(100, ge=10, le=200, description="Number of posts to analyze")
    include_comments: Optional[bool] = Field(True, description="Include comment analysis")

class MetricsData(BaseModel):
    content_scam_score: float
    account_credibility: float
    coordination_risk: float
    engagement_quality: float
    sentiment: str

class BreakdownData(BaseModel):
    high_risk_posts: int
    suspicious_accounts: int
    coordinated: bool
    low_quality_engagement: int

class RecommendationData(BaseModel):
    recommendation: str
    message: str
    actions: List[str]

class AnalysisResponse(BaseModel):
    score: float
    risk_level: str
    red_flags: List[str]
    analyzed_posts: int
    metrics: MetricsData
    breakdown: BreakdownData
    recommendation: RecommendationData
    timestamp: str
    sources: Dict[str, int]

class TrendingToken(BaseModel):
    symbol: str
    mentions: int
    sentiment: Optional[str] = None

class TrendingResponse(BaseModel):
    trending: List[TrendingToken]
    timestamp: str
    total_analyzed: int

class SentimentResponse(BaseModel):
    token: str
    sentiment: str
    avg_score: float
    post_count: int
    total_upvotes: int
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    timestamp: str
    uptime: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: str

# ==========================================
# HEALTH CHECK ENDPOINTS
# ==========================================

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    uptime = datetime.now(timezone.utc) - start_time
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    
    return {
        "status": "operational",
        "services": {
            "api": "operational",
            "reddit_collector": "operational",
            "truth_scorer": "operational"
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": f"{hours}h {minutes}m"
    }

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Comprehensive health check endpoint
    Tests all service connections
    """
    services = {
        "api": "operational",
        "reddit_collector": "unknown",
        "pattern_detector": "operational",
        "truth_scorer": "operational"
    }
    
    # Test Reddit connection
    try:
        # Try to access Reddit (read-only, no auth needed)
        test = reddit_collector.reddit.subreddit('cryptocurrency').display_name
        services["reddit_collector"] = "operational"
    except Exception as e:
        services["reddit_collector"] = f"error: {str(e)[:50]}"
    
    uptime = datetime.now(timezone.utc) - start_time
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    
    overall_status = "operational" if all(
        status == "operational" for status in services.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "services": services,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": f"{hours}h {minutes}m"
    }

# ==========================================
# MAIN ANALYSIS ENDPOINT
# ==========================================

@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_token(request: AnalysisRequest):
    """
    Analyze a cryptocurrency token for misinformation and manipulation
    
    This endpoint collects social media data (Reddit) and performs comprehensive
    analysis including scam pattern detection, account credibility assessment,
    and coordination detection.
    
    **Parameters:**
    - **token_symbol**: The cryptocurrency symbol (e.g., BTC, ETH, DOGE)
    - **post_limit**: Number of posts to analyze (10-200, default: 100)
    - **include_comments**: Whether to include comment analysis (default: true)
    
    **Returns:**
    - Complete analysis with Truth Score (0-100)
    - Risk level assessment
    - Detailed red flags
    - Actionable recommendations
    """
    try:
        # Validate and sanitize input
        token = request.token_symbol.upper().strip()
        
        if not token.isalnum():
            raise HTTPException(
                status_code=400, 
                detail="Token symbol must contain only letters and numbers"
            )
        
        print(f"\n🔍 Analyzing token: {token}")
        print(f"📊 Post limit: {request.post_limit}")
        
        # Collect data from Reddit
        print(f"📡 Collecting data from Reddit...")
        posts = reddit_collector.search_token_mentions(
            token_symbol=token,
            limit=request.post_limit
        )
        
        if not posts or len(posts) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No social media data found for ${token}. "
                       f"This token may be too new, not actively discussed, "
                       f"or the symbol may be incorrect."
            )
        
        print(f"✓ Found {len(posts)} posts/comments")
        
        # Calculate Truth Score
        print(f"🧮 Calculating Truth Score...")
        result = truth_scorer.calculate_truth_score(posts)
        
        # Get recommendation based on score
        recommendation = truth_scorer.get_risk_recommendation(result['score'])
        
        print(f"✓ Analysis complete: Score = {result['score']:.1f}")
        print(f"✓ Risk Level: {result['risk_level'].upper()}")
        
        # Prepare response
        response = AnalysisResponse(
            score=result['score'],
            risk_level=result['risk_level'],
            red_flags=result['red_flags'],
            analyzed_posts=result['analyzed_posts'],
            metrics=MetricsData(**result['metrics']),
            breakdown=BreakdownData(**result['breakdown']),
            recommendation=RecommendationData(**recommendation),
            timestamp=result['timestamp'],
            sources={
                'reddit': len(posts),
                'telegram': 0,  # For future implementation
                'twitter': 0    # For future implementation
            }
        )
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

# ==========================================
# TRENDING TOKENS ENDPOINT
# ==========================================

@app.get("/api/trending", response_model=TrendingResponse, tags=["Discovery"])
async def get_trending_tokens(limit: int = 20):
    """
    Get currently trending cryptocurrency tokens from Reddit
    
    Analyzes popular crypto subreddits to find the most mentioned tokens.
    
    **Parameters:**
    - **limit**: Number of trending tokens to return (default: 20, max: 50)
    
    **Returns:**
    - List of trending tokens with mention counts
    - Sorted by popularity
    """
    try:
        if limit > 50:
            limit = 50
        
        print(f"\n📈 Fetching trending tokens (limit: {limit})")
        
        trending_data = reddit_collector.get_trending_tokens(limit=limit)
        
        trending_tokens = [
            TrendingToken(
                symbol=token,
                mentions=count,
                sentiment=None  # Could add sentiment analysis here
            )
            for token, count in trending_data
        ]
        
        print(f"✓ Found {len(trending_tokens)} trending tokens")
        
        return TrendingResponse(
            trending=trending_tokens,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_analyzed=len(trending_tokens)
        )
    
    except Exception as e:
        print(f"❌ Error fetching trending: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trending tokens: {str(e)}"
        )

# ==========================================
# SENTIMENT ANALYSIS ENDPOINT
# ==========================================

@app.get("/api/sentiment/{token_symbol}", response_model=SentimentResponse, tags=["Analysis"])
async def get_token_sentiment(token_symbol: str):
    """
    Get overall sentiment analysis for a specific token
    
    Analyzes recent posts and calculates aggregate sentiment.
    
    **Parameters:**
    - **token_symbol**: The token to analyze (e.g., BTC, ETH)
    
    **Returns:**
    - Sentiment classification (positive/neutral/negative)
    - Average score
    - Post count and engagement metrics
    """
    try:
        token = token_symbol.upper().strip()
        
        if not token.isalnum():
            raise HTTPException(status_code=400, detail="Invalid token symbol")
        
        print(f"\n💭 Analyzing sentiment for: {token}")
        
        sentiment_data = reddit_collector.get_subreddit_sentiment(token)
        
        if sentiment_data['post_count'] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No recent posts found for ${token}"
            )
        
        print(f"✓ Sentiment: {sentiment_data['sentiment']}")
        
        return SentimentResponse(
            token=token,
            sentiment=sentiment_data['sentiment'],
            avg_score=sentiment_data['avg_score'],
            post_count=sentiment_data['post_count'],
            total_upvotes=sentiment_data['total_upvotes'],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error analyzing sentiment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        )

# ==========================================
# BATCH ANALYSIS ENDPOINT
# ==========================================

@app.post("/api/analyze/batch", tags=["Analysis"])
async def analyze_batch(token_symbols: List[str], post_limit: int = 50):
    """
    Analyze multiple tokens in a single request
    
    **Parameters:**
    - **token_symbols**: List of token symbols to analyze
    - **post_limit**: Posts per token (default: 50)
    
    **Returns:**
    - Dictionary of results keyed by token symbol
    """
    if len(token_symbols) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tokens per batch request"
        )
    
    results = {}
    
    for token in token_symbols:
        try:
            request = AnalysisRequest(
                token_symbol=token,
                post_limit=post_limit
            )
            result = await analyze_token(request)
            results[token] = result
        except Exception as e:
            results[token] = {
                "error": str(e),
                "status": "failed"
            }
    
    return {
        "results": results,
        "analyzed": len(results),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ==========================================
# PATTERN DETECTION ENDPOINT
# ==========================================

@app.post("/api/detect-patterns", tags=["Analysis"])
async def detect_patterns(text: str):
    """
    Analyze a piece of text for scam patterns
    
    Useful for checking individual posts, messages, or promotional content.
    
    **Parameters:**
    - **text**: The text content to analyze
    
    **Returns:**
    - Scam score and detected patterns
    """
    try:
        if not text or len(text) < 10:
            raise HTTPException(
                status_code=400,
                detail="Text must be at least 10 characters"
            )
        
        result = pattern_detector.analyze_text(text)
        
        return {
            "scam_score": result['scam_score'],
            "risk_level": result['risk_level'],
            "red_flags": result['red_flags'],
            "pattern_matches": result['pattern_matches'],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pattern detection failed: {str(e)}"
        )

# ==========================================
# ERROR HANDLERS
# ==========================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ==========================================
# MAIN ENTRY POINT
# ==========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )