import json
from datetime import UTC, datetime
from typing import Annotated

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from redactive.agent_os.secrets import get_secret
from redactive.agent_os.tools.protocol import ToolWithUserIdentity


class GoogleCalendarTool(ToolWithUserIdentity):
    @property
    def name(self) -> str:
        return "google_calendar_tool"
    
    @property
    def description(self) -> str:
        return "Creates an event in the user's google calendar. Authentication is already handled."

    def get_user_signin_redirect(self) -> tuple[str, str]:
        flow = Flow.from_client_config(
            client_config=json.loads(get_secret("google_calendar_api__client_config")),
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            redirect_uri='urn:ietf:wg:oauth:2.0:oob',
        )
        return flow.authorization_url()

    def exchange_signin_code(self, signin_code: str, state: str) -> str:
        flow = Flow.from_client_config(
            client_config=json.loads(get_secret("google_calendar_api__client_config")),
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            redirect_uri='urn:ietf:wg:oauth:2.0:oob',
            state=state,
        )
        flow.fetch_token(code=signin_code)
        return flow.credentials.to_json()

    async def __call__(self, access_token: str, query: Annotated[str, "search query"]) -> str:
        credentials = Credentials.from_authorized_user_info(access_token)
        service = build("calendar", "v3", credentials=credentials)
        now = datetime.now(UTC).isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        
        if not events:
            print("No upcoming events found.")
        print(events)

        return events