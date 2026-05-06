
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
            SUM(CASE WHEN flagged THEN 1 ELSE 0 END) as flagged_count
        FROM conversations
        WHERE created_at >= NOW() - INTERVAL ':days days'
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    ''', {"days": days})
    return {"trend": [dict(r) for r in rows]}

