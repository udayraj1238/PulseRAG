
@router.get("/hallucination-trend")
async def hallucination_trend(days: int = 7):
    '''
