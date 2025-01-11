class CredentialsStore:
    def __init__(self):
        self._creds = {}

    def has_user_creds(self, tool_name: str, user_id: str) -> bool:
        return f"u:{user_id}:{tool_name}" in self._creds
    
    def get_user_creds(self, tool_name: str, user_id: str) -> str:
        return self._creds[f"u:{user_id}:{tool_name}"]
    
    def update_user_creds(self, tool_name: str, user_id: str, creds: str) -> None:
        self._creds[f"u:{user_id}:{tool_name}"] = creds

    def pop_signin_state(self, tool_name: str, user_id: str) -> str:
        return self._creds.pop(f"signin_state:{tool_name}:{user_id}")
    
    def set_sigin_state(self, tool_name: str, user_id: str, state: str) -> None:
        self._creds[f"signin_state:{tool_name}:{user_id}"] = state

    def has_static_creds(self, tool_name: str, static_id: str) -> bool:
        return f"s:{tool_name}:{static_id}" in self._creds
    
    def get_static_creds(self, tool_name: str, static_id: str) -> str:
        return self._creds[f"s:{tool_name}:{static_id}"]
    
    def update_static_creds(self, tool_name: str, static_id: str, creds: str) -> None:
        self._creds[f"s:{tool_name}:{static_id}"] = creds