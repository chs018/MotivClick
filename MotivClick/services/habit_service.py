"""
Habit Service - Handles all habit-related operations with Supabase
"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from supabase_client import get_supabase


def create_habit(
    user_id: str,
    goal_id: str,
    name: str,
    frequency: str = "daily"
) -> Dict:
    """
    Create a new habit linked to a goal.
    
    Args:
        user_id: UUID of the user
        goal_id: UUID of the goal this habit belongs to
        name: Habit name
        frequency: 'daily' or 'weekly'
    
    Returns:
        dict: The created habit record
    """
    supabase = get_supabase()
    
    habit_data = {
        'user_id': user_id,
        'goal_id': goal_id,
        'name': name,
        'frequency': frequency,
        'is_active': True
    }
    
    response = supabase.table('habits').insert(habit_data).execute()
    return response.data[0] if response.data else None


def get_habits_for_goal(goal_id: str, user_id: str) -> List[Dict]:
    """
    Get all habits for a specific goal.
    
    Args:
        goal_id: UUID of the goal
        user_id: UUID of the user (for security)
    
    Returns:
        list: List of habit records
    """
    supabase = get_supabase()
    
    response = supabase.table('habits')\
        .select('*')\
        .eq('goal_id', goal_id)\
        .eq('user_id', user_id)\
        .eq('is_active', True)\
        .order('created_at', desc=False)\
        .execute()
    
    return response.data if response.data else []


def get_all_user_habits(user_id: str, active_only: bool = True) -> List[Dict]:
    """
    Get all habits for a user across all goals.
    
    Args:
        user_id: UUID of the user
        active_only: Whether to only return active habits
    
    Returns:
        list: List of habit records
    """
    supabase = get_supabase()
    
    query = supabase.table('habits').select('*').eq('user_id', user_id)
    
    if active_only:
        query = query.eq('is_active', True)
    
    response = query.order('created_at', desc=False).execute()
    return response.data if response.data else []


def get_habit_by_id(habit_id: str, user_id: str) -> Optional[Dict]:
    """
    Get a specific habit by ID.
    
    Args:
        habit_id: UUID of the habit
        user_id: UUID of the user (for security)
    
    Returns:
        dict: Habit record or None
    """
    supabase = get_supabase()
    
    response = supabase.table('habits')\
        .select('*')\
        .eq('id', habit_id)\
        .eq('user_id', user_id)\
        .execute()
    
    return response.data[0] if response.data else None


def update_habit(
    habit_id: str,
    user_id: str,
    name: str = None,
    frequency: str = None,
    is_active: bool = None
) -> Optional[Dict]:
    """
    Update a habit.
    
    Args:
        habit_id: UUID of the habit
        user_id: UUID of the user
        name: New name (optional)
        frequency: New frequency (optional)
        is_active: Active status (optional)
    
    Returns:
        dict: Updated habit record or None
    """
    supabase = get_supabase()
    
    update_data = {}
    if name is not None:
        update_data['name'] = name
    if frequency is not None:
        update_data['frequency'] = frequency
    if is_active is not None:
        update_data['is_active'] = is_active
    
    if not update_data:
        return None
    
    response = supabase.table('habits')\
        .update(update_data)\
        .eq('id', habit_id)\
        .eq('user_id', user_id)\
        .execute()
    
    return response.data[0] if response.data else None


def delete_habit(habit_id: str, user_id: str) -> bool:
    """
    Delete a habit (and associated logs via CASCADE).
    
    Args:
        habit_id: UUID of the habit
        user_id: UUID of the user
    
    Returns:
        bool: True if successful
    """
    supabase = get_supabase()
    
    response = supabase.table('habits')\
        .delete()\
        .eq('id', habit_id)\
        .eq('user_id', user_id)\
        .execute()
    
    return response.data is not None


def log_habit_completion(
    habit_id: str,
    user_id: str,
    log_date: str,
    status: str = "completed"
) -> Dict:
    """
    Log a habit completion for a specific date.
    Uses upsert to handle duplicate entries.
    
    Args:
        habit_id: UUID of the habit
        user_id: UUID of the user
        log_date: ISO format date string (YYYY-MM-DD)
        status: 'completed' or 'skipped'
    
    Returns:
        dict: The created/updated habit log record
    """
    supabase = get_supabase()
    
    log_data = {
        'habit_id': habit_id,
        'user_id': user_id,
        'date': log_date,
        'status': status
    }
    
    # Use upsert to handle unique constraint (habit_id, date)
    response = supabase.table('habit_logs')\
        .upsert(log_data, on_conflict='habit_id,date')\
        .execute()
    
    return response.data[0] if response.data else None


def get_habit_logs(
    habit_id: str,
    user_id: str,
    start_date: str = None,
    end_date: str = None
) -> List[Dict]:
    """
    Get habit logs for a specific habit within a date range.
    
    Args:
        habit_id: UUID of the habit
        user_id: UUID of the user
        start_date: ISO format date string (optional)
        end_date: ISO format date string (optional)
    
    Returns:
        list: List of habit log records
    """
    supabase = get_supabase()
    
    query = supabase.table('habit_logs')\
        .select('*')\
        .eq('habit_id', habit_id)\
        .eq('user_id', user_id)
    
    if start_date:
        query = query.gte('date', start_date)
    if end_date:
        query = query.lte('date', end_date)
    
    response = query.order('date', desc=True).execute()
    return response.data if response.data else []


def get_user_logs_by_date_range(
    user_id: str,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Get all habit logs for a user within a date range.
    
    Args:
        user_id: UUID of the user
        start_date: ISO format date string
        end_date: ISO format date string
    
    Returns:
        list: List of habit log records
    """
    supabase = get_supabase()
    
    response = supabase.table('habit_logs')\
        .select('*')\
        .eq('user_id', user_id)\
        .gte('date', start_date)\
        .lte('date', end_date)\
        .order('date', desc=True)\
        .execute()
    
    return response.data if response.data else []


