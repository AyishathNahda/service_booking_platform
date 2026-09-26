from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Booking, User, RoleEnum
from app.schemas import BookingCreate, BookingUpdate, BookingResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if booking_in.end_time <= booking_in.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")
    
    provider = db.query(User).filter(User.id == booking_in.provider_id, User.role == RoleEnum.provider).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    new_booking = Booking(
        provider_id=booking_in.provider_id,
        customer_id=current_user.id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

def check_booking_ownership(booking: Booking, current_user: User):
    if current_user.role == RoleEnum.admin:
        return
    if current_user.role == RoleEnum.provider and booking.provider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this booking")
    if current_user.role == RoleEnum.customer and booking.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this booking")

@router.get("", response_model=List[BookingResponse])
def get_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.admin:
        return db.query(Booking).all()
    elif current_user.role == RoleEnum.provider:
        return db.query(Booking).filter(Booking.provider_id == current_user.id).all()
    else:
        return db.query(Booking).filter(Booking.customer_id == current_user.id).all()

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    check_booking_ownership(booking, current_user)
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    check_booking_ownership(booking, current_user)
        
    if booking_in.status is not None:
        booking.status = booking_in.status
    if booking_in.start_time is not None:
        booking.start_time = booking_in.start_time
    if booking_in.end_time is not None:
        booking.end_time = booking_in.end_time
        
    if booking.end_time <= booking.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    check_booking_ownership(booking, current_user)
        
    db.delete(booking)
    db.commit()
    return None
