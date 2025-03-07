class AgentOSError(BaseException):
    pass

class ToolInvocationError(AgentOSError):
    pass

class MissingStaticCredential(ToolInvocationError):
    pass

class RestrictedToolUsage(ToolInvocationError):
    pass

class RestrictedToolInput(RestrictedToolUsage):
    pass

class RestrictedToolOutput(RestrictedToolUsage):
    pass

class AgentDefinitionError(AgentOSError):
    pass

class UserIdentityNotSupportedForTool(AgentDefinitionError):
    pass

class EngagementShortCircuited(AgentOSError):
    pass