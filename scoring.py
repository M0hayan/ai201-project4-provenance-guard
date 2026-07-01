def calculate_confidence(llm_score, stylometric_score):
    """
    Combines both signals.

    LLM = 60%
    Stylometric = 40%
    """

    combined_score = (
        (llm_score * 0.6) +
        (stylometric_score * 0.4)
    )


    combined_score = round(combined_score, 2)


    if combined_score >= 0.70:
        attribution = "likely_ai"

    elif combined_score >= 0.40:
        attribution = "uncertain"

    else:
        attribution = "likely_human"


    return {
        "confidence": combined_score,
        "attribution": attribution
    }