
@router.get("/hallucination-trend")
async def hallucination_trend(days: int = 7):
    '''
    Returns average hallucination risk per day for the past N days.
    This is what you show in your README as a graph.
    '''
    rows = await db.fetch_all('''
        SELECT 
            DATE(created_at) as date,
            AVG(hallucination_risk) as avg_risk,
            COUNT(*) as query_count,
