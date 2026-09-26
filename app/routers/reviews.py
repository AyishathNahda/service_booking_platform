from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Review, Booking, User, RoleEnum, BookingStatusEnum
from app.schemas import ReviewCreate, ReviewResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. verify authenticated user is a customer
    if current_user.role != RoleEnum.customer:
        raise HTTPException(status_code=403, detail="Only customers can leave reviews")
        
    # 2. booking exists
    booking = db.query(Booking).filter(Booking.id == review_in.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # 3. booking belongs to that customer
    if booking.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to review this booking")
        
    # 4. booking status is completed
    if booking.status != BookingStatusEnum.completed:
        raise HTTPException(status_code=400, detail="Can only review completed bookings")
        
    # 5. booking does not already have a review
    existing_review = db.query(Review).filter(Review.booking_id == booking.id).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="Booking already has a review")

    new_review = Review(
        booking_id=booking.id,
        customer_id=current_user.id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/provider/{provider_id}", response_model=List[ReviewResponse])
def get_provider_reviews(
    provider_id: int,
    db: Session = Depends(get_db)
):
    provider = db.query(User).filter(User.id == provider_id, User.role == RoleEnum.provider).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    reviews = db.query(Review).join(Booking).filter(Booking.provider_id == provider_id).all()
    return reviews

import uuid
import json
import redis
from app.config import settings
from app.schemas import ReviewSummarizeRequest, ReviewSummarizeResponse

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.post("/summarize", response_model=ReviewSummarizeResponse)
def summarize_reviews(
    request: ReviewSummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [RoleEnum.admin, RoleEnum.provider]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == RoleEnum.provider and current_user.id != request.provider_id:
        raise HTTPException(status_code=403, detail="Can only summarize your own reviews")
        
    provider = db.query(User).filter(User.id == request.provider_id, User.role == RoleEnum.provider).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "provider_id": request.provider_id
    }
    
    redis_client.lpush("review_summary_queue", json.dumps(job_data))
    
    return {"message": "Review summarisation job queued", "job_id": job_id}
