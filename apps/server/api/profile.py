from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from middleware.auth import verify_session
from utils.logger import logger
from prisma import Prisma

router = APIRouter(prefix="/profile", tags=["Profile"])


class ProfileResponse(BaseModel):
    id: str
    userId: str
    userName: str
    email: str
    image: Optional[str] = None
    createdAt: str
    updatedAt: str


class ProfileUpdateRequest(BaseModel):
    userName: Optional[str] = None
    image: Optional[str] = None


@router.get("/", response_model=ProfileResponse)
async def get_profile(user=Depends(verify_session)):
    """Get user profile"""
    try:
        async with Prisma() as db:
            profile = await db.profile.find_unique(where={"userId": user.id})

            if not profile:
                # Create profile if it doesn't exist
                profile = await db.profile.create(
                    data={
                        "userId": user.id,
                        "email": user.email,
                        "userName": user.email.split("@")[0],
                    }
                )
                logger.info(f"Created profile for user {user.id}")

            return ProfileResponse(
                id=profile.id,
                userId=profile.userId,
                userName=profile.userName,
                email=profile.email,
                image=profile.image,
                createdAt=profile.createdAt.isoformat(),
                updatedAt=profile.updatedAt.isoformat(),
            )

    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching profile")


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    update_data: ProfileUpdateRequest, user=Depends(verify_session)
):
    """Update user profile"""
    try:
        async with Prisma() as db:
            # Ensure profile exists
            profile = await db.profile.find_unique(where={"userId": user.id})

            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")

            # Prepare update data
            update_fields = {}
            if update_data.userName is not None:
                update_fields["userName"] = update_data.userName
            if update_data.image is not None:
                update_fields["image"] = update_data.image

            if not update_fields:
                # Return existing profile if no updates
                return ProfileResponse(
                    id=profile.id,
                    userId=profile.userId,
                    userName=profile.userName,
                    email=profile.email,
                    image=profile.image,
                    createdAt=profile.createdAt.isoformat(),
                    updatedAt=profile.updatedAt.isoformat(),
                )

            # Update profile
            updated_profile = await db.profile.update(
                where={"userId": user.id}, data=update_fields
            )

            return ProfileResponse(
                id=updated_profile.id,
                userId=updated_profile.userId,
                userName=updated_profile.userName,
                email=updated_profile.email,
                image=updated_profile.image,
                createdAt=updated_profile.createdAt.isoformat(),
                updatedAt=updated_profile.updatedAt.isoformat(),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating profile")


@router.delete("/")
async def delete_profile(user=Depends(verify_session)):
    """Delete user profile and all associated data"""
    try:
        async with Prisma() as db:
            # Check if profile exists
            profile = await db.profile.find_unique(where={"userId": user.id})

            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")

            # Delete all user chats (this will cascade to messages due to schema)
            await db.chat.delete_many(where={"userId": user.id})

            # Delete profile
            await db.profile.delete(where={"userId": user.id})

        return {"message": "Profile and all associated data deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting profile")


@router.get("/stats")
async def get_profile_stats(user=Depends(verify_session)):
    """Get user profile statistics"""
    try:
        async with Prisma() as db:
            profile = await db.profile.find_unique(
                where={"userId": user.id},
                include={"_count": {"select": {"chats": True}}},
            )

            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")

            # Get total messages count
            total_messages = await db.message.count(where={"chat": {"userId": user.id}})

            return {
                "total_chats": profile._count.chats,
                "total_messages": total_messages,
                "profile_created": profile.createdAt.isoformat(),
                "last_updated": profile.updatedAt.isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching profile statistics")
