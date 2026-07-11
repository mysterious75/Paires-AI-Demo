"""
Sample messages for demo - realistic investor-founder communications
"""

SAMPLE_MESSAGES = [
    {
        "sender": "Sarah Chen",
        "sender_email": "sarah.chen@sequoiacap.com",
        "subject": "Interested in your Series A round",
        "body": """Hi,

I came across your company through our mutual connection at TechCrunch Disrupt. Your approach to AI-powered document processing is impressive, and I'd love to learn more about your Series A plans.

At Sequoia, we've been particularly focused on enterprise AI companies with strong unit economics. Your mentioned traction of $2M ARR with 80% gross margins caught my attention.

Would you be available for a 30-minute call next week? I'd like to understand more about your go-to-market strategy and competitive positioning.

Looking forward to connecting.

Best regards,
Sarah Chen
Partner, Sequoia Capital""",
        "thread_id": None,
        "metadata": {"source": "email", "priority": "high"}
    },
    {
        "sender": "Marcus Johnson",
        "sender_email": "marcus@techstartup.io",
        "subject": "Following up on our meeting",
        "body": """Hi Team,

Following up on our call last Tuesday. As discussed, I've attached our updated pitch deck and financial projections.

Key highlights from our conversation:
- Currently at $1.5M ARR, growing 15% MoM
- Raising $8M Series A
- Looking to close by end of Q2

I've also included the customer case studies you requested. Our NRR is at 145% which demonstrates strong product-market fit.

Please let me know if you need any additional information. Happy to schedule a follow-up with our CTO to discuss the technical architecture.

Thanks,
Marcus""",
        "thread_id": None,
        "metadata": {"source": "email", "priority": "medium"}
    },
    {
        "sender": "Emily Rodriguez",
        "sender_email": "emily.r@accel.com",
        "subject": "Quick question about your platform",
        "body": """Hello,

I'm exploring potential investments in the AI infrastructure space and came across your company profile.

A few quick questions:
1. What's your current burn rate?
2. Who are your main competitors?
3. What's your defensibility moat?

Also, are you planning to raise in the next 6 months? We have several portfolio companies that could be potential customers.

Thanks,
Emily""",
        "thread_id": None,
        "metadata": {"source": "linkedin", "priority": "medium"}
    },
    {
        "sender": "David Park",
        "sender_email": "david@founderfund.com",
        "subject": "Introduction request",
        "body": """Hi,

Our mutual friend James from YC suggested I reach out. He mentioned you're building something interesting in the climate tech space.

I'm particularly interested in:
- Your approach to carbon credit verification
- The team's background in sustainability
- Your timeline to revenue

Would you be open to a quick chat? I'm in SF next week and could do an in-person meeting if that works better.

Best,
David Park
Principal, Founder Fund""",
        "thread_id": None,
        "metadata": {"source": "referral", "priority": "high"}
    },
    {
        "sender": "Lisa Thompson",
        "sender_email": "lisa.t@google ventures.com",
        "subject": "Re: Your application to our portfolio",
        "body": """Hi there,

Thank you for applying to join our portfolio. After reviewing your application, we'd like to move forward with the next steps.

Our process typically involves:
1. Initial screening call (30 min)
2. Partner meeting (1 hour)
3. Customer references
4. Final decision

Are you available for the initial screening call next Wednesday or Thursday afternoon?

Looking forward to learning more about your journey.

Best regards,
Lisa""",
        "thread_id": None,
        "metadata": {"source": "application", "priority": "high"}
    }
]


CONVERSATION_THREADS = {
    "thread_001": {
        "participants": ["Sarah Chen", "Founder"],
        "messages": [
            {
                "sender": "Sarah Chen",
                "body": "Hi, interested in learning more about your Series A plans.",
                "subject": "Series A Interest"
            },
            {
                "sender": "Founder",
                "body": "Thanks Sarah! We're raising $10M at $50M pre-money. Happy to share our deck.",
                "subject": "Re: Series A Interest"
            }
        ]
    },
    "thread_002": {
        "participants": ["Marcus Johnson", "IR Team"],
        "messages": [
            {
                "sender": "Marcus Johnson",
                "body": "Following up on our meeting. Here's the updated deck.",
                "subject": "Follow-up"
            },
            {
                "sender": "IR Team",
                "body": "Thanks Marcus! We'll review and get back to you by Friday.",
                "subject": "Re: Follow-up"
            },
            {
                "sender": "Marcus Johnson",
                "body": "Any update on the review? We're getting other interest.",
                "subject": "Checking in"
            }
        ]
    }
}
