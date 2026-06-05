from database import get_connection, hash_password

class Session:
    """Stores the currently logged-in user info."""
    user_id = None
    username = None
    role = None

    @classmethod
    def set_user(cls, uid, uname, role):
        cls.user_id = uid
        cls.username = uname
        cls.role = role

    @classmethod
    def clear(cls):
        cls.user_id = None
        cls.username = None
        cls.role = None

    @classmethod
    def is_logged_in(cls):
        return cls.user_id is not None

def login(username, password):
    """Authenticates user credentials. Returns (success, message)."""
    if not username or not password:
        return False, "Username and password are required."
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, role FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        )
        user = cur.fetchone()
        conn.close()

        if user:
            Session.set_user(user[0], user[1], user[2])
            return True, "Login successful."
        return False, "Invalid username or password."
    except Exception as e:
        return False, f"Login error: {e}"

def logout():
    """Clears the session."""
    Session.clear()