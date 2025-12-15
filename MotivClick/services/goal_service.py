"""
Goal Service - Handles all goal-related operations with Supabase
"""
from typing import List, Dict, Optional
from datetime import datetime, date
from supabase_client import get_supabase


def create_goal(
    user_id: str,
    title: str,
    description: str = "",
    target_type: str = "daily",
    start_date: str = None,
    target_date: str = None
) -> Dict:
    """
    Create a new goal for a user.
    
    Args:
        user_id: UUID of the user
        title: Goal title
        description: Goal description
        target_type: 'daily', 'weekly', or 'once'
        start_date: ISO format date string (YYYY-MM-DD)
        target_date: ISO format date string (YYYY-MM-DD), optional
    
    Returns:
        dict: The created goal record
    """
    supabase = get_supabase()
    
    if not start_date:
        start_date = date.today().isoformat()
    
    goal_data = {
        'user_id': user_id,
        'title': title,
        'description': description,
        'target_type': target_type,
        'start_date': start_date,
        'is_archived': False
    }
    
    if target_date:
        goal_data['target_date'] = target_date
    
    response = supabase.table('goals').insert(goal_data).execute()
    return response.data[0] if response.data else None


def get_user_goals(user_id: str, include_archived: bool = False) -> List[Dict]:
    """
    Get all goals for a user.
    
    Args:
        user_id: UUID of the user
        include_archived: Whether to include archived goals
    
    Returns:
        list: List of goal records
    """
    supabase = get_supabase()
    
    query = supabase.table('goals').select('*').eq('user_id', user_id)
    
    if not include_archived:
        query = query.eq('is_archived', False)
    
    response = query.order('created_at', desc=True).execute()
    return response.data if response.data else []


def get_goal_by_id(goal_id: str, user_id: str) -> Optional[Dict]:
    """
    Get a specific goal by ID (with user verification).
    
    Args:
        goal_id: UUID of the goal
        user_id: UUID of the user (for security)
    
    Returns:
        dict: Goal record or None
    """
    supabase = get_supabase()
    
    response = supabase.table('goals')\
        .select('*')\
        .eq('id', goal_id)\
        .eq('user_id', user_id)\
        .execute()
    
    return response.data[0] if response.data else None


def update_goal(
    goal_id: str,
    user_id: str,
    title: str = None,
    description: str = None,
    target_type: str = None,
    start_date: str = None,
    target_date: str = None,
    is_archived: bool = None
) -> Optional[Dict]:
    """
    Update a goal.
    
    Args:
        goal_id: UUID of the goal
        user_id: UUID of the user (for security)
        title: New title (optional)
        description: New description (optional)
        target_type: New target type (optional)
        start_date: New start date (optional)
        target_date: New target date (optional)
        is_archived: Archive status (optional)
    
    Returns:
        dict: Updated goal record or None
    """
    supabase = get_supabase()
    
    # Build update data with only provided fields
    update_data = {}
    if title is not None:
        update_data['title'] = title
    if description is not None:
        update_data['description'] = description
    if target_type is not None:
        update_data['target_type'] = target_type
    if start_date is not None:
        update_data['start_date'] = start_date
    if target_date is not None:
        update_data['target_date'] = target_date
    if is_archived is not None:
        update_data['is_archived'] = is_archived
    
    if not update_data:
        return None
    
    response = supabase.table('goals')\
        .update(update_data)\
        .eq('id', goal_id)\
        .eq('user_id', user_id)\
        .execute()
    
    return response.data[0] if response.data else None


def archive_goal(goal_id: str, user_id: str) -> bool:
    """
    Archive a goal (soft delete).
    
    Args:
        goal_id: UUID of the goal
        user_id: UUID of the user
    
    Returns:
        bool: True if successful
    """
    result = update_goal(goal_id, user_id, is_archived=True)
    return result is not None


def delete_goal(goal_id: str, user_id: str) -> bool:
    """
    Permanently delete a goal (and associated habits/logs via CASCADE).
    
    Args:
        goal_id: UUID of the goal
        user_id: UUID of the user
    
    Returns:
        bool: True if successful
    """
    supabase = get_supabase()
    
    response = supabase.table('goals')\
        .delete()\
        .eq('id', goal_id)\
        .eq('user_id', user_id)\
        .execute()
    
    return response.data is not None


def get_active_goals_count(user_id: str) -> int:
    """
    Get count of active (non-archived) goals for a user.
    
    Args:
        user_id: UUID of the user
    
    Returns:
        int: Number of active goals
    """
    supabase = get_supabase()
    
    response = supabase.table('goals')\
        .select('id', count='exact')\
        .eq('user_id', user_id)\
        .eq('is_archived', False)\
        .execute()
    
    return response.count if response.count is not None else 0


def get_goals_with_habits(user_id: str) -> List[Dict]:
    """
    Get all goals with their associated habits.
    
    Args:
        user_id: UUID of the user
    
    Returns:
        list: Goals with nested habits data
    """
    # First get all goals
    goals = get_user_goals(user_id, include_archived=False)
    
    # Import habit service to avoid circular import
    from services.habit_service import get_habits_for_goal
    
    # Attach habits to each goal
    for goal in goals:
        goal['habits'] = get_habits_for_goal(goal['id'], user_id)
    
    return goals
