import re
import statistics


def analyze_stylometry(text):

    sentences = [
        s.strip()
        for s in re.split(r'[.!?]+', text)
        if s.strip()
    ]

    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())


    if len(words) < 20:
        return {
            "stylometric_score": 0.5,
            "reason": "Text too short."
        }


    # Sentence length consistency
    lengths = [
        len(sentence.split())
        for sentence in sentences
    ]

    variance = statistics.pvariance(lengths)

    # Very consistent sentences = AI-like
    consistency_score = max(
        0,
        min(1, 1 - (variance / 50))
    )


    # Vocabulary repetition
    unique_ratio = len(set(words)) / len(words)

    repetition_score = max(
        0,
        min(1, 1 - unique_ratio)
    )


    # Formal transition words
    ai_phrases = [
        "furthermore",
        "it is important to note",
        "in conclusion",
        "moreover",
        "stakeholders",
        "various sectors"
    ]

    phrase_count = sum(
        text.lower().count(p)
        for p in ai_phrases
    )

    phrase_score = min(
        1,
        phrase_count / 3
    )


    final_score = (
        consistency_score * 0.3 +
        repetition_score * 0.2 +
        phrase_score * 0.5
    )


    return {
        "stylometric_score": round(final_score, 2),
        "metrics": {
            "sentence_variance": round(variance, 2),
            "vocabulary_ratio": round(unique_ratio, 2),
            "ai_phrase_score": round(phrase_score, 2)
        }
    }