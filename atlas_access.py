"""Server-enforced Atlas free question allowance."""

FREE_QUESTIONS = 5


def claim_question(client):
    """Atomically claim a free question in Supabase; never trust browser state."""
    result = client.rpc('claim_atlas_question').execute().data
    if not isinstance(result, dict) or not isinstance(result.get('allowed'), bool):
        raise ValueError('Atlas allowance unavailable')
    return result

