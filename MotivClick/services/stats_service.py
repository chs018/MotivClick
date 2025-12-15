"""
Stats Service - Analytics and statistics calculations
"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from collections import defaultdict
from supabase_client import get_supabase
from services.habit_service import get_all_user_habits, calculate_habit_streak


def get_user_overview_stats(user_id: str) -> Dict:
    """
    Get high-level overview statistics for a user.
    
    Args:
        user_id: UUID of the user
    
    Returns:
        dict: Overview statistics
    """
    supabase = get_supabase()
    
    # Count active goals
    goals_response = supabase.table('goals')\
        .select('id', count='exact')\
        .eq('user_id', user_id)\
        .eq('is_archived', False)\
        .execute()
    
    active_goals = goals_response.count if goals_response.count is not None else 0
    
    # Count active habits
    habits_response = supabase.table('habits')\
        .select('id', count='exact')\
        .eq('user_id', user_id)\
        .eq('is_active', True)\
        .execute()
    
    active_habits = habits_response.count if habits_response.count is not None else 0
    
    # Get today's completion stats
    today = date.today().isoformat()
    today_logs = supabase.table('habit_logs')\
        .select('status')\
        .eq('user_id', user_id)\
        .eq('date', today)\
        .execute()
    
    today_completed = len([log for log in (today_logs.data or []) if log['status'] == 'completed'])
    
    # Calculate overall completion rate (last 30 days)
    start_date = (date.today() - timedelta(days=30)).isoformat()
    month_logs = supabase.table('habit_logs')\
        .select('status')\
        .eq('user_id', user_id)\
        .gte('date', start_date)\
        .execute()
    
    total_logs = len(month_logs.data or [])
    completed_logs = len([log for log in (month_logs.data or []) if log['status'] == 'completed'])
    completion_rate = (completed_logs / total_logs * 100) if total_logs > 0 else 0
    
    return {
        'active_goals': active_goals,
        'active_habits': active_habits,
        'today_completed': today_completed,
        'today_total': active_habits,
        'completion_rate_30d': round(completion_rate, 1),
        'total_logs_30d': total_logs
    }


def get_weekly_completion_stats(user_id: str, weeks: int = 4) -> List[Dict]:
    """
    Get weekly completion statistics.
    
    Args:
        user_id: UUID of the user
        weeks: Number of weeks to analyze (default: 4)
    
    Returns:
        list: Weekly stats with week_start, week_end, total, completed, rate
    """
    supabase = get_supabase()
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=weeks * 7)
    
    # Get all logs in the range
    logs_response = supabase.table('habit_logs')\
        .select('date, status')\
        .eq('user_id', user_id)\
        .gte('date', start_date.isoformat())\
        .lte('date', end_date.isoformat())\
        .execute()
    
    logs = logs_response.data or []
    
    # Group logs by week
    weekly_data = defaultdict(lambda: {'total': 0, 'completed': 0})
    
    for log in logs:
        log_date = datetime.fromisoformat(log['date'].replace('Z', '+00:00')).date() \
            if isinstance(log['date'], str) else log['date']
        
        # Calculate week start (Monday)
        week_start = log_date - timedelta(days=log_date.weekday())
        week_key = week_start.isoformat()
        
        weekly_data[week_key]['total'] += 1
        if log['status'] == 'completed':
            weekly_data[week_key]['completed'] += 1
    
    # Format results
    results = []
    for week_start_str, data in sorted(weekly_data.items()):
        week_start = datetime.fromisoformat(week_start_str).date()
        week_end = week_start + timedelta(days=6)
        
        completion_rate = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
        
        results.append({
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'total': data['total'],
            'completed': data['completed'],
            'rate': round(completion_rate, 1)
        })
    
    return results


def get_monthly_completion_stats(user_id: str, months: int = 3) -> List[Dict]:
    """
    Get monthly completion statistics.
    
    Args:
        user_id: UUID of the user
        months: Number of months to analyze (default: 3)
    
    Returns:
        list: Monthly stats with year, month, total, completed, rate
    """
    supabase = get_supabase()
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=months * 31)
    
    # Get all logs in the range
    logs_response = supabase.table('habit_logs')\
        .select('date, status')\
        .eq('user_id', user_id)\
        .gte('date', start_date.isoformat())\
        .lte('date', end_date.isoformat())\
        .execute()
    
    logs = logs_response.data or []
    
    # Group logs by month
    monthly_data = defaultdict(lambda: {'total': 0, 'completed': 0})
    
    for log in logs:
        log_date = datetime.fromisoformat(log['date'].replace('Z', '+00:00')).date() \
            if isinstance(log['date'], str) else log['date']
        
        month_key = f"{log_date.year}-{log_date.month:02d}"
        
        monthly_data[month_key]['total'] += 1
        if log['status'] == 'completed':
            monthly_data[month_key]['completed'] += 1
    
    # Format results
    results = []
    for month_key, data in sorted(monthly_data.items()):
        year, month = map(int, month_key.split('-'))
        
        completion_rate = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
        
        # Get month name
        month_name = datetime(year, month, 1).strftime('%B')
        
        results.append({
            'year': year,
            'month': month,
            'month_name': month_name,
            'total': data['total'],
            'completed': data['completed'],
            'rate': round(completion_rate, 1)
        })
    
    return results


def get_habit_statistics(habit_id: str, user_id: str) -> Dict:
    """
    Get detailed statistics for a specific habit.
    
    Args:
        habit_id: UUID of the habit
        user_id: UUID of the user
    
    Returns:
        dict: Habit statistics including streaks, completion rates, etc.
    """
    supabase = get_supabase()
    
    # Get all logs for this habit
    logs_response = supabase.table('habit_logs')\
        .select('date, status')\
        .eq('habit_id', habit_id)\
        .eq('user_id', user_id)\
        .order('date', desc=True)\
        .execute()
    
    logs = logs_response.data or []
    
    if not logs:
        return {
            'total_logs': 0,
            'completed': 0,
            'skipped': 0,
            'completion_rate': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'last_completed': None
        }
    
    # Calculate basic stats
    total_logs = len(logs)
    completed = len([log for log in logs if log['status'] == 'completed'])
    skipped = len([log for log in logs if log['status'] == 'skipped'])
    completion_rate = (completed / total_logs * 100) if total_logs > 0 else 0
    
    # Calculate current streak
    current_streak = calculate_habit_streak(habit_id, user_id)
    
    # Calculate longest streak
    completed_dates = sorted([
        datetime.fromisoformat(log['date'].replace('Z', '+00:00')).date()
        if isinstance(log['date'], str) else log['date']
        for log in logs if log['status'] == 'completed'
    ])
    
    longest_streak = 0
    current_streak_count = 0
    previous_date = None
    
    for log_date in completed_dates:
        if previous_date is None or log_date == previous_date + timedelta(days=1):
            current_streak_count += 1
            longest_streak = max(longest_streak, current_streak_count)
        else:
            current_streak_count = 1
        previous_date = log_date
    
    # Get last completed date
    last_completed = None
    for log in logs:
        if log['status'] == 'completed':
            last_completed = log['date']
            break
    
    return {
        'total_logs': total_logs,
        'completed': completed,
        'skipped': skipped,
        'completion_rate': round(completion_rate, 1),
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'last_completed': last_completed
    }


def get_all_habits_statistics(user_id: str) -> List[Dict]:
    """
    Get statistics for all user habits.
    
    Args:
        user_id: UUID of the user
    
    Returns:
        list: List of habits with their statistics
    """
    habits = get_all_user_habits(user_id, active_only=True)
    
    results = []
    for habit in habits:
        stats = get_habit_statistics(habit['id'], user_id)
        results.append({
            'habit': habit,
            'stats': stats
        })
    
    return results


def get_recent_activity(user_id: str, days: int = 7) -> List[Dict]:
    """
    Get recent activity for the last N days.
    
    Args:
        user_id: UUID of the user
        days: Number of days to look back (default: 7)
    
    Returns:
        list: Daily activity summaries
    """
    supabase = get_supabase()
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    # Get logs in the range
    logs_response = supabase.table('habit_logs')\
        .select('date, status')\
        .eq('user_id', user_id)\
        .gte('date', start_date.isoformat())\
        .lte('date', end_date.isoformat())\
        .execute()
    
    logs = logs_response.data or []
    
    # Group by date
    daily_data = defaultdict(lambda: {'total': 0, 'completed': 0})
    
    for log in logs:
        log_date = log['date']
        daily_data[log_date]['total'] += 1
        if log['status'] == 'completed':
            daily_data[log_date]['completed'] += 1
    
    # Create result for each day
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.isoformat()
        data = daily_data.get(date_str, {'total': 0, 'completed': 0})
        
        completion_rate = (data['completed'] / data['total'] * 100) if data['total'] > 0 else 0
        
        results.append({
            'date': date_str,
            'day_name': current_date.strftime('%A'),
            'total': data['total'],
            'completed': data['completed'],
            'rate': round(completion_rate, 1)
        })
        
        current_date += timedelta(days=1)
    
    return results
