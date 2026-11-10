from collections import defaultdict, deque
from time import time

from fastapi import Depends, HTTPException, status

from app.auth.api_key import get_current_school
from app.models import School


# Maximum 60 requests in 60 seconds
RATE_LIMIT = 60
TIME_WINDOW = 60

# Stores request timestamps separately for each school
_recent_requests = defaultdict(deque)


def rate_limit(
    school: School = Depends(get_current_school),
):
    current_time = time()

    requests = _recent_requests[school.api_key]

    # Remove requests older than 60 seconds
    while requests and current_time - requests[0] >= TIME_WINDOW:
        requests.popleft()

    # Reject requests if the limit has been reached
    if len(requests) >= RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 60 requests per minute.",
        )

    # Record this request
    requests.append(current_time)