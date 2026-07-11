"""
Paires AI Messaging Agent - Production Demo
Applied AI Engineer Role Submission

A complete AI-powered messaging system for investor-founder communications.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

from agent.messaging_agent import MessagingAgent
from agent.classifier import MessageClassifier
from agent.extractor import EntityExtractor
from agent.summarizer import ConversationSummarizer
from evals.quality_tracker import QualityTracker
from guardrails.content_filter import ContentFilter

# ============================================================
# APP CONFIGURATION
# ============================================================

app = FastAPI(
    title="Paires AI Messaging Agent",
    description="""
## Welcome to Paires AI Messaging Agent 

This is a **production-level demo** of an AI-powered messaging system designed for investor-founder communications.

### What This System Does

This AI agent helps investment platforms like Paires manage communications at scale:

- **Automatically classifies** incoming messages (investor inquiries, founder pitches, meeting requests, etc.)
- **Extracts key information** (emails, company names, funding amounts, investment stages)
- **Drafts intelligent replies** using AI, with appropriate tone and context
- **Ensures quality** through automated guardrails and human review
- **Tracks metrics** to continuously improve performance

### How to Use

1. **Send a message** using the `/api/messages/inbound` endpoint
2. **Generate a draft reply** using `/api/drafts/generate`
3. **Review and approve** the draft (human-in-the-loop)
4. **Monitor quality** through the evals dashboard

### Quick Start

Try the `/api/demo/run` endpoint to see the full system in action with sample messages!

### Key Features

- Real-time message classification
- Smart entity extraction
- Context-aware reply generation
- Built-in guardrails (PII detection, compliance checks)
- Comprehensive quality metrics
- Human-in-the-loop workflow

