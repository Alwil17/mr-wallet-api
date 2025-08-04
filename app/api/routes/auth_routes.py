import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.schemas.user_dto import (
    UserCreateDTO,
    UserResponse,
    UserUpdateDTO,
    UserExportData,
    AccountDeletionRequest,
)
from app.schemas.auth_dto import TokenResponse, RefreshTokenRequest
from app.services.user_service import UserService
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.core.security import (
    get_current_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from app.db.base import get_db
from sqlalchemy.orm import Session
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Constants
USER_NOT_FOUND = "User not found"


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate user and return access and refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data
        db (Session): Database session

    Returns:
        TokenResponse: Access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}, expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token(user.id, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    Args:
        token_data (RefreshTokenRequest): The refresh token
        db (Session): Database session

    Returns:
        TokenResponse: New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify refresh token
    user_id = verify_refresh_token(token_data.refresh_token, db)
    
    # Get user
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=USER_NOT_FOUND,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Revoke old refresh token
    token_repo = RefreshTokenRepository(db)
    token_repo.revoke(token_data.refresh_token)

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}, expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(user.id, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout", status_code=204)
async def logout(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Logout user by revoking refresh token.

    Args:
        token_data (RefreshTokenRequest): The refresh token to revoke
        db (Session): Database session

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify and revoke refresh token
    verify_refresh_token(token_data.refresh_token, db)
    token_repo = RefreshTokenRepository(db)
    token_repo.revoke(token_data.refresh_token)


@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(user_data: UserCreateDTO, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data (UserCreateDTO): The user registration data
        db (Session): Database session

    Returns:
        UserResponse: The created user

    Raises:
        HTTPException: If user already exists
    """
    user_service = UserService(db)
    try:
        # For testing environments, allow creation of admins by email
        if (settings.APP_ENV.lower() == "testing") and "admin" in user_data.email:
            user_data.role = "admin"
        else:
            user_data.role = "user"  # Default role for normal users

        user = user_service.create_user(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Args:
        current_user (UserResponse): The current user from token

    Returns:
        UserResponse: Current user information
    """
    return current_user


@router.put("/edit", response_model=UserResponse)
async def edit_current_user(
    update_data: UserUpdateDTO,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Update current user information.

    Args:
        update_data (UserUpdateDTO): The update data
        db (Session): Database session
        current_user (UserResponse): The current user from token

    Returns:
        UserResponse: Updated user information

    Raises:
        HTTPException: If update fails
    """
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(updated_user)


@router.delete("/remove", status_code=204)
async def remove_current_user(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Delete current user account.

    Args:
        db (Session): Database session
        current_user (UserResponse): The current user from token

    Raises:
        HTTPException: If deletion fails
    """
    user_service = UserService(db)
    success = user_service.delete_user(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND
        )


@router.get("/export-data", response_model=UserExportData)
async def export_user_data(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export all user data for GDPR compliance.

    Args:
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        UserExportData: All user data

    Raises:
        HTTPException: If export fails
    """
    user_service = UserService(db)
    try:
        export_data = user_service.export_user_data(current_user.id)
        return export_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/export-data/download")
async def download_user_data(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Download user data as JSON file.

    Args:
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        JSON file with user data

    Raises:
        HTTPException: If export fails
    """
    from fastapi.responses import JSONResponse
    
    user_service = UserService(db)
    try:
        export_data = user_service.export_user_data(current_user.id)
        
        # Convert to dict for JSON response
        data_dict = export_data.model_dump()
        
        return JSONResponse(
            content=data_dict,
            headers={
                "Content-Disposition": f"attachment; filename=user_data_{current_user.id}.json"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/delete-account")
async def delete_user_account(
    deletion_request: AccountDeletionRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Permanently delete user account and all data.

    Args:
        deletion_request (AccountDeletionRequest): Deletion confirmation
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If deletion fails
    """
    user_service = UserService(db)
    try:
        result = user_service.delete_user_account(current_user.id, deletion_request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/anonymize-account")
async def anonymize_user_account(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Anonymize user account data.

    Args:
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If anonymization fails
    """
    user_service = UserService(db)
    try:
        result = user_service.anonymize_user_data(current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/data-summary")
async def get_user_data_summary(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a summary of user's data.

    Args:
        current_user (UserResponse): The current user from token
        db (Session): Database session

    Returns:
        dict: Data summary
    """
    user_service = UserService(db)
    
    # TODO: Implement actual data counting when other models are available
    # For now, return basic summary
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "account_created": current_user.created_at,
        "wallets_count": 0,  # TODO: Count actual wallets
        "transactions_count": 0,  # TODO: Count actual transactions
        "debts_count": 0,  # TODO: Count actual debts
        "transfers_count": 0,  # TODO: Count actual transfers
        "data_summary_generated_at": datetime.now()
    }
