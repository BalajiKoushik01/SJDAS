from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.routers.auth import User, require_roles, verify_token

router = APIRouter(prefix="/premium", tags=["Premium B2B"])


class OrganizationUser(BaseModel):
    id: str
    username: str
    role: Literal["owner", "admin", "designer", "operator", "viewer"]
    active: bool = True


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    role: Literal["owner", "admin", "designer", "operator", "viewer"]


class ApprovalRequest(BaseModel):
    design_id: str
    requested_by: str
    notes: Optional[str] = None


class ApprovalDecision(BaseModel):
    decision: Literal["approved", "rejected"]
    reviewer: str
    notes: Optional[str] = None


class DesignComment(BaseModel):
    design_id: str
    author: str
    message: str = Field(min_length=1, max_length=1000)


class DesignSnapshotRequest(BaseModel):
    design_id: str
    tag: str = Field(min_length=1, max_length=100)
    created_by: str
    metadata: Dict[str, str] = Field(default_factory=dict)


ORG_USERS: List[OrganizationUser] = [
    OrganizationUser(id="usr_admin", username="admin", role="admin"),
]
APPROVALS: Dict[str, Dict[str, str]] = {}
COMMENTS: Dict[str, List[Dict[str, str]]] = {}
SNAPSHOTS: Dict[str, List[Dict[str, str]]] = {}
AUDIT_LOG: List[Dict[str, str]] = []


def _audit(event_type: str, actor: str, subject: str, details: str) -> None:
    AUDIT_LOG.append(
        {
            "id": str(uuid4()),
            "event_type": event_type,
            "actor": actor,
            "subject": subject,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.get("/users", response_model=List[OrganizationUser])
async def list_users(current_user: User = Depends(require_roles(["admin", "owner"]))):
    return ORG_USERS


@router.post("/users", response_model=OrganizationUser)
async def create_user(
    payload: CreateUserRequest, current_user: User = Depends(require_roles(["admin", "owner"]))
):
    new_user = OrganizationUser(id=f"usr_{uuid4().hex[:8]}", username=payload.username, role=payload.role)
    ORG_USERS.append(new_user)
    _audit("user.created", current_user.username, new_user.id, f"role={payload.role}")
    return new_user


@router.post("/approvals/request")
async def request_approval(
    payload: ApprovalRequest, current_user: User = Depends(verify_token)
):
    approval_id = f"apr_{uuid4().hex[:10]}"
    APPROVALS[approval_id] = {
        "id": approval_id,
        "design_id": payload.design_id,
        "status": "pending",
        "requested_by": payload.requested_by,
        "notes": payload.notes or "",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _audit("approval.requested", current_user.username, payload.design_id, f"approval_id={approval_id}")
    return APPROVALS[approval_id]


@router.post("/approvals/{approval_id}/decision")
async def decide_approval(
    approval_id: str,
    payload: ApprovalDecision,
    current_user: User = Depends(require_roles(["admin", "owner", "operator"])),
):
    approval = APPROVALS.get(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    approval["status"] = payload.decision
    approval["reviewer"] = payload.reviewer
    approval["notes"] = payload.notes or approval.get("notes", "")
    approval["updated_at"] = datetime.now(timezone.utc).isoformat()
    _audit("approval.decided", current_user.username, approval["design_id"], payload.decision)
    return approval


@router.post("/comments")
async def add_comment(payload: DesignComment, current_user: User = Depends(verify_token)):
    row = {
        "id": f"cmt_{uuid4().hex[:10]}",
        "author": payload.author,
        "message": payload.message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    COMMENTS.setdefault(payload.design_id, []).append(row)
    _audit("comment.added", current_user.username, payload.design_id, row["id"])
    return row


@router.get("/comments/{design_id}")
async def list_comments(design_id: str, current_user: User = Depends(verify_token)):
    return {"design_id": design_id, "comments": COMMENTS.get(design_id, [])}


@router.post("/snapshots")
async def create_snapshot(
    payload: DesignSnapshotRequest, current_user: User = Depends(require_roles(["admin", "owner", "designer"]))
):
    snapshot = {
        "id": f"snp_{uuid4().hex[:10]}",
        "tag": payload.tag,
        "created_by": payload.created_by,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": payload.metadata,
    }
    SNAPSHOTS.setdefault(payload.design_id, []).append(snapshot)
    _audit("snapshot.created", current_user.username, payload.design_id, payload.tag)
    return snapshot


@router.get("/snapshots/{design_id}")
async def list_snapshots(design_id: str, current_user: User = Depends(verify_token)):
    return {"design_id": design_id, "snapshots": SNAPSHOTS.get(design_id, [])}


@router.get("/audit")
async def get_audit_log(current_user: User = Depends(require_roles(["admin", "owner"]))):
    return {"events": AUDIT_LOG[-500:]}
