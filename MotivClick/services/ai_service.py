"""
AI Service - Google Gemini integration for motivational content generation
"""
import os
from typing import List, Dict, Optional
import google.generativeai as genai
from config import Config

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)


def call_gemini(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Call Google Gemini API with the given prompt.
    
    Args:
        prompt: The text prompt to send to Gemini
        model_name: The Gemini model to use (default: gemini-1.5-flash)
    
    Returns:
        str: The generated text response
    
    Raises:
        Exception: If API call fails
    """
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        # Return the text content from the response
        if response and response.text:
            return response.text
        else:
            return "I'm here to support you! Keep pushing forward with your goals."
            
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        # Return a fallback motivational message if API fails
        return "Stay focused on your goals! Every small step counts toward your success."


def generate_daily_motivation(
    user_name: str,
    goals: List[Dict],
    recent_logs: List[Dict]
) -> Dict[str, any]:
    """
    Generate daily motivational content based on user's goals and progress.
    
    Args:
        user_name: User's display name or email
        goals: List of user's active goals (with title and description)
        recent_logs: List of recent habit completion logs (last 7 days)
    
    Returns:
        dict: Contains 'summary', 'suggestions' (list), and 'motivation' (string)
    """
    # Build progress summary
    total_logs = len(recent_logs)
    completed_logs = len([log for log in recent_logs if log.get('status') == 'completed'])
    completion_rate = (completed_logs / total_logs * 100) if total_logs > 0 else 0
    
    # Build goals summary
    goals_text = "\n".join([f"- {goal.get('title', 'Untitled Goal')}: {goal.get('description', 'No description')}" 
                            for goal in goals[:5]])  # Limit to 5 goals
    
    if not goals_text:
        goals_text = "No active goals set yet."
    
    # Create comprehensive prompt for Gemini
    prompt = f"""You are a supportive personal coach helping {user_name} achieve their goals.

Current Goals:
{goals_text}

Recent Progress (Last 7 Days):
- Total habit actions tracked: {total_logs}
- Completed actions: {completed_logs}
- Completion rate: {completion_rate:.1f}%

Based on this information, please provide:

1. Three specific, actionable suggestions to help improve their progress (be practical and encouraging)
2. One short motivational message (2-3 sentences) to inspire them for today

Format your response as follows:
SUGGESTIONS:
1. [First suggestion]
2. [Second suggestion]
3. [Third suggestion]

MOTIVATION:
[Your motivational message here]

Keep the tone positive, supportive, and personalized to their specific goals."""

    try:
        # Call Gemini API
        response_text = call_gemini(prompt)
        
        # Parse the response
        suggestions = []
        motivation = ""
        
        # Split response into sections
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'SUGGESTIONS:' in line.upper():
                current_section = 'suggestions'
                continue
            elif 'MOTIVATION:' in line.upper():
                current_section = 'motivation'
                continue
            
            if current_section == 'suggestions':
                # Extract numbered suggestions
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and bullet points
                    suggestion = line.lstrip('0123456789.-) ').strip()
                    if suggestion:
                        suggestions.append(suggestion)
            elif current_section == 'motivation':
                motivation += line + " "
        
        # Clean up motivation text
        motivation = motivation.strip()
        
        # Fallback if parsing fails
        if not suggestions:
            suggestions = [
                "Focus on one habit at a time and build consistency.",
                "Celebrate small wins - every completed task matters!",
                "Review your goals daily to stay aligned with your vision."
            ]
        
        if not motivation:
            motivation = f"Great work, {user_name}! Keep building momentum one day at a time. Your consistency is your superpower!"
        
        return {
            'summary': f"Completion rate: {completion_rate:.1f}% over the last 7 days",
            'suggestions': suggestions,
            'motivation': motivation,
            'raw_response': response_text
        }
        
    except Exception as e:
        print(f"Error generating motivation: {str(e)}")
        # Return fallback content
        return {
            'summary': f"Completion rate: {completion_rate:.1f}% over the last 7 days",
            'suggestions': [
                "Stay consistent with your daily habits.",
                "Break down large goals into smaller, manageable tasks.",
                "Reflect on your progress weekly to adjust your approach."
            ],
            'motivation': f"Keep going, {user_name}! Every step forward is progress. You've got this!",
            'raw_response': None
        }


def generate_goal_specific_tips(goal_title: str, goal_description: str) -> List[str]:
    """
    Generate specific tips for achieving a particular goal.
    
    Args:
        goal_title: The title of the goal
        goal_description: Description of the goal
    
    Returns:
        list: 3-5 actionable tips for achieving the goal
    """
    prompt = f"""As a personal development coach, provide 5 specific, actionable tips for achieving this goal:

Goal: {goal_title}
Description: {goal_description}

Provide 5 clear, practical tips. Format each tip as a single sentence starting with an action verb.

Tips:
1. [First tip]
2. [Second tip]
3. [Third tip]
4. [Fourth tip]
5. [Fifth tip]"""

    try:
        response_text = call_gemini(prompt)
        
        # Parse numbered tips
        tips = []
        for line in response_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                tip = line.lstrip('0123456789.-) ').strip()
                if tip:
                    tips.append(tip)
        
        return tips[:5] if tips else [
            "Break this goal into smaller milestones.",
            "Set specific daily or weekly actions.",
            "Track your progress regularly.",
            "Seek accountability from friends or community.",
            "Adjust your approach based on what works."
        ]
        
    except Exception as e:
        print(f"Error generating goal tips: {str(e)}")
        return [
            "Start with small, consistent actions.",
            "Create a detailed action plan.",
            "Review and adjust weekly."
        ]
