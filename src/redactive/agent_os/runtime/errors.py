class AgentOSError(BaseException):
    pass

class RestrictedToolUsage(AgentOSError):
    pass

class RestrictedToolInput(RestrictedToolUsage):
    pass

class RestrictedToolOutput(RestrictedToolUsage):
    pass