---
*Built for the Paires Applied AI Engineer role*
    """,
    version="1.0.0",
    contact={
        "name": "Applied AI Engineer Candidate",
        "email": "candidate@paires.ai"
    },
    license_info={
        "name": "Proprietary Demo",
        "url": "https://paires.ai"
    }
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
messaging_agent = MessagingAgent()
classifier = MessageClassifier()
extractor = EntityExtractor()
summarizer = ConversationSummarizer()
quality_tracker = QualityTracker()
content_filter = ContentFilter()

# In-memory store
messages_db: Dict[str, Dict] = {}
conversations_db: Dict[str, List] = {}
drafts_db: Dict[str, Dict] = {}


# ============================================================
# DATA MODELS (User-Friendly Descriptions)
# ============================================================

class InboundMessage(BaseModel):
    """
    An incoming message to be processed by the AI agent.
    
    This represents a real message from an investor or founder that needs
    to be classified, analyzed, and potentially replied to.
    """
    sender: str = Field(
        ..., 
        description="Full name of the message sender (e.g., 'Sarah Chen')",
        examples=["Sarah Chen"]
    )
    sender_email: str = Field(
        ..., 
        description="Email address of the sender",
        examples=["sarah.chen@sequoiacap.com"]
    )
    subject: str = Field(
        ..., 
        description="Subject line of the message",
        examples=["Interested in your Series A round"]
    )
    body: str = Field(
        ..., 
        description="The full text content of the message",
        examples=["Hi, I saw your company and would love to discuss investment opportunities."]
    )
    thread_id: Optional[str] = Field(
        None, 
        description="Optional: ID of existing conversation thread (for follow-ups)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Optional: Additional metadata (source, priority, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sender": "Sarah Chen",
                "sender_email": "sarah.chen@sequoiacap.com",
                "subject": "Series A Investment Interest",
                "body": "Hi,\n\nI'm interested in learning more about your Series A plans. At Sequoia, we've been focused on enterprise AI companies.\n\nWould you be available for a call next week?\n\nBest,\nSarah",
                "metadata": {"source": "email", "priority": "high"}
            }
        }


class DraftRequest(BaseModel):
    """
    Request to generate an AI-drafted reply to a message.
    
    After processing an inbound message, use this endpoint to generate
    a context-aware reply that can be reviewed before sending.
    """
    message_id: str = Field(
        ..., 
        description="The ID of the message to reply to (from /api/messages/inbound)"
    )
    tone: Optional[str] = Field(
        "professional", 
        description="Desired tone for the reply",
        enum=["professional", "warm", "concise", "detailed", "follow_up"]
    )
    context: Optional[str] = Field(
        None, 
        description="Optional: Additional context or instructions for the AI"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "abc-123-def-456",
                "tone": "warm",
                "context": "Mention our upcoming product launch"
            }
        }


class DraftResponse(BaseModel):
    """
    AI-generated draft reply with quality metrics.
    
    Includes the drafted reply, classification of the original message,
    extracted entities, guardrail results, and quality score.
    """
    draft_id: str = Field(..., description="Unique identifier for this draft")
    message_id: str = Field(..., description="ID of the original message")
    original_message: str = Field(..., description="The original message being replied to")
    drafted_reply: str = Field(..., description="The AI-generated reply")
    classification: Dict[str, Any] = Field(..., description="How the message was classified")
    extracted_entities: Dict[str, Any] = Field(..., description="Key information extracted from the message")
    guardrail_results: Dict[str, Any] = Field(..., description="Results of safety and quality checks")
    quality_score: float = Field(..., description="Overall quality score (0-1)", ge=0, le=1)
    created_at: str = Field(..., description="Timestamp when the draft was created")


class ApprovalRequest(BaseModel):
    """
    Approve or reject an AI-drafted reply (Human-in-the-Loop).
    
    This is the human review step where you can approve the draft as-is,
    edit it before approving, or reject it with feedback.
    """
    draft_id: str = Field(..., description="ID of the draft to approve/reject")
    approved: bool = Field(..., description="Whether to approve the draft")
    edits: Optional[str] = Field(
        None, 
        description="Optional: Your edited version of the reply (if making changes)"
    )
    feedback: Optional[str] = Field(
        None, 
        description="Optional: Feedback if rejecting (helps improve the AI)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "draft_id": "Use the draft_id from /api/drafts/generate response",
                "approved": True,
                "edits": None,
                "feedback": None
            }
        }


class BatchProcessRequest(BaseModel):
    """
    Process multiple messages at once (Batch Processing).
    
    Useful for initial setup or bulk imports.
    """
    messages: List[InboundMessage] = Field(
        ..., 
        description="List of messages to process",
        min_length=1,
        max_length=100
    )


# ============================================================
# CORE ENDPOINTS
# ============================================================

@app.post(
    "/api/messages/inbound",
    tags=["Message Processing"],
    summary="Process an incoming message",
    description="""
    **Process a new incoming message.**
    
    This endpoint:
    1. Classifies the message type (investor inquiry, founder pitch, etc.)
    2. Extracts key entities (emails, amounts, company names)
    3. Routes to appropriate team/person
    4. Returns classification and extracted data
    
    Use the returned `message_id` to generate a draft reply.
    """,
    response_description="Processing results including classification and extracted entities"
)
async def process_inbound_message(
    message: InboundMessage, 
    background_tasks: BackgroundTasks
):
    """Process an inbound message: classify, extract, route"""
    message_id = str(uuid.uuid4())
    
    # Classify the message
    classification = await classifier.classify(message.body, message.subject)
    
    # Extract entities
    entities = await extractor.extract(message.body)
    
    # Store message
    messages_db[message_id] = {
        "id": message_id,
        "sender": message.sender,
        "sender_email": message.sender_email,
        "subject": message.subject,
        "body": message.body,
        "thread_id": message.thread_id or str(uuid.uuid4()),
        "classification": classification,
        "entities": entities,
        "status": "received",
        "created_at": datetime.now().isoformat(),
        "metadata": message.metadata or {}
    }
    
    # Track conversation
    thread_id = messages_db[message_id]["thread_id"]
    if thread_id not in conversations_db:
        conversations_db[thread_id] = []
    conversations_db[thread_id].append(message_id)
    
    # Log eval metrics in background
    background_tasks.add_task(
        quality_tracker.log_inbound_processing,
        message_id=message_id,
        classification=classification,
        extraction=entities
    )
    
    return {
        "success": True,
        "message_id": message_id,
        "classification": classification,
        "entities": entities,
        "routing": classification.get("routing_suggestion", {}),
        "status": "processed",
        "next_step": "Use /api/drafts/generate to create a reply"
    }


@app.post(
    "/api/drafts/generate",
    tags=["Draft Generation"],
    summary="Generate an AI-drafted reply",
    description="""
    **Generate an intelligent reply to a processed message.**
    
    The AI considers:
    - The original message content
    - How it was classified
    - Extracted entities (company, funding stage, etc.)
    - Conversation history (if available)
    - Your specified tone
    
    The draft goes through guardrails before being returned.
    """,
    response_model=DraftResponse,
    response_description="The AI-drafted reply with quality metrics"
)
async def generate_draft(
    request: DraftRequest, 
    background_tasks: BackgroundTasks
):
    """Generate an AI-drafted reply to a message"""
    
    # Auto-use latest message if no valid message_id
    msg_id = request.message_id
    if msg_id not in messages_db:
        if not messages_db:
            raise HTTPException(
                status_code=404,
                detail="No messages found. Process a message first with /api/messages/inbound or run /api/test/full-flow"
            )
        # Use the latest message
        msg_id = list(messages_db.keys())[-1]
    
    original = messages_db[msg_id]
    
    # Get conversation context
    thread_id = original["thread_id"]
    thread_messages = [
        messages_db[mid] for mid in conversations_db.get(thread_id, [])
        if mid in messages_db
    ]
    
    # Generate draft
    draft = await messaging_agent.draft_reply(
        original_message=original["body"],
        classification=original["classification"],
        entities=original["entities"],
        thread_context=thread_messages,
        tone=request.tone,
        additional_context=request.context,
        sender_name=original.get("sender", "").split()[0] if original.get("sender") else None
    )
    
    # Run guardrails
    guardrail_results = await content_filter.check(draft)
    
    # Calculate quality score
    quality_score = await quality_tracker.score_draft(
        original=original["body"],
        draft=draft,
        classification=original["classification"]
    )
    
    draft_id = str(uuid.uuid4())
    
    # Store draft
    draft_data = {
        "draft_id": draft_id,
        "message_id": msg_id,
        "drafted_reply": draft,
        "guardrail_results": guardrail_results,
        "quality_score": quality_score,
        "status": "pending_review",
        "created_at": datetime.now().isoformat()
    }
    messages_db[msg_id]["draft"] = draft_data
    drafts_db[draft_id] = draft_data
    
    # Background eval
    background_tasks.add_task(
        quality_tracker.log_draft_generation,
        draft_id=draft_id,
        quality_score=quality_score,
        guardrail_passed=guardrail_results["passed"]
    )
    
    return DraftResponse(
        draft_id=draft_id,
        message_id=msg_id,
        original_message=original["body"],
        drafted_reply=draft,
        classification=original["classification"],
        extracted_entities=original["entities"],
        guardrail_results=guardrail_results,
        quality_score=quality_score,
        created_at=draft_data["created_at"]
    )


@app.post(
    "/api/drafts/{draft_id}/approve",
    tags=["Human Review"],
    summary="Approve or reject a draft (Human-in-the-Loop)",
    description="""
    **Review and approve an AI-drafted reply.**
    
    This is the critical human review step:
    
    - **Approve as-is**: Send the AI's draft
    - **Edit and approve**: Make changes, then approve
    - **Reject**: Provide feedback to improve future drafts
    
    All approvals are tracked for quality metrics.
    """,
    response_description="Approval status and confirmation"
)
async def approve_draft(
    draft_id: str, 
    approval: ApprovalRequest, 
    background_tasks: BackgroundTasks
):
    """Approve or edit a drafted reply (human-in-the-loop)"""
    # Auto-use latest draft if draft_id not found
    did = draft_id
    if did not in drafts_db:
        if not drafts_db:
            raise HTTPException(
                status_code=404, 
                detail="No drafts found. Generate a draft first with /api/drafts/generate or /api/test/create-and-draft"
            )
        did = list(drafts_db.keys())[-1]
    
    draft = drafts_db[did]
    message_id = draft["message_id"]
    
    if message_id not in messages_db:
        raise HTTPException(status_code=404, detail="Original message not found")
    
    if approval.approved:
        final_reply = approval.edits or draft["drafted_reply"]
        draft["status"] = "approved"
        draft["final_reply"] = final_reply
        messages_db[message_id]["status"] = "replied"
    else:
        draft["status"] = "rejected"
        draft["rejection_reason"] = approval.feedback
    
    # Log approval metrics
    background_tasks.add_task(
        quality_tracker.log_approval,
        draft_id=did,
        approved=approval.approved,
        had_edits=bool(approval.edits),
        feedback=approval.feedback
    )
    
    return {
        "success": True,
        "draft_id": did,
        "status": draft["status"],
        "message": f"Draft {'approved' if approval.approved else 'rejected'} successfully"
    }


# ============================================================
# BATCH PROCESSING
# ============================================================

@app.post(
    "/api/messages/batch",
    tags=["Batch Processing"],
    summary="Process multiple messages at once",
    description="""
    **Process multiple messages in a single request.**
    
    Useful for:
    - Initial data imports
    - Bulk message processing
    - Testing with multiple samples
    
    Returns results for each processed message.
    """,
    response_description="Processing results for all messages"
)
async def batch_process_messages(
    request: BatchProcessRequest, 
    background_tasks: BackgroundTasks
):
    """Process multiple messages at once"""
    results = []
    
    for msg in request.messages:
        message_id = str(uuid.uuid4())
        
        classification = await classifier.classify(msg.body, msg.subject)
        entities = await extractor.extract(msg.body)
        
        messages_db[message_id] = {
            "id": message_id,
            "sender": msg.sender,
            "sender_email": msg.sender_email,
            "subject": msg.subject,
            "body": msg.body,
            "thread_id": msg.thread_id or str(uuid.uuid4()),
            "classification": classification,
            "entities": entities,
            "status": "received",
            "created_at": datetime.now().isoformat(),
            "metadata": msg.metadata or {}
        }
        
        thread_id = messages_db[message_id]["thread_id"]
        if thread_id not in conversations_db:
            conversations_db[thread_id] = []
        conversations_db[thread_id].append(message_id)
        
        results.append({
            "message_id": message_id,
            "sender": msg.sender,
            "classification": classification.get("type"),
            "confidence": classification.get("confidence"),
            "status": "processed"
        })
    
    return {
        "success": True,
        "processed_count": len(results),
        "results": results
    }


# ============================================================
# CONVERSATIONS
# ============================================================

@app.get(
    "/api/conversations/summary",
    tags=["Conversations"],
    summary="Get conversation summary (auto-uses latest thread)",
    description="""
    **Get an AI-generated summary of a conversation thread.**
    
    Optionally provide `thread_id` parameter to specify which thread.
    If no thread_id provided, uses the latest thread automatically.
    
    Returns:
    - Brief summary of the conversation
    - Key points discussed
    - Action items
    - Recommended next steps
    """,
    response_description="Conversation summary with key points and action items"
)
async def get_conversation_summary(thread_id: Optional[str] = None):
    """Get AI-generated summary of a conversation thread"""
    # Auto-use latest thread if no thread_id provided or invalid
    tid = thread_id
    if not tid or tid not in conversations_db:
        if not conversations_db:
            return {
                "success": False,
                "message": "No conversations found. Process a message first with /api/messages/inbound or run /api/test/full-flow",
                "threads": []
            }
        tid = list(conversations_db.keys())[-1]
    
    thread_messages = [
        messages_db[mid] for mid in conversations_db[tid]
        if mid in messages_db
    ]
    
    summary = await summarizer.summarize(thread_messages)
    
    return {
        "success": True,
        "thread_id": tid,
        "message_count": len(thread_messages),
        "summary": summary,
        "key_points": summary.get("key_points", []),
        "action_items": summary.get("action_items", []),
        "next_steps": summary.get("next_steps", [])
    }


@app.get(
    "/api/conversations",
    tags=["Conversations"],
    summary="List all conversation threads",
    description="Get a list of all active conversation threads with their message counts.",
    response_description="List of conversation threads"
)
async def list_conversations():
    """List all conversation threads"""
    threads = []
    for thread_id, message_ids in conversations_db.items():
        if message_ids:
            first_msg = messages_db.get(message_ids[0], {})
            threads.append({
                "thread_id": thread_id,
                "message_count": len(message_ids),
                "participants": list(set(
                    messages_db[mid].get("sender", "Unknown") 
                    for mid in message_ids 
                    if mid in messages_db
                )),
                "subject": first_msg.get("subject", "No subject"),
                "last_activity": messages_db.get(message_ids[-1], {}).get("created_at")
            })
    
    return {
        "success": True,
        "total_threads": len(threads),
        "threads": threads
    }


# ============================================================
# EVALS & METRICS
# ============================================================

@app.get(
    "/api/evals/dashboard",
    tags=["Quality Metrics"],
    summary="Get eval metrics dashboard",
    description="""
    **Comprehensive quality metrics dashboard.**
    
    Shows:
    - Total messages processed
    - Drafts generated
    - Approval rates
    - Average quality scores
    - Guardrail pass rates
    """,
    response_description="Dashboard metrics"
)
async def get_eval_dashboard():
    """Get eval metrics dashboard"""
    return quality_tracker.get_dashboard_metrics()


@app.get(
    "/api/evals/recent",
    tags=["Quality Metrics"],
    summary="Get recent evaluation results",
    description="Get the most recent draft evaluations with quality scores.",
    response_description="List of recent evaluations"
)
async def get_recent_evals(limit: int = Query(20, ge=1, le=100)):
    """Get recent eval results"""
    return quality_tracker.get_recent_evals(limit)


@app.get(
    "/api/evals/accuracy",
    tags=["Quality Metrics"],
    summary="Get accuracy metrics",
    description="Get classification and extraction accuracy metrics.",
    response_description="Accuracy metrics"
)
async def get_accuracy_metrics():
    """Get classification and routing accuracy"""
    return quality_tracker.get_accuracy_metrics()


# ============================================================
# ANALYTICS
# ============================================================

@app.get(
    "/api/analytics/volume",
    tags=["Analytics"],
    summary="Get message volume analytics",
    description="Get analytics on message volume, distribution by type, and trends.",
    response_description="Volume analytics"
)
async def get_volume_analytics():
    """Get message volume analytics"""
    return {
        "success": True,
        "total_messages": len(messages_db),
        "total_drafts": len(drafts_db),
        "approval_rate": quality_tracker.get_approval_rate(),
        "avg_quality_score": quality_tracker.get_avg_quality_score(),
        "by_classification": quality_tracker.get_by_classification(),
        "by_hour": quality_tracker.get_by_hour()
    }


@app.get(
    "/api/analytics/performance",
    tags=["Analytics"],
    summary="Get agent performance metrics",
    description="Get detailed performance metrics for the AI agent.",
    response_description="Performance metrics"
)
async def get_performance_metrics():
    """Get agent performance metrics"""
    return {
        "success": True,
        "avg_response_time_ms": quality_tracker.get_avg_response_time(),
        "classification_accuracy": quality_tracker.get_classification_accuracy(),
        "extraction_accuracy": quality_tracker.get_extraction_accuracy(),
        "guardrail_pass_rate": quality_tracker.get_guardrail_pass_rate(),
        "human_edit_rate": quality_tracker.get_human_edit_rate()
    }


# ============================================================
# DEMO & TESTING
# ============================================================

@app.post(
    "/api/demo/run",
    tags=["Demo"],
    summary="Run complete demo with sample messages",
    description="""
    **Run a complete demo of the system.**
    
    This endpoint:
    1. Processes 5 sample messages (investor inquiries, founder pitches, etc.)
    2. Generates AI-drafted replies for each
    3. Returns full results including classifications, extractions, and drafts
    
    Perfect for seeing the entire system in action!
    """,
    response_description="Demo results with all processed messages and drafts"
)
async def run_demo(background_tasks: BackgroundTasks):
    """Run a full demo flow with sample messages"""
    from data.sample_messages import SAMPLE_MESSAGES
    
    results = []
    for msg_data in SAMPLE_MESSAGES:
        # Process message
        message_id = str(uuid.uuid4())
        
        classification = await classifier.classify(msg_data["body"], msg_data["subject"])
        entities = await extractor.extract(msg_data["body"])
        
        messages_db[message_id] = {
            "id": message_id,
            "sender": msg_data["sender"],
            "sender_email": msg_data["sender_email"],
            "subject": msg_data["subject"],
            "body": msg_data["body"],
            "thread_id": str(uuid.uuid4()),
            "classification": classification,
            "entities": entities,
            "status": "received",
            "created_at": datetime.now().isoformat(),
            "metadata": msg_data.get("metadata", {})
        }
        
        # Generate draft
        draft_text = await messaging_agent.draft_reply(
            original_message=msg_data["body"],
            classification=classification,
            entities=entities,
            thread_context=[],
            tone="professional",
            sender_name=msg_data["sender"].split()[0] if msg_data.get("sender") else None
        )
        
        guardrail_results = await content_filter.check(draft_text)
        quality_score = await quality_tracker.score_draft(
            original=msg_data["body"],
            draft=draft_text,
            classification=classification
        )
        
        draft_id = str(uuid.uuid4())
        draft_data = {
            "draft_id": draft_id,
            "message_id": message_id,
            "drafted_reply": draft_text,
            "guardrail_results": guardrail_results,
            "quality_score": quality_score,
            "status": "pending_review",
            "created_at": datetime.now().isoformat()
        }
        messages_db[message_id]["draft"] = draft_data
        drafts_db[draft_id] = draft_data
        
        results.append({
            "message_id": message_id,
            "sender": msg_data["sender"],
            "subject": msg_data["subject"],
            "classification": classification,
            "entities": {
                "sender_name": entities.get("sender_name"),
                "company_name": entities.get("company_name"),
                "funding_stage": entities.get("funding_stage"),
                "emails": entities.get("emails")
            },
            "draft_id": draft_id,
            "drafted_reply": draft_text[:200] + "..." if len(draft_text) > 200 else draft_text,
            "quality_score": quality_score,
            "guardrail_passed": guardrail_results["passed"]
        })
    
    return {
        "success": True,
        "demo_run": True,
        "messages_processed": len(results),
        "results": results,
        "next_steps": [
            "View full drafts at /api/drafts/{draft_id}",
            "Approve drafts at /api/drafts/{draft_id}/approve",
            "Check metrics at /api/evals/dashboard"
        ]
    }


@app.get(
    "/api/demo/quick-test",
    tags=["Demo"],
    summary="Quick test with a single message",
    description="Process a single sample investor inquiry message for quick testing.",
    response_description="Quick test results"
)
async def quick_test(background_tasks: BackgroundTasks):
    """Quick test with a single message"""
    msg_data = {
        "sender": "Test Investor",
        "sender_email": "investor@test.com",
        "subject": "Quick Question",
        "body": "Hi, I'm interested in your Series A. What's your current ARR and burn rate?"
    }
    
    # Process
    message_id = str(uuid.uuid4())
    classification = await classifier.classify(msg_data["body"], msg_data["subject"])
    entities = await extractor.extract(msg_data["body"])
    
    messages_db[message_id] = {
        "id": message_id,
        **msg_data,
        "thread_id": str(uuid.uuid4()),
        "classification": classification,
        "entities": entities,
        "status": "received",
        "created_at": datetime.now().isoformat(),
        "metadata": {}
    }
    
    # Generate draft
    draft_text = await messaging_agent.draft_reply(
        original_message=msg_data["body"],
        classification=classification,
        entities=entities,
        thread_context=[],
        tone="professional",
        sender_name=msg_data["sender"].split()[0]
    )
    
    return {
        "success": True,
        "message_id": message_id,
        "classification": classification,
        "entities": entities,
        "draft": draft_text,
        "status": "ready for review"
    }


# ============================================================
# SYSTEM
# ============================================================

@app.get(
    "/api/health",
    tags=["System"],
    summary="Health check",
    description="Check the health status of all system components.",
    response_description="System health status"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "agent": "ready",
            "classifier": "ready",
            "extractor": "ready",
            "summarizer": "ready",
            "evals": "ready",
            "guardrails": "ready"
        },
        "stats": {
            "messages_processed": len(messages_db),
            "drafts_generated": len(drafts_db)
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/api/drafts",
    tags=["Draft Generation"],
    summary="List all drafts",
    description="Get a list of all generated drafts with their IDs for use in the approve endpoint.",
    response_description="List of drafts"
)
async def list_drafts():
    """List all generated drafts"""
    drafts_list = []
    for draft_id, draft in drafts_db.items():
        drafts_list.append({
            "draft_id": draft_id,
            "message_id": draft.get("message_id"),
            "status": draft.get("status"),
            "quality_score": draft.get("quality_score"),
            "created_at": draft.get("created_at"),
            "preview": draft.get("drafted_reply", "")[:100] + "..."
        })
    
    return {
        "success": True,
        "total_drafts": len(drafts_list),
        "drafts": drafts_list
    }


# ============================================================
# EASY TEST ENDPOINTS (One-Click Testing)
# ============================================================

@app.post(
    "/api/test/create-and-draft",
    tags=["Easy Test"],
    summary="One-click: Create message + Generate draft",
    description="""
    **One-click test!** 
    
    Creates a sample message AND generates an AI draft reply.
    Returns both IDs so you can test the approve endpoint next.
    
    No input needed - just click Execute!
    """,
    response_description="Created message and draft with IDs"
)
async def test_create_and_draft(background_tasks: BackgroundTasks):
    """One-click: Create message + generate draft"""
    # Create sample message
    msg_data = {
        "sender": "Test Investor",
        "sender_email": "investor@test.com",
        "subject": "Series A Interest",
        "body": "Hi, I'm interested in your Series A round. What's your current ARR and burn rate? Would love to schedule a call."
    }
    
    message_id = str(uuid.uuid4())
    classification = await classifier.classify(msg_data["body"], msg_data["subject"])
    entities = await extractor.extract(msg_data["body"])
    
    messages_db[message_id] = {
        "id": message_id,
        "sender": msg_data["sender"],
        "sender_email": msg_data["sender_email"],
        "subject": msg_data["subject"],
        "body": msg_data["body"],
        "thread_id": str(uuid.uuid4()),
        "classification": classification,
        "entities": entities,
        "status": "received",
        "created_at": datetime.now().isoformat(),
        "metadata": {}
    }
    
    # Generate draft
    draft_text = await messaging_agent.draft_reply(
        original_message=msg_data["body"],
        classification=classification,
        entities=entities,
        thread_context=[],
        tone="professional",
        sender_name=msg_data["sender"].split()[0]
    )
    
    guardrail_results = await content_filter.check(draft_text)
    quality_score = await quality_tracker.score_draft(
        original=msg_data["body"],
        draft=draft_text,
        classification=classification
    )
    
    draft_id = str(uuid.uuid4())
    draft_data = {
        "draft_id": draft_id,
        "message_id": message_id,
        "drafted_reply": draft_text,
        "guardrail_results": guardrail_results,
        "quality_score": quality_score,
        "status": "pending_review",
        "created_at": datetime.now().isoformat()
    }
    messages_db[message_id]["draft"] = draft_data
    drafts_db[draft_id] = draft_data
    
    return {
        "success": True,
        "message": "Message created and draft generated!",
        "message_id": message_id,
        "draft_id": draft_id,
        "sender": msg_data["sender"],
        "subject": msg_data["subject"],
        "classification": classification["type"],
        "quality_score": quality_score,
        "drafted_reply": draft_text,
        "next_step": f"Copy the draft_id and use it in /api/drafts/{draft_id}/approve"
    }


@app.post(
    "/api/test/approve-latest",
    tags=["Easy Test"],
    summary="One-click: Approve the latest draft",
    description="""
    **One-click test!** 
    
    Automatically approves the most recent draft.
    Run `/api/test/create-and-draft` first, then click Execute here!
    """,
    response_description="Approval confirmation"
)
async def test_approve_latest(background_tasks: BackgroundTasks):
    """One-click: Approve the latest draft"""
    if not drafts_db:
        return {
            "success": False,
            "message": "No drafts found. Run /api/test/create-and-draft first!"
        }
    
    # Get latest draft
    latest_draft_id = list(drafts_db.keys())[-1]
    draft = drafts_db[latest_draft_id]
    message_id = draft["message_id"]
    
    # Approve it
    draft["status"] = "approved"
    draft["final_reply"] = draft["drafted_reply"]
    if message_id in messages_db:
        messages_db[message_id]["status"] = "replied"
    
    # Log metrics
    background_tasks.add_task(
        quality_tracker.log_approval,
        draft_id=latest_draft_id,
        approved=True,
        had_edits=False,
        feedback=None
    )
    
    return {
        "success": True,
        "message": "Latest draft approved!",
        "draft_id": latest_draft_id,
        "status": "approved",
        "quality_score": draft.get("quality_score"),
        "next_step": "Check /api/evals/dashboard to see updated metrics"
    }


@app.post(
    "/api/test/full-flow",
    tags=["Easy Test"],
    summary="One-click: Complete workflow (create + draft + approve)",
    description="""
    **One-click test!** 
    
    Runs the ENTIRE workflow:
    1. Creates a sample message
    2. Generates an AI draft
    3. Approves the draft
    
    Everything happens automatically!
    """,
    response_description="Complete workflow results"
)
async def test_full_flow(background_tasks: BackgroundTasks):
    """One-click: Complete workflow"""
    # Step 1: Create message
    msg_data = {
        "sender": "Demo Founder",
        "sender_email": "founder@startup.com",
        "subject": "Raising $10M Series A",
        "body": "Hi, we're raising a $10M Series A at $50M valuation. Currently at $3M ARR with 80% margins. Looking for investors who understand B2B SaaS."
    }
    
    message_id = str(uuid.uuid4())
    classification = await classifier.classify(msg_data["body"], msg_data["subject"])
    entities = await extractor.extract(msg_data["body"])
    
    messages_db[message_id] = {
        "id": message_id,
        "sender": msg_data["sender"],
        "sender_email": msg_data["sender_email"],
        "subject": msg_data["subject"],
        "body": msg_data["body"],
        "thread_id": str(uuid.uuid4()),
        "classification": classification,
        "entities": entities,
        "status": "received",
        "created_at": datetime.now().isoformat(),
        "metadata": {}
    }
    
    # Step 2: Generate draft
    draft_text = await messaging_agent.draft_reply(
        original_message=msg_data["body"],
        classification=classification,
        entities=entities,
        thread_context=[],
        tone="warm",
        sender_name=msg_data["sender"].split()[0]
    )
    
    guardrail_results = await content_filter.check(draft_text)
    quality_score = await quality_tracker.score_draft(
        original=msg_data["body"],
        draft=draft_text,
        classification=classification
    )
    
    draft_id = str(uuid.uuid4())
    draft_data = {
        "draft_id": draft_id,
        "message_id": message_id,
        "drafted_reply": draft_text,
        "guardrail_results": guardrail_results,
        "quality_score": quality_score,
        "status": "pending_review",
        "created_at": datetime.now().isoformat()
    }
    messages_db[message_id]["draft"] = draft_data
    drafts_db[draft_id] = draft_data
    
    # Step 3: Approve draft
    draft_data["status"] = "approved"
    draft_data["final_reply"] = draft_text
    messages_db[message_id]["status"] = "replied"
    
    background_tasks.add_task(
        quality_tracker.log_approval,
        draft_id=draft_id,
        approved=True,
        had_edits=False,
        feedback=None
    )
    
    return {
        "success": True,
        "message": "Complete workflow executed!",
        "steps": {
            "1_message_created": {
                "message_id": message_id,
                "sender": msg_data["sender"],
                "subject": msg_data["subject"]
            },
            "2_draft_generated": {
                "draft_id": draft_id,
                "quality_score": quality_score,
                "guardrail_passed": guardrail_results["passed"]
            },
            "3_draft_approved": {
                "status": "approved",
                "message": "Ready to send!"
            }
        },
        "drafted_reply": draft_text,
        "summary": f"Processed message from {msg_data['sender']}, classified as {classification['type']}, draft approved with {quality_score*100:.0f}% quality score"
    }


@app.get(
    "/",
    tags=["System"],
    summary="Welcome page",
    description="Welcome page with links to documentation.",
    response_class=HTMLResponse
)
async def root():
    """Welcome page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Paires AI Messaging Agent</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
            .card { background: white; border-radius: 12px; padding: 30px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #0077B5; }
            h2 { color: #333; border-bottom: 2px solid #0077B5; padding-bottom: 10px; }
            .endpoint { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }
            .method { background: #0077B5; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .path { font-family: monospace; font-weight: bold; }
            a { color: #0077B5; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .btn { display: inline-block; background: #0077B5; color: white; padding: 12px 24px; 
                   border-radius: 8px; text-decoration: none; margin: 10px 5px; }
            .btn:hover { background: #005885; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Paires AI Messaging Agent</h1>
            <p>Production-level demo for the Applied AI Engineer role</p>
            <a href="/docs" class="btn">API Documentation</a>
            <a href="/api/demo/run" class="btn">Run Demo</a>
            <a href="/api/health" class="btn">Health Check</a>
        </div>
        
        <div class="card">
            <h2>Quick Start</h2>
            <ol>
                <li>Click <strong>"Run Demo"</strong> above to process sample messages</li>
                <li>Go to <a href="/api/evals/dashboard">Metrics Dashboard</a> to see results</li>
                <li>Try the API endpoints in the <a href="/docs">Documentation</a></li>
            </ol>
        </div>
        
        <div class="card" style="border: 2px solid #44712E;">
            <h2 style="color: #44712E;">Easy Test (One-Click!)</h2>
            <p>Try these first - no input needed, just click Execute in /docs!</p>
            <div class="endpoint" style="background: #E8F5E9;">
                <span class="method" style="background: #44712E;">POST</span>
                <span class="path">/api/test/full-flow</span>
                <p><strong>BEST ONE!</strong> Creates message + generates draft + approves it</p>
            </div>
            <div class="endpoint" style="background: #E8F5E9;">
                <span class="method" style="background: #44712E;">POST</span>
                <span class="path">/api/test/create-and-draft</span>
                <p>Creates message and generates draft (returns IDs for testing)</p>
            </div>
            <div class="endpoint" style="background: #E8F5E9;">
                <span class="method" style="background: #44712E;">POST</span>
                <span class="path">/api/test/approve-latest</span>
                <p>Approves the most recent draft</p>
            </div>
        </div>

        <div class="card">
            <h2>All Endpoints</h2>
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="path">/api/messages/inbound</span>
                <p>Process a new incoming message</p>
            </div>
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="path">/api/drafts/generate</span>
                <p>Generate an AI-drafted reply</p>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/api/drafts</span>
                <p>List all drafts</p>
            </div>
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="path">/api/drafts/{id}/approve</span>
                <p>Approve or edit a draft (Human-in-the-Loop)</p>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/api/evals/dashboard</span>
                <p>View quality metrics</p>
            </div>
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="path">/api/demo/run</span>
                <p>Run full demo with 5 sample messages</p>
            </div>
        </div>
        
        <div class="card">
            <h2>Features</h2>
            <ul>
                <li>AI-powered message classification</li>
                <li>Smart entity extraction</li>
                <li>Context-aware reply generation</li>
                <li>Built-in guardrails (PII, compliance)</li>
                <li>Quality scoring and metrics</li>
                <li>Human-in-the-loop workflow</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
