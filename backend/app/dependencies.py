"""
FastAPI 依赖注入模块
"""

from fastapi import Header, HTTPException, status

WORKSPACE_HEADER = "X-Workspace"


async def get_workspace(x_workspace: str = Header(default="default")) -> str:
    """从 X-Workspace 请求头中提取工作区名称。

    工作区用于隔离不同用户/团队的数据。
    未提供时默认使用 'default' 工作区。
    """
    workspace = x_workspace.strip() if x_workspace else "default"
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Workspace 请求头不能为空",
        )
    if len(workspace) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工作区名称不能超过 100 个字符",
        )
    if not _is_valid_workspace_name(workspace):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工作区名称只能包含字母、数字、中划线、下划线和中文",
        )
    return workspace


def _is_valid_workspace_name(name: str) -> bool:
    import re
    return bool(re.match(r'^[\w一-鿿-]+$', name))
