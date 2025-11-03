"""
Reddit Data Collector
Collects cryptocurrency mentions and discussions from Reddit
Uses FREE Reddit API (PRAW)
"""

import praw
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import re
import time

load_dotenv()

class RedditCollector:
    """
    Collects and processes cryptocurrency-related posts from Reddit
    """
    
    def __init__(self):
        """Initialize Reddit API client"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent='TruthFi:v1.0.0 (by /u/YourUsername)'
            )
            
            # Test connection
            self.reddit.read_only = True
            
            # Target crypto subreddits
            self.crypto_subreddits = [
                'CryptoCurrency',
                'CryptoMoonShots',
                'SatoshiStreetBets',
                'CryptoMarkets',
                'altcoin',
                'Bitcoin',
                'ethereum'
            ]
            
            print("✓ Reddit API initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Reddit API: {e}")
            print("Make sure your .env file has REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
            raise
    
    def search_token_mentions(self, token_symbol: str, limit: int = 100) -> List[Dict]:
        """
        Search Reddit for mentions of a specific cryptocurrency token
        
        Args:
            token_symbol: The token symbol to search for (e.g., 'BTC', 'ETH')
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing post and comment data
        """
        token_symbol = token_symbol.upper()
        subreddit_string = '+'.join(self.crypto_subreddits)
        subreddit = self.reddit.subreddit(subreddit_string)
        
        posts = []
        search_queries = [
            f"${token_symbol}",
            f"#{token_symbol}",
            token_symbol
        ]
        
        print(f"🔍 Searching for: {token_symbol}")
        
        # Try multiple search approaches
        for query in search_queries:
            try:
                # Search recent posts (past week)
                for submission in subreddit.search(
                    query, 
                    limit=limit // len(search_queries),
                    time_filter='week',
                    sort='new'
                ):
                    # Skip if already processed
                    if any(p['id'] == submission.id for p in posts):
                        continue
                    
                    post_data = self._extract_submission_data(submission)
                    posts.append(post_data)
                    
                    # Get top comments for additional context
                    try:
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list()[:3]:
                            if comment.body and len(comment.body) > 10:
                                comment_data = self._extract_comment_data(comment, submission.id)
                                posts.append(comment_data)
                    except:
                        pass  # Skip if comments fail
                    
                    # Rate limiting
                    time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️  Search error for '{query}': {e}")
                continue
        
        print(f"✓ Found {len(posts)} posts/comments")
        return posts
    
    def get_trending_tokens(self, limit: int = 50) -> List[tuple]:
        """
        Find the most mentioned cryptocurrency tokens across crypto subreddits
        
        Args:
            limit: Number of hot posts to analyze
            
        Returns:
            List of tuples: (token_symbol, mention_count)
        """
        subreddit = self.reddit.subreddit('CryptoCurrency')
        tokens = {}
        
        print(f"📊 Analyzing trending tokens from r/CryptoCurrency...")
        
        try:
            for submission in subreddit.hot(limit=limit):
                # Combine title and body text
                text = f"{submission.title} {submission.selftext}"
                
                # Find token symbols using multiple patterns
                # Pattern 1: $BTC, $ETH style
                dollar_tokens = re.findall(r'\$([A-Z]{2,10})\b', text)
                
                # Pattern 2: Standalone capitals (be selective)
                word_tokens = re.findall(r'\b([A-Z]{3,10})\b', text)
                
                all_tokens = dollar_tokens + word_tokens
                
                for token in all_tokens:
                    # Filter out common words
                    if token not in self._get_excluded_words():
                        tokens[token] = tokens.get(token, 0) + 1
            
            # Sort by frequency
            sorted_tokens = sorted(tokens.items(), key=lambda x: x[1], reverse=True)
            
            print(f"✓ Found {len(sorted_tokens)} unique tokens")
            return sorted_tokens[:20]  # Return top 20
            
        except Exception as e:
            print(f"❌ Error getting trending tokens: {e}")
            return []
    
    def get_subreddit_sentiment(self, token_symbol: str) -> Dict:
        """
        Calculate overall sentiment for a token based on Reddit activity
        
        Args:
            token_symbol: The token to analyze
            
        Returns:
            Dictionary with sentiment metrics
        """
        posts = self.search_token_mentions(token_symbol, limit=30)
        
        if not posts:
            return {
                'sentiment': 'neutral',
                'avg_score': 0,
                'post_count': 0,
                'total_upvotes': 0
            }
        
        # Calculate average score
        scores = [p.get('score', 0) for p in posts if p.get('type') == 'post']
        total_score = sum(scores)
        avg_score = total_score / len(scores) if scores else 0
        
        # Determine sentiment
        if avg_score > 15:
            sentiment = 'positive'
        elif avg_score > 5:
            sentiment = 'moderately_positive'
        elif avg_score > -5:
            sentiment = 'neutral'
        elif avg_score > -15:
            sentiment = 'moderately_negative'
        else:
            sentiment = 'negative'
        
        return {
            'sentiment': sentiment,
            'avg_score': round(avg_score, 2),
            'post_count': len(posts),
            'total_upvotes': total_score
        }
    
    def monitor_new_posts(self, callback_func, token_filter: Optional[str] = None):
        """
        Real-time monitoring of new posts in crypto subreddits
        
        Args:
            callback_func: Function to call with each new post
            token_filter: Optional token symbol to filter for
        """
        subreddit_string = '+'.join(self.crypto_subreddits)
        subreddit = self.reddit.subreddit(subreddit_string)
        
        print(f"👀 Monitoring {subreddit_string} for new posts...")
        
        try:
            for submission in subreddit.stream.submissions(skip_existing=True):
                post_data = self._extract_submission_data(submission)
                
                # Apply filter if specified
                if token_filter:
                    text_to_check = f"{post_data['title']} {post_data['text']}".upper()
                    if token_filter.upper() not in text_to_check:
                        continue
                
                callback_func(post_data)
                
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
    
    def get_post_by_id(self, post_id: str) -> Dict:
        """
        Fetch a specific Reddit post by ID
        
        Args:
            post_id: Reddit post ID
            
        Returns:
            Post data dictionary
        """
        try:
            submission = self.reddit.submission(id=post_id)
            return self._extract_submission_data(submission)
        except Exception as e:
            print(f"❌ Error fetching post {post_id}: {e}")
            return {}
    
    def _extract_submission_data(self, submission) -> Dict:
        """
        Extract relevant data from a Reddit submission
        
        Args:
            submission: PRAW Submission object
            
        Returns:
            Dictionary with cleaned post data
        """
        try:
            return {
                'id': submission.id,
                'type': 'post',
                'title': submission.title,
                'text': submission.selftext if submission.selftext else '',
                'author': str(submission.author) if submission.author else '[deleted]',
                'subreddit': str(submission.subreddit),
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'created_utc': datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                'url': submission.url,
                'is_self': submission.is_self,
                'awards': submission.total_awards_received,
                'distinguished': submission.distinguished,
                'stickied': submission.stickied,
                'over_18': submission.over_18,
                'spoiler': submission.spoiler,
                'link_flair_text': submission.link_flair_text
            }
        except Exception as e:
            print(f"⚠️  Error extracting submission data: {e}")
            return {}
    
    def _extract_comment_data(self, comment, parent_id: str) -> Dict:
        """
        Extract relevant data from a Reddit comment
        
        Args:
            comment: PRAW Comment object
            parent_id: ID of parent submission
            
        Returns:
            Dictionary with cleaned comment data
        """
        try:
            return {
                'id': comment.id,
                'type': 'comment',
                'text': comment.body,
                'title': '',  # Comments don't have titles
                'author': str(comment.author) if comment.author else '[deleted]',
                'subreddit': str(comment.subreddit),
                'score': comment.score,
                'created_utc': datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
                'parent_id': parent_id,
                'is_comment': True,
                'distinguished': comment.distinguished,
                'stickied': comment.stickied,
                'is_submitter': comment.is_submitter,
                'awards': comment.total_awards_received
            }
        except Exception as e:
            print(f"⚠️  Error extracting comment data: {e}")
            return {}
    
    def _get_excluded_words(self) -> set:
        """
        Get list of common words to exclude from token detection
        
        Returns:
            Set of words to exclude
        """
        return {
            'THE', 'AND', 'FOR', 'NOT', 'BUT', 'ARE', 'YOU', 'ALL',
            'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET',
            'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD',
            'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET',
            'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'WILL', 'ABOUT', 'BEEN',
            'HAVE', 'INTO', 'LIKE', 'MORE', 'SOME', 'THAN', 'THAT',
            'THEM', 'THEN', 'THESE', 'THIS', 'WHAT', 'WHEN', 'WHERE',
            'WHICH', 'WITH', 'YOUR', 'WOULD', 'COULD', 'SHOULD', 'CRYPTO',
            'COIN', 'TOKEN', 'PRICE', 'REDDIT', 'POST', 'COMMENT'
        }


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Reddit Collector")
    print("="*60 + "\n")
    
    try:
        collector = RedditCollector()
        
        # Test 1: Search for Bitcoin
        print("\n📝 Test 1: Searching for BTC mentions...")
        btc_posts = collector.search_token_mentions('BTC', limit=10)
        print(f"✓ Found {len(btc_posts)} posts/comments")
        if btc_posts:
            print(f"Sample: {btc_posts[0]['title'][:50]}...")
        
        # Test 2: Get trending tokens
        print("\n📝 Test 2: Getting trending tokens...")
        trending = collector.get_trending_tokens(limit=20)
        print("✓ Top 10 trending tokens:")
        for i, (token, count) in enumerate(trending[:10], 1):
            print(f"  {i}. ${token}: {count} mentions")
        
        # Test 3: Sentiment analysis
        print("\n📝 Test 3: BTC sentiment analysis...")
        sentiment = collector.get_subreddit_sentiment('BTC')
        print(f"✓ Sentiment: {sentiment['sentiment']}")
        print(f"  Avg Score: {sentiment['avg_score']}")
        print(f"  Posts Analyzed: {sentiment['post_count']}")
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")