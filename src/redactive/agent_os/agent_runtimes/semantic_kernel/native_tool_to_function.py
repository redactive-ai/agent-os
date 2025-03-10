from semantic_kernel.functions import kernel_function

from redactive.agent_os.agent_runtimes.errors import UserIdentityNotSupportedForTool
from redactive.agent_os.native_tools.protocol import Tool, ToolWithUserIdentity
from redactive.agent_os.spec.agent import Capability


def convert_native_tool_to_kernel_function(tool: Tool, capability: Capability):
    kernel_func = kernel_function(func=tool, name=tool.name, description=tool.description)

    parameters = getattr(kernel_func, "__kernel_function_parameters__")
    
    if capability.user_identity:
        if not isinstance(tool, ToolWithUserIdentity):
            raise UserIdentityNotSupportedForTool()
        
        parameters = [p for p in parameters if p["name"] != "access_token"]

    setattr(kernel_func, "__kernel_function_parameters__", parameters)
    print(kernel_func.__dict__)
    return kernel_func