def get_today_habit_status(user_id: str) -> Dict[str, str]:
    """
    Get today's completion status for all user habits.
    
    Args:
        user_id: UUID of the user
    
    Returns:
        dict: Map of habit_id -> status ('completed', 'skipped', or None)
    """
    today = date.today().isoformat()
    
    supabase = get_supabase()
    
    response = supabase.table('habit_logs')\
        .select('habit_id, status')\
        .eq('user_id', user_id)\
        .eq('date', today)\
        .execute()
    
    # Convert to dictionary
    status_map = {}
    if response.data:
        for log in response.data:
            status_map[log['habit_id']] = log['status']
    
    return status_map


def calculate_habit_streak(habit_id: str, user_id: str) -> int:
    """
    Calculate the current streak for a habit (consecutive days completed).
    
    Args:
        habit_id: UUID of the habit
        user_id: UUID of the user
    
    Returns:
        int: Current streak count
    """
    # Get logs for the last 60 days (sufficient for most streaks)
    end_date = date.today()
    start_date = end_date - timedelta(days=60)
    
    logs = get_habit_logs(
        habit_id,
        user_id,
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    if not logs:
        return 0
    
    # Create a set of completed dates
    completed_dates = set()
    for log in logs:
        if log['status'] == 'completed':
            log_date = datetime.fromisoformat(log['date'].replace('Z', '+00:00')).date() \
                if isinstance(log['date'], str) else log['date']
            completed_dates.add(log_date)
    
    # Count consecutive days from today backwards
    streak = 0
    current_date = date.today()
    
    while current_date in completed_dates:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak


def get_habits_with_streaks(user_id: str) -> List[Dict]:
    """
    Get all active habits with their current streaks and today's status.
    
    Args:
        user_id: UUID of the user
    
    Returns:
        list: Habits with added 'streak' and 'today_status' fields
    """
    habits = get_all_user_habits(user_id, active_only=True)
    today_status = get_today_habit_status(user_id)
    
    for habit in habits:
        habit['streak'] = calculate_habit_streak(habit['id'], user_id)
        habit['today_status'] = today_status.get(habit['id'])
    
    return habits
