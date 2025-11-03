"""
Truth Score Calculator
Combines multiple analysis signals to generate a comprehensive Truth Score
"""

from typing import List, Dict
from datetime import datetime, timezone, timedelta
from pattern_detector import PatternDetector
import statistics

class TruthScorer:
    """
    Calculates comprehensive Truth Scores for cryptocurrency tokens
    Combines content analysis, account credibility, and coordination detection
    """
    
    def __init__(self):
        """Initialize the truth scorer with pattern detector"""
        self.pattern_detector = PatternDetector()
        
        # Scoring component weights
        self.weights = {
            'content_analysis': 0.40,      # 40% - What is being said
            'account_credibility': 0.30,   # 30% - Who is saying it
            'coordination': 0.20,          # 20% - How it's being said (patterns)
            'engagement_quality': 0.10     # 10% - Community response quality
        }
        
        self.analysis_history = []
    
    def calculate_truth_score(self, posts: List[Dict], token_data: Dict = None) -> Dict:
        """
        Calculate comprehensive Truth Score for a token
        
        Args:
            posts: List of social media posts (Reddit posts/comments)
            token_data: Optional metadata about the token (price, volume, etc.)
            
        Returns:
            Comprehensive analysis dictionary with:
            - score (0-100): Overall truth score
            - risk_level: Classification (low/medium/high/critical)
            - red_flags: List of detected issues
            - metrics: Detailed component scores
            - breakdown: Quantitative breakdown
        """
        # Validate input
        if not posts or len(posts) == 0:
            return self._default_response()
        
        # Filter valid posts
        valid_posts = [
            p for p in posts 
            if (p.get('text') and len(p.get('text', '').strip()) > 10) or 
               (p.get('title') and len(p.get('title', '').strip()) > 10)
        ]
        
        if not valid_posts:
            return self._default_response()
        
        print(f"\n🧮 Analyzing {len(valid_posts)} valid posts...")
        
        # Run all analysis components
        content_results = self._analyze_content(valid_posts)
        credibility_results = self._analyze_accounts(valid_posts)
        coordination_results = self._detect_coordination(valid_posts)
        engagement_results = self._analyze_engagement(valid_posts)
        
        # Calculate weighted final score
        final_score = (
            (100 - content_results['avg_scam_score']) * self.weights['content_analysis'] +
            credibility_results['avg_credibility'] * self.weights['account_credibility'] +
            (100 - coordination_results['coordination_score']) * self.weights['coordination'] +
            engagement_results['quality_score'] * self.weights['engagement_quality']
        )
        
        # Ensure score is within bounds
        final_score = max(0, min(100, final_score))
        
        # Collect all red flags
        all_red_flags = []
        all_red_flags.extend(content_results['top_flags'])
        all_red_flags.extend(credibility_results['top_flags'])
        
        if coordination_results['is_coordinated']:
            all_red_flags.append(
                f"⚠️  Coordinated activity: {coordination_results['reason']}"
            )
        
        if engagement_results['avg_quality'] < 40:
            all_red_flags.append(
                f"📉 Poor engagement quality ({engagement_results['low_quality_count']} low-quality posts)"
            )
        
        # Get unique flags (remove duplicates while preserving order)
        seen = set()
        unique_flags = []
        for flag in all_red_flags:
            if flag not in seen:
                seen.add(flag)
                unique_flags.append(flag)
        
        # Build comprehensive result
        result = {
            'score': round(final_score, 1),
            'risk_level': self._determine_risk_level(final_score),
            'red_flags': unique_flags[:15],  # Top 15 flags
            'analyzed_posts': len(valid_posts),
            'metrics': {
                'content_scam_score': round(content_results['avg_scam_score'], 1),
                'account_credibility': round(credibility_results['avg_credibility'], 1),
                'coordination_risk': round(coordination_results['coordination_score'], 1),
                'engagement_quality': round(engagement_results['quality_score'], 1),
                'sentiment': content_results['overall_sentiment']
            },
            'breakdown': {
                'high_risk_posts': content_results['high_risk_count'],
                'suspicious_accounts': credibility_results['suspicious_count'],
                'coordinated': coordination_results['is_coordinated'],
                'low_quality_engagement': engagement_results['low_quality_count']
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Store in history
        self.analysis_history.append({
            'score': final_score,
            'timestamp': datetime.now(timezone.utc),
            'post_count': len(valid_posts)
        })
        
        print(f"✅ Truth Score: {result['score']:.1f}/100")
        print(f"   Risk Level: {result['risk_level'].upper()}")
        
        return result
    
    def _analyze_content(self, posts: List[Dict]) -> Dict:
        """
        Analyze content of posts for scam patterns
        
        Returns:
            Dictionary with content analysis results
        """
        print("  📝 Analyzing content...")
        
        scam_scores = []
        all_flags = []
        high_risk_count = 0
        pattern_counts = {}
        
        for post in posts:
            # Combine title and text
            text = f"{post.get('title', '')} {post.get('text', '')}".strip()
            
            if not text or len(text) < 10:
                continue
            
            # Analyze text for scam patterns
            result = self.pattern_detector.analyze_text(text)
            
            scam_scores.append(result['scam_score'])
            all_flags.extend(result['red_flags'])
            
            # Count high-risk posts
            if result['scam_score'] >= 60:
                high_risk_count += 1
            
            # Track pattern types
            for flag in result['red_flags']:
                pattern_type = flag.split(':')[0]
                pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        # Calculate average scam score
        avg_scam_score = statistics.mean(scam_scores) if scam_scores else 50
        
        # Determine overall sentiment
        if avg_scam_score < 25:
            sentiment = 'legitimate'
        elif avg_scam_score < 45:
            sentiment = 'questionable'
        elif avg_scam_score < 65:
            sentiment = 'suspicious'
        else:
            sentiment = 'highly_suspicious'
        
        # Get most common red flags
        from collections import Counter
        flag_counter = Counter(all_flags)
        top_flags = []
        
        for flag, count in flag_counter.most_common(8):
            if count > 1:
                top_flags.append(f"{flag} ({count}x)")
            else:
                top_flags.append(flag)
        
        return {
            'avg_scam_score': avg_scam_score,
            'high_risk_count': high_risk_count,
            'top_flags': top_flags,
            'overall_sentiment': sentiment,
            'pattern_distribution': pattern_counts
        }
    
    def _analyze_accounts(self, posts: List[Dict]) -> Dict:
        """
        Analyze credibility of accounts posting content
        
        Returns:
            Dictionary with account analysis results
        """
        print("  👤 Analyzing accounts...")
        
        credibility_scores = []
        all_flags = []
        suspicious_count = 0
        account_types = {'new': 0, 'low_karma': 0, 'suspicious_username': 0, 'deleted': 0}
        
        for post in posts:
            # Prepare account data
            account_data = {
                'username': post.get('author', ''),
                'karma': post.get('score', 0),
                'account_age_days': self._calculate_account_age(post)
            }
            
            # Analyze account
            result = self.pattern_detector.analyze_account(account_data)
            
            credibility_scores.append(result['credibility_score'])
            all_flags.extend(result['red_flags'])
            
            # Count suspicious accounts
            if result['credibility_score'] < 40:
                suspicious_count += 1
            
            # Categorize account issues
            for flag in result['red_flags']:
                if 'new account' in flag.lower():
                    account_types['new'] += 1
                if 'karma' in flag.lower():
                    account_types['low_karma'] += 1
                if 'username' in flag.lower():
                    account_types['suspicious_username'] += 1
                if 'deleted' in flag.lower():
                    account_types['deleted'] += 1
        
        # Calculate average credibility
        avg_credibility = statistics.mean(credibility_scores) if credibility_scores else 50
        
        # Get most common account issues
        from collections import Counter
        flag_counter = Counter(all_flags)
        top_flags = []
        
        for flag, count in flag_counter.most_common(5):
            if count > 1:
                top_flags.append(f"👤 {flag} ({count} accounts)")
            else:
                top_flags.append(f"👤 {flag}")
        
        return {
            'avg_credibility': avg_credibility,
            'suspicious_count': suspicious_count,
            'top_flags': top_flags,
            'account_types': account_types
        }
    
    def _detect_coordination(self, posts: List[Dict]) -> Dict:
        """
        Detect coordinated manipulation campaigns
        
        Returns:
            Dictionary with coordination analysis
        """
        print("  🔗 Checking for coordination...")
        
        result = self.pattern_detector.detect_coordinated_activity(posts)
        
        # Calculate coordination risk score
        if result['coordinated']:
            coordination_score = result['confidence']
        else:
            coordination_score = 0
        
        return {
            'is_coordinated': result['coordinated'],
            'coordination_score': coordination_score,
            'reason': result.get('reason', 'No coordination detected'),
            'pattern': result.get('pattern', 'none')
        }
    
    def _analyze_engagement(self, posts: List[Dict]) -> Dict:
        """
        Analyze quality of community engagement
        
        Returns:
            Dictionary with engagement analysis
        """
        print("  📊 Analyzing engagement...")
        
        quality_scores = []
        low_quality_count = 0
        engagement_metrics = {
            'high_engagement': 0,
            'medium_engagement': 0,
            'low_engagement': 0,
            'negative_engagement': 0
        }
        
        for post in posts:
            score = post.get('score', 0)
            num_comments = post.get('num_comments', 0)
            post_type = post.get('type', 'unknown')
            
            # Quality heuristic
            if post_type == 'post':
                # Posts with good engagement
                if score > 20 and num_comments > 10:
                    quality = 90
                    engagement_metrics['high_engagement'] += 1
                elif score > 5 and num_comments > 3:
                    quality = 70
                    engagement_metrics['medium_engagement'] += 1
                elif score > 0:
                    quality = 50
                    engagement_metrics['low_engagement'] += 1
                else:
                    quality = 20
                    engagement_metrics['negative_engagement'] += 1
                    low_quality_count += 1
            else:
                # Comments
                if score > 10:
                    quality = 80
                    engagement_metrics['high_engagement'] += 1
                elif score > 3:
                    quality = 65
                    engagement_metrics['medium_engagement'] += 1
                elif score >= 0:
                    quality = 45
                    engagement_metrics['low_engagement'] += 1
                else:
                    quality = 25
                    engagement_metrics['negative_engagement'] += 1
                    low_quality_count += 1
            
            quality_scores.append(quality)
        
        avg_quality = statistics.mean(quality_scores) if quality_scores else 50
        
        return {
            'quality_score': avg_quality,
            'avg_quality': avg_quality,
            'low_quality_count': low_quality_count,
            'engagement_metrics': engagement_metrics
        }
    
    def _calculate_account_age(self, post: Dict) -> int:
        """
        Calculate account age in days from post data
        
        Args:
            post: Post dictionary
            
        Returns:
            Age in days (defaults to 999 if unknown)
        """
        if 'created_utc' in post:
            try:
                created = post['created_utc']
                if isinstance(created, datetime):
                    age = datetime.now() - created
                    return age.days
            except:
                pass
        
        return 999  # Assume old account if unknown
    
    def _determine_risk_level(self, score: float) -> str:
        """
        Convert numeric score to risk level category
        
        Args:
            score: Truth score (0-100)
            
        Returns:
            Risk level string (low/medium/high/critical)
        """
        if score >= 75:
            return 'low'
        elif score >= 55:
            return 'medium'
        elif score >= 35:
            return 'high'
        else:
            return 'critical'
    
    def _default_response(self) -> Dict:
        """
        Return default response when analysis cannot be performed
        
        Returns:
            Default analysis dictionary
        """
        return {
            'score': 50,
            'risk_level': 'unknown',
            'red_flags': ['⚠️  Insufficient data for comprehensive analysis'],
            'analyzed_posts': 0,
            'metrics': {
                'content_scam_score': 0,
                'account_credibility': 0,
                'coordination_risk': 0,
                'engagement_quality': 0,
                'sentiment': 'unknown'
            },
            'breakdown': {
                'high_risk_posts': 0,
                'suspicious_accounts': 0,
                'coordinated': False,
                'low_quality_engagement': 0
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def get_risk_recommendation(self, truth_score: float) -> Dict:
        """
        Generate actionable recommendations based on Truth Score
        
        Args:
            truth_score: The calculated truth score (0-100)
            
        Returns:
            Dictionary with recommendation, message, and action items
        """
        if truth_score >= 75:
            return {
                'recommendation': '✅ PROCEED WITH CAUTION',
                'message': 'This token shows relatively low risk indicators based on social media analysis. However, always conduct your own research and never invest more than you can afford to lose.',
                'actions': [
                    'Verify project legitimacy through official channels',
                    'Check team credentials and project roadmap',
                    'Review smart contract audits if available',
                    'Start with small investment amounts',
                    'Monitor for any changes in social sentiment'
                ]
            }
        elif truth_score >= 55:
            return {
                'recommendation': '⚠️  EXERCISE CAUTION',
                'message': 'Moderate risk detected in social media activity. Additional verification is strongly recommended before any investment decision.',
                'actions': [
                    'Investigate all red flags thoroughly',
                    'Look for independent third-party audits',
                    'Verify contract address on blockchain explorers',
                    'Check for liquidity locks and tokenomics',
                    'Avoid FOMO - take time for proper research',
                    'Consult multiple information sources'
                ]
            }
        elif truth_score >= 35:
            return {
                'recommendation': '🚫 HIGH RISK - AVOID',
                'message': 'Significant scam indicators detected in social media activity. Investment is not recommended without extensive additional verification.',
                'actions': [
                    'Do NOT invest based on social media hype alone',
                    'Multiple red flags indicate possible manipulation',
                    'If considering investment, wait for more information',
                    'Consult with experienced crypto investors',
                    'Be extremely wary of time pressure tactics',
                    'Report suspicious activity to platform moderators'
                ]
            }
        else:
            return {
                'recommendation': '⛔ CRITICAL RISK - DO NOT INVEST',
                'message': 'Strong scam indicators detected. This appears to be a fraudulent scheme or heavily manipulated token. Do not invest under any circumstances.',
                'actions': [
                    'DO NOT INVEST - high probability of scam',
                    'Do not send any funds or connect wallets',
                    'Report to relevant authorities and platforms',
                    'Warn others in the community about this token',
                    'Block and ignore promotional accounts',
                    'If you already invested, seek immediate assistance'
                ]
            }
    
    def get_analysis_summary(self) -> Dict:
        """
        Get summary statistics of all analyses performed
        
        Returns:
            Summary statistics dictionary
        """
        if not self.analysis_history:
            return {
                'total_analyses': 0,
                'average_score': 0,
                'risk_distribution': {}
            }
        
        scores = [a['score'] for a in self.analysis_history]
        
        risk_dist = {
            'low': sum(1 for s in scores if s >= 75),
            'medium': sum(1 for s in scores if 55 <= s < 75),
            'high': sum(1 for s in scores if 35 <= s < 55),
            'critical': sum(1 for s in scores if s < 35)
        }
        
        return {
            'total_analyses': len(self.analysis_history),
            'average_score': round(statistics.mean(scores), 1),
            'median_score': round(statistics.median(scores), 1),
            'risk_distribution': risk_dist,
            'recent_scores': scores[-10:]  # Last 10 scores
        }


# Testing and example usage
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Truth Scorer")
    print("="*60 + "\n")
    
    scorer = TruthScorer()
    
    # Create sample posts
    test_posts = [
        {
            'title': '🚀 NEW GEM! 1000X GUARANTEED! 🚀',
            'text': 'This is going to moon! DM for presale! Trust me!',
            'author': 'CryptoKing12345',
            'score': 2,
            'num_comments': 0,
            'created_utc': datetime.now(timezone.utc) - timedelta(days=2),
            'type': 'post'
        },
        {
            'title': 'Analysis of new token economics',
            'text': 'I analyzed the tokenomics and found some concerning aspects regarding the distribution model.',
            'author': 'ExperiencedTrader',
            'score': 45,
            'num_comments': 12,
            'created_utc': datetime.now(timezone.utc) - timedelta(days=365),
            'type': 'post'
        },
        {
            'text': 'Looks like a pump and dump scheme to me. Be careful everyone.',
            'author': 'CryptoWatcher',
            'score': 28,
            'created_utc': datetime.now(timezone.utc) - timedelta(days=200),
            'type': 'comment'
        }
    ]
    
    print("📊 Analyzing sample posts...")
    result = scorer.calculate_truth_score(test_posts)
    
    print(f"\n✅ Truth Score: {result['score']}/100")
    print(f"🚨 Risk Level: {result['risk_level'].upper()}")
    
    print(f"\n📋 Red Flags ({len(result['red_flags'])}):")
    for i, flag in enumerate(result['red_flags'], 1):
        print(f"  {i}. {flag}")
    
    print(f"\n📊 Metrics:")
    for key, value in result['metrics'].items():
        print(f"  {key}: {value}")
    
    print(f"\n🔍 Breakdown:")
    for key, value in result['breakdown'].items():
        print(f"  {key}: {value}")
    
    # Get recommendation
    rec = scorer.get_risk_recommendation(result['score'])
    print(f"\n💡 Recommendation:")
    print(f"  {rec['recommendation']}")
    print(f"  {rec['message']}")
    
    print("\n" + "="*60)
    print("✅ Test Complete")
    print("="*60 + "\n")