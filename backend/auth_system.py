"""
Authentication and Authorization System
Implements JWT-based authentication with role-based access control
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

@dataclass
class User:
    user_id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: str = ""
    last_login: str = ""
    permissions: List[str] = None

class AuthenticationService:
    """Handles user authentication and JWT token management"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
        
        # In-memory user store (in production, use a database)
        self.users = {
            "admin": User(
                user_id="admin_001",
                username="admin",
                email="admin@startup-evaluator.com",
                role=UserRole.ADMIN,
                created_at=datetime.now().isoformat(),
                permissions=["read", "write", "delete", "admin"]
            ),
            "analyst": User(
                user_id="analyst_001",
                username="analyst",
                email="analyst@startup-evaluator.com",
                role=UserRole.ANALYST,
                created_at=datetime.now().isoformat(),
                permissions=["read", "write"]
            ),
            "viewer": User(
                user_id="viewer_001",
                username="viewer",
                email="viewer@startup-evaluator.com",
                role=UserRole.VIEWER,
                created_at=datetime.now().isoformat(),
                permissions=["read"]
            )
        }
        
        # Password hashes (in production, use proper password hashing)
        self.password_hashes = {
            "admin": self._hash_password("admin123"),
            "analyst": self._hash_password("analyst123"),
            "viewer": self._hash_password("viewer123")
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            if username not in self.users:
                logger.warning(f"Authentication failed: User {username} not found")
                return None
            
            user = self.users[username]
            if not user.is_active:
                logger.warning(f"Authentication failed: User {username} is inactive")
                return None
            
            password_hash = self.password_hashes.get(username)
            if not password_hash or password_hash != self._hash_password(password):
                logger.warning(f"Authentication failed: Invalid password for user {username}")
                return None
            
            # Update last login
            user.last_login = datetime.now().isoformat()
            
            logger.info(f"User {username} authenticated successfully")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for authenticated user"""
        try:
            payload = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "permissions": user.permissions,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Token generated for user {user.username}")
            return token
            
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if user still exists and is active
            username = payload.get("username")
            if username not in self.users:
                logger.warning(f"Token verification failed: User {username} not found")
                return None
            
            user = self.users[username]
            if not user.is_active:
                logger.warning(f"Token verification failed: User {username} is inactive")
                return None
            
            logger.info(f"Token verified for user {username}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token verification failed: Invalid token")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            username = payload.get("username")
            user = self.users[username]
            
            return self.generate_token(user)
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None

class AuthorizationService:
    """Handles role-based access control and permissions"""
    
    def __init__(self):
        self.role_permissions = {
            UserRole.ADMIN: ["read", "write", "delete", "admin"],
            UserRole.ANALYST: ["read", "write"],
            UserRole.VIEWER: ["read"],
            UserRole.GUEST: []
        }
    
    def has_permission(self, user_role: UserRole, required_permission: str) -> bool:
        """Check if user role has required permission"""
        permissions = self.role_permissions.get(user_role, [])
        return required_permission in permissions
    
    def can_access_endpoint(self, user_role: UserRole, endpoint: str) -> bool:
        """Check if user can access specific endpoint"""
        endpoint_permissions = {
            "/evaluate": "write",
            "/health": "read",
            "/metrics/framework": "read",
            "/admin/users": "admin",
            "/admin/analytics": "admin",
            "/reports": "read"
        }
        
        required_permission = endpoint_permissions.get(endpoint, "read")
        return self.has_permission(user_role, required_permission)
    
    def get_user_permissions(self, user_role: UserRole) -> List[str]:
        """Get all permissions for user role"""
        return self.role_permissions.get(user_role, [])

class SecurityMiddleware:
    """Middleware for handling authentication and authorization"""
    
    def __init__(self, auth_service: AuthenticationService, authz_service: AuthorizationService):
        self.auth_service = auth_service
        self.authz_service = authz_service
    
    def extract_token_from_header(self, authorization_header: str) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        if not authorization_header:
            return None
        
        try:
            scheme, token = authorization_header.split(" ", 1)
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
    
    def authenticate_request(self, authorization_header: str) -> Optional[Dict[str, Any]]:
        """Authenticate request using JWT token"""
        token = self.extract_token_from_header(authorization_header)
        if not token:
            return None
        
        return self.auth_service.verify_token(token)
    
    def authorize_request(self, user_payload: Dict[str, Any], endpoint: str) -> bool:
        """Authorize request based on user role and endpoint"""
        if not user_payload:
            return False
        
        user_role = UserRole(user_payload.get("role", "guest"))
        return self.authz_service.can_access_endpoint(user_role, endpoint)
    
    def get_user_info(self, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get user information from JWT payload"""
        if not user_payload:
            return {}
        
        return {
            "user_id": user_payload.get("user_id"),
            "username": user_payload.get("username"),
            "email": user_payload.get("email"),
            "role": user_payload.get("role"),
            "permissions": user_payload.get("permissions", [])
        }

# Global instances
auth_service = AuthenticationService()
authz_service = AuthorizationService()
security_middleware = SecurityMiddleware(auth_service, authz_service)
