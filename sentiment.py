from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


_analyzer = SentimentIntensityAnalyzer()


def score(text: str) -> float:
    """Return VADER compound sentiment in [-1, 1]."""
    if not text:
        return 0.0
    return _analyzer.polarity_scores(text)["compound"]
