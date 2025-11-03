"""
Pattern-Based Scam Detector
Detects cryptocurrency scams using rule-based pattern matching
No AI required - uses heuristics and known scam patterns
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime, timezone, timedelta
from collections import Counter

class PatternDetector:
    """
    Detects scam patterns in cryptocurrency-related content
    Uses pattern matching, keyword analysis, and behavioral heuristics
    """
    
    # Scam keyword categories with severity weights
    SCAM_PATTERNS = {
        'urgency': {
            'keywords': [
                'now', 'hurry', 'quick', 'fast', 'urgent', 'limited time',
                'last chance', 'ending soon', 'act now', 'don\'t wait',
                'expires', 'hurry up', 'right now', 'immediately', 'asap'
            ],
            'weight': 15,
            'description': 'Urgency tactics'
        },
        'fomo': {
            'keywords': [
                'moon', 'lambo', 'rocket', '🚀', 'x100', 'x1000', 'x10000',
                'to the moon', 'don\'t miss', 'regret', 'next bitcoin',
                'next eth', 'gem', 'hidden gem', 'before it\'s too late',
                'massive gains', 'life changing', 'retire', 'financial freedom'
            ],
            'weight': 20,
            'description': 'FOMO (Fear of Missing Out) language'
        },
        'guaranteed': {
            'keywords': [
                'guaranteed', 'certain', 'sure thing', 'no risk', 'can\'t lose',
                'safe bet', '100%', 'definitely', 'promise', 'assured',
                'risk-free', 'zero risk', 'cannot fail', 'will moon',
                'guaranteed profit', 'guaranteed returns'
            ],
            'weight': 25,
            'description': 'Unrealistic guarantees'
        },
        'pressure': {
            'keywords': [
                'dm me', 'join now', 'buy now', 'act fast', 'spots left',
                'slots available', 'first 100', 'limited spots', 'whitelist',
                'exclusive access', 'vip only', 'members only', 'invite only',
                'private group', 'secret', 'insider info'
            ],
            'weight': 20,
            'description': 'High-pressure tactics'
        },
        'suspicious_offers': {
            'keywords': [
                'airdrop', 'giveaway', 'free tokens', 'free crypto', 'presale',
                'private sale', 'ico', 'ido', 'early access', 'presale price',
                'bonus tokens', 'double your', 'triple your', 'multiply your'
            ],
            'weight': 15,
            'description': 'Suspicious offers'
        },
        'pump_signals': {
            'keywords': [
                'pump', 'dump', 'signal', 'call', 'target', 'entry point',
                'exit point', 'buy zone', 'sell zone', 'accumulation',
                'distribution', 'pump group', 'signal group', 'trading signal',
                'buy signal', 'sell signal'
            ],
            'weight': 30,
            'description': 'Pump & dump indicators'
        },
        'fake_authority': {
            'keywords': [
                'expert', 'professional trader', 'whale', 'insider',
                'team member', 'advisor', 'partner', 'affiliated',
                'endorsed by', 'recommended by', 'approved by',
                'verified by', 'certified'
            ],
            'weight': 18,
            'description': 'False authority claims'
        }
    }
    
    # Known scam phrase patterns
    SCAM_PHRASES = [
        r'send.*(?:btc|eth|usdt|bnb).*(?:receive|get)',
        r'\d+x.*guaranteed',
        r'double.*(?:bitcoin|crypto|money|investment)',
        r'triple.*(?:bitcoin|crypto|money|investment)',
        r'elon.*musk.*(?:giveaway|airdrop)',
        r'verify.*wallet.*(?:claim|receive)',
        r'connect.*wallet.*(?:claim|receive|get)',
        r'smart.*contract.*(?:guaranteed|safe|approved)',
        r'audit.*(?:passed|approved|verified).*trust',
        r'liquidity.*locked.*safe',
    ]
    
    def __init__(self):
        """Initialize the pattern detector"""
        self.scam_count = 0
        self.analysis_count = 0
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for scam patterns and manipulation tactics
        
        Args:
            text: The text content to analyze (post, comment, message)
            
        Returns:
            Dictionary containing:
            - scam_score (0-100): Higher = more likely a scam
            - red_flags: List of detected issues
            - risk_level: low/medium/high/critical
            - pattern_matches: Number of patterns detected
        """
        if not text or len(text.strip()) < 10:
            return self._empty_result()
        
        self.analysis_count += 1
        text_lower = text.lower()
        red_flags = []
        score = 0
        
        # Check each keyword category
        for category, data in self.SCAM_PATTERNS.items():
            matches = [kw for kw in data['keywords'] if kw in text_lower]
            if matches:
                # Calculate points based on number of matches and weight
                category_score = min(len(matches) * data['weight'], data['weight'] * 2)
                score += category_score
                
                # Add red flag with specific examples
                flag_text = f"{data['description']}: {', '.join(matches[:3])}"
                if len(matches) > 3:
                    flag_text += f" (+{len(matches)-3} more)"
                red_flags.append(flag_text)
        
        # Check for scam phrase patterns
        for pattern in self.SCAM_PHRASES:
            matches = re.findall(pattern, text_lower)
            if matches:
                score += 25
                red_flags.append(f"Known scam phrase pattern detected")
                break  # Only flag once for phrases
        
        # Check for unrealistic return promises
        return_patterns = [
            (r'(\d+)x\s*(?:profit|gain|return|moon)', 'X multiplier promise'),
            (r'(\d+)%\s*(?:profit|gain|return|apy|apr)', 'Percentage return promise'),
            (r'make\s*\$?(\d+k|\d+,\d+)', 'Specific dollar amount promise'),
            (r'earn\s*\$?(\d+k|\d+,\d+)', 'Earning promise')
        ]
        
        for pattern, desc in return_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    # Extract the number
                    num_str = match.group(1).replace('k', '000').replace(',', '')
                    value = int(re.search(r'\d+', num_str).group())
                    
                    if value >= 100:  # 100x, 100%, or $100k+
                        score += 30
                        red_flags.append(f"{desc}: {value}")
                        break
                except:
                    pass
        
        # Check for excessive capitalization
        if len(text) > 20:
            caps_count = sum(1 for c in text if c.isupper())
            caps_ratio = caps_count / len(text)
            
            if caps_ratio > 0.5:
                score += 20
                red_flags.append(f"Excessive caps lock ({int(caps_ratio*100)}% of text)")
            elif caps_ratio > 0.3:
                score += 10
                red_flags.append(f"High caps usage ({int(caps_ratio*100)}%)")
        
        # Check for excessive emojis
        emoji_pattern = r'[\U0001F300-\U0001F9FF]|🚀|💎|🙌|💰|📈|📊|🔥|⚡|💸|🤑|💵|💴'
        emojis = re.findall(emoji_pattern, text)
        emoji_count = len(emojis)
        
        if emoji_count > 10:
            score += 20
            red_flags.append(f"Excessive emojis ({emoji_count} emojis)")
        elif emoji_count > 5:
            score += 10
            red_flags.append(f"Many emojis ({emoji_count} emojis)")
        
        # Check for suspicious links
        suspicious_domains = [
            'bit.ly', 'tinyurl', 't.me/+', 'discord.gg',
            'forms.gle', 'rb.gy', 'cutt.ly', 'shorturl'
        ]
        
        for domain in suspicious_domains:
            if domain in text_lower:
                score += 20
                red_flags.append(f"Suspicious shortened link: {domain}")
                break
        
        # Check for crypto wallet addresses
        wallet_patterns = [
            (r'0x[a-fA-F0-9]{40}', 'Ethereum address'),
            (r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}', 'Bitcoin address'),
            (r'T[A-Za-z1-9]{33}', 'Tron address')
        ]
        
        for pattern, addr_type in wallet_patterns:
            if re.search(pattern, text):
                score += 15
                red_flags.append(f"Contains {addr_type} (potential fund request)")
                break
        
        # Check for excessive exclamation marks
        exclaim_count = text.count('!')
        if exclaim_count > 10:
            score += 15
            red_flags.append(f"Excessive excitement ({exclaim_count} exclamation marks)")
        elif exclaim_count > 5:
            score += 8
            red_flags.append(f"High excitement level ({exclaim_count} exclamation marks)")
        
        # Check for defensive/trust-seeking language
        trust_phrases = [
            'trust me', 'believe me', 'i promise', 'honest',
            'legit', 'not a scam', 'legitimate', '100% real',
            'no scam', 'real deal', 'verified'
        ]
        
        trust_matches = [phrase for phrase in trust_phrases if phrase in text_lower]
        if trust_matches:
            score += 18
            red_flags.append(f"Trust-seeking language: {', '.join(trust_matches[:2])}")
        
        # Check for time-sensitive language patterns
        time_patterns = [
            'today only', 'ends tonight', 'midnight', 'hours left',
            'minutes left', 'expiring', 'deadline', 'countdown'
        ]
        
        time_matches = [p for p in time_patterns if p in text_lower]
        if time_matches:
            score += 12
            red_flags.append(f"Time pressure: {', '.join(time_matches[:2])}")
        
        # Cap score at 100
        final_score = min(score, 100)
        
        if final_score >= 70:
            self.scam_count += 1
        
        return {
            'scam_score': final_score,
            'red_flags': red_flags[:15],  # Top 15 flags
            'risk_level': self._calculate_risk_level(final_score),
            'pattern_matches': len(red_flags)
        }
    
    def analyze_account(self, account_data: Dict) -> Dict:
        """
        Analyze account credibility and detect potential bot/shill accounts
        
        Args:
            account_data: Dictionary with account information
                - username: Account username
                - karma: Total karma/reputation
                - account_age_days: Age of account in days
                - posts_per_day: Average posts per day (optional)
                
        Returns:
            Dictionary with credibility assessment
        """
        red_flags = []
        suspicion_score = 0
        
        # Check account age
        age_days = account_data.get('account_age_days', 999)
        
        if age_days < 7:
            suspicion_score += 40
            red_flags.append(f"Very new account ({age_days} days old)")
        elif age_days < 30:
            suspicion_score += 25
            red_flags.append(f"New account ({age_days} days old)")
        elif age_days < 90:
            suspicion_score += 10
            red_flags.append(f"Relatively new account ({age_days} days old)")
        
        # Check karma/reputation score
        karma = account_data.get('karma', 0)
        
        if karma < 10:
            suspicion_score += 30
            red_flags.append(f"Very low karma ({karma})")
        elif karma < 50:
            suspicion_score += 20
            red_flags.append(f"Low karma ({karma})")
        elif karma < 100:
            suspicion_score += 10
            red_flags.append(f"Minimal karma ({karma})")
        
        # Check username patterns (common bot naming patterns)
        username = account_data.get('username', '')
        
        if username and username != '[deleted]':
            # Pattern 1: word + numbers (e.g., user12345)
            if re.match(r'^[a-z]+\d{4,}$', username.lower()):
                suspicion_score += 20
                red_flags.append("Generic username pattern (word+numbers)")
            
            # Pattern 2: CamelCase + numbers (e.g., CryptoKing12345)
            elif re.match(r'^[A-Z][a-z]+([A-Z][a-z]+)+\d+$', username):
                suspicion_score += 18
                red_flags.append("Bot-like username (CamelCase+numbers)")
            
            # Pattern 3: Random characters
            elif re.match(r'^[a-zA-Z]{1,3}\d{6,}$', username):
                suspicion_score += 25
                red_flags.append("Random character username")
            
            # Pattern 4: Crypto keywords in username
            crypto_keywords = ['crypto', 'moon', 'pump', 'gem', 'hodl', 'whale']
            if any(kw in username.lower() for kw in crypto_keywords):
                suspicion_score += 12
                red_flags.append("Crypto-focused username (possible shill)")
        
        # Check posting frequency (if available)
        posts_per_day = account_data.get('posts_per_day', 0)
        
        if posts_per_day > 50:
            suspicion_score += 25
            red_flags.append(f"Extremely high posting rate ({posts_per_day}/day)")
        elif posts_per_day > 30:
            suspicion_score += 18
            red_flags.append(f"Very high posting rate ({posts_per_day}/day)")
        elif posts_per_day > 20:
            suspicion_score += 10
            red_flags.append(f"High posting rate ({posts_per_day}/day)")
        
        # Check if account is deleted
        if username == '[deleted]':
            suspicion_score += 20
            red_flags.append("Deleted/suspended account")
        
        # Calculate credibility (inverse of suspicion)
        credibility_score = max(0, 100 - min(suspicion_score, 100))
        
        return {
            'credibility_score': credibility_score,
            'red_flags': red_flags,
            'risk_level': self._calculate_risk_level(suspicion_score),
            'is_suspicious': credibility_score < 50
        }
    
    def detect_coordinated_activity(self, posts: List[Dict]) -> Dict:
        """
        Detect signs of coordinated manipulation campaigns
        
        Args:
            posts: List of post dictionaries to analyze
            
        Returns:
            Dictionary with coordination indicators
        """
        if len(posts) < 5:
            return {
                'coordinated': False,
                'confidence': 0,
                'reason': 'Insufficient data for analysis'
            }
        
        # Check 1: Posting time clustering
        timestamps = [p.get('created_utc') for p in posts if 'created_utc' in p]
        
        if len(timestamps) > 3:
            sorted_times = sorted(timestamps)
            time_gaps = []
            
            for i in range(len(sorted_times) - 1):
                gap = (sorted_times[i + 1] - sorted_times[i]).total_seconds()
                time_gaps.append(gap)
            
            # Count posts within 5 minutes of each other
            close_posts = sum(1 for gap in time_gaps if gap < 300)
            
            if close_posts > len(posts) * 0.4:
                return {
                    'coordinated': True,
                    'confidence': 75,
                    'reason': f'{close_posts} posts clustered within 5 minutes',
                    'pattern': 'temporal_clustering'
                }
        
        # Check 2: Text similarity (copy-paste detection)
        texts = []
        for p in posts:
            full_text = f"{p.get('title', '')} {p.get('text', '')}".strip()
            if full_text:
                texts.append(full_text)
        
        if len(texts) >= 3:
            similar_pairs = 0
            total_comparisons = 0
            
            for i, text1 in enumerate(texts):
                for text2 in texts[i+1:]:
                    total_comparisons += 1
                    similarity = self._text_similarity(text1, text2)
                    if similarity > 0.7:
                        similar_pairs += 1
            
            if total_comparisons > 0 and similar_pairs / total_comparisons > 0.3:
                return {
                    'coordinated': True,
                    'confidence': 85,
                    'reason': f'{similar_pairs} pairs of very similar content detected',
                    'pattern': 'content_duplication'
                }
        
        # Check 3: Author concentration
        authors = [p.get('author') for p in posts if p.get('author') and p.get('author') != '[deleted]']
        
        if authors:
            unique_authors = set(authors)
            author_ratio = len(unique_authors) / len(authors)
            
            if author_ratio < 0.5:
                return {
                    'coordinated': True,
                    'confidence': 70,
                    'reason': f'Only {len(unique_authors)} authors for {len(authors)} posts',
                    'pattern': 'author_concentration'
                }
        
        # Check 4: Identical hashtags/emojis pattern
        emoji_patterns = [re.findall(r'[\U0001F300-\U0001F9FF🚀💎]', p.get('text', '')) for p in posts]
        
        if emoji_patterns:
            emoji_strings = [''.join(sorted(ep)) for ep in emoji_patterns if ep]
            if emoji_strings:
                most_common = Counter(emoji_strings).most_common(1)[0]
                if most_common[1] > len(posts) * 0.6:
                    return {
                        'coordinated': True,
                        'confidence': 65,
                        'reason': f'Identical emoji pattern in {most_common[1]} posts',
                        'pattern': 'emoji_coordination'
                    }
        
        return {
            'coordinated': False,
            'confidence': 0,
            'reason': 'No significant coordination detected'
        }
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity between two texts
        
        Args:
            text1, text2: Texts to compare
            
        Returns:
            Similarity score (0-1)
        """
        # Tokenize and clean
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Remove very common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'on', 'at'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_risk_level(self, score: int) -> str:
        """Convert numeric score to risk level category"""
        if score >= 70:
            return 'critical'
        elif score >= 50:
            return 'high'
        elif score >= 30:
            return 'medium'
        else:
            return 'low'
    
    def _empty_result(self) -> Dict:
        """Return empty analysis result for invalid input"""
        return {
            'scam_score': 0,
            'red_flags': ['Text too short for analysis'],
            'risk_level': 'unknown',
            'pattern_matches': 0
        }
    
    def get_statistics(self) -> Dict:
        """Get detector statistics"""
        return {
            'total_analyzed': self.analysis_count,
            'scams_detected': self.scam_count,
            'scam_rate': (self.scam_count / self.analysis_count * 100) if self.analysis_count > 0 else 0
        }


# Testing and example usage
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Pattern Detector")
    print("="*60 + "\n")
    
    detector = PatternDetector()
    
    # Test 1: Obvious scam
    print("📝 Test 1: Obvious Scam Text")
    scam_text = """
    🚀🚀🚀 URGENT! NEW TOKEN LAUNCHING NOW! 🚀🚀🚀
    
    Get in NOW before it goes 1000x! This is GUARANTEED to moon!
    Last chance to become a millionaire! Only 50 spots left!
    
    DM me for presale access! Not a scam, trust me! 💎🙌
    Send 0.1 ETH to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
    """
    
    result = detector.analyze_text(scam_text)
    print(f"Scam Score: {result['scam_score']}/100")
    print(f"Risk Level: {result['risk_level'].upper()}")
    print(f"Red Flags ({len(result['red_flags'])}):")
    for flag in result['red_flags']:
        print(f"  • {flag}")
    
    # Test 2: Legitimate discussion
    print("\n📝 Test 2: Legitimate Discussion")
    legit_text = """
    I've been researching Bitcoin's layer 2 solutions and the Lightning Network
    seems promising for scaling. Has anyone tried using it for actual transactions?
    The fee reduction compared to on-chain transactions is significant.
    """
    
    result2 = detector.analyze_text(legit_text)
    print(f"Scam Score: {result2['scam_score']}/100")
    print(f"Risk Level: {result2['risk_level'].upper()}")
    
    # Test 3: Account analysis
    print("\n📝 Test 3: Suspicious Account")
    suspicious_account = {
        'username': 'CryptoMoonPump12345',
        'karma': 5,
        'account_age_days': 3,
        'posts_per_day': 45
    }
    
    account_result = detector.analyze_account(suspicious_account)
    print(f"Credibility: {account_result['credibility_score']}/100")
    print(f"Risk Level: {account_result['risk_level'].upper()}")
    print(f"Red Flags: {account_result['red_flags']}")
    
    # Stats
    print("\n📊 Detector Statistics:")
    stats = detector.get_statistics()
    print(f"Total Analyzed: {stats['total_analyzed']}")
    print(f"Scams Detected: {stats['scams_detected']}")
    
    print("\n" + "="*60)
    print("✅ Tests Complete")
    print("="*60 + "\n")