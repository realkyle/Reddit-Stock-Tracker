from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def score_text(text: str) -> float:
    """Return compound VADER score: -1.0 (very negative) to +1.0 (very positive)."""
    if not text:
        return 0.0
    return _analyzer.polarity_scores(text)["compound"]


def score_post(post: dict) -> float:
    """Score a post by combining title and body text."""
    combined = f"{post.get('title', '')} {post.get('text', '')}".strip()
    return score_text(combined)


def label(score: float) -> str:
    if score >= 0.05:
        return "bullish"
    if score <= -0.05:
        return "bearish"
    return "neutral"
