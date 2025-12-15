from supabase import create_client, Client
from config import Config

# Global Supabase client instance
_supabase_client: Client = None


def get_supabase() -> Client:
    """
    Get or create the Supabase client instance.
    This ensures we reuse the same client throughout the application.
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = create_client(
            supabase_url=Config.SUPABASE_URL,
            supabase_key=Config.SUPABASE_KEY
        )
    
    return _supabase_client


def init_supabase():
    """
    Initialize and validate Supabase connection.
    Call this at application startup.
    """
    try:
        client = get_supabase()
        # Test the connection by attempting a simple query
        # This will raise an exception if credentials are invalid
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Supabase client: {str(e)}")
