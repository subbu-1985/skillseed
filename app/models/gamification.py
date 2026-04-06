# Re-export from notification module to avoid circular imports
from app.models.notification import Badge, StudentBadge, Achievement, StudentAchievement

__all__ = ["Badge", "StudentBadge", "Achievement", "StudentAchievement"]
