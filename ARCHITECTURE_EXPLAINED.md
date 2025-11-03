# 🏗️ Architecture Explained: FastAPI vs AgentCore Runtime vs Lambda

## Your Question:
> "How are you using FastAPI Backend - REST API? what is the role of FastAPI Backend, AgentCore Runtime - Serverless production deployment and lambdas functions, what is the difference and usage in this app?"

---

## 📊 Architecture Overview

Your application has **3 deployment options**, each serving different purposes:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKYRCHITECT ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│   React Frontend │───────▶│   Backend Layer  │───────▶│  AWS Bedrock     │
│   (Port 5173)    │        │                  │        │  Claude 4 Sonnet │
└──────────────────┘        └──────────────────┘        └──────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │   Option 1   │  │   Option 2   │  │   Option 3   │
         │   FastAPI    │  │  AgentCore   │  │    Lambda    │
         │   REST API   │  │   Runtime    │  │  Functions   │
         └──────────────┘  └──────────────┘  └──────────────┘
         Development/      Production        Alternative
         Traditional       (Recommended)     Production
```

---

## 🎯 The Three Deployment Options

### Option 1: FastAPI Backend (REST API)
**File**: `backend/api/main.py`
**Status**: ✅ Currently implemented

#### What It Is:
- Traditional Python web server using FastAPI framework
- Runs continuously on a server (EC2, local machine, etc.)
- Handles HTTP requests via REST API endpoints

#### How It Works:
```python
# backend/api/main.py
from fastapi import FastAPI
from backend.agents.architecture_agent import get_architecture_agent

app = FastAPI()

@app.post("/api/architecture/generate")
async def generate_architecture(req: ArchitectureRequirement):
    agent = get_architecture_agent()  # Regular Strands Agent
    response = agent.generate_architecture(req.description)
    return {"response": response}
```

#### When to Use:
- ✅ **Local development and testing** (what you're doing now)
- ✅ **Traditional deployment** on EC2, ECS, or any VM
- ✅ **When you need full control** over the server
- ✅ **Complex workflows** with multiple endpoints
- ✅ **Integration with existing systems**

#### How to Run:
```bash
./start_backend.sh
# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Pros:
- Easy to develop and debug locally
- Full control over request handling
- Standard REST API patterns
- Works with any HTTP client

#### Cons:
- Server runs 24/7 (costs money even when idle)
- You manage scaling, load balancing, monitoring
- Requires server maintenance

---

### Option 2: AgentCore Runtime (Serverless)
**File**: `backend/agents/agentcore_architecture_agent.py`
**Status**: ✅ Implemented for hackathon

#### What It Is:
- **AWS-native serverless deployment** for AI agents
- Uses Bedrock AgentCore primitives (Runtime + Memory)
- **Zero infrastructure management** - AWS handles everything
- **Pay only for actual invocations** (not idle time)

#### How It Works:
```python
# backend/agents/agentcore_architecture_agent.py
from bedrock_agentcore.runtime import BedrockAgentCoreApp, agent_handler

app = BedrockAgentCoreApp()

@agent_handler  # This decorator makes it serverless
def architecture_handler(input_data: dict) -> dict:
    agent = get_agentcore_agent()  # Agent with Memory primitive

    action = input_data.get("action", "generate")
    session_id = input_data.get("session_id")

    # AgentCore Memory provides conversation context
    response = agent.invoke(prompt, session_id)

    return {
        "success": True,
        "response": response,
        "agentcore_primitives_used": ["Runtime", "Memory"]
    }
```

#### When to Use:
- ✅ **Production deployment** (recommended for hackathon)
- ✅ **AWS-native applications**
- ✅ **Variable traffic** (auto-scales to zero)
- ✅ **AI agent-specific workloads**
- ✅ **When you want managed memory/state**

#### How It Works Under the Hood:
1. You deploy with `@agent_handler` decorator
2. AWS creates serverless infrastructure automatically
3. Incoming requests trigger your handler function
4. AgentCore Memory persists conversation across sessions
5. Function shuts down after processing (no idle costs)

#### Deployment:
```bash
# Deploy to AgentCore Runtime
bedrock-agentcore deploy \
  --function architecture_handler \
  --file backend/agents/agentcore_architecture_agent.py \
  --region us-west-2
```

#### Pros:
- **Zero server management** - AWS handles everything
- **Auto-scaling** - handles 1 or 1,000,000 requests
- **Pay per invocation** - no idle costs
- **Built-in memory** - conversation persistence included
- **AWS-native monitoring** - CloudWatch integration
- **Perfect for hackathon** - shows advanced AWS knowledge

#### Cons:
- AWS-specific (not portable)
- Cold start latency (first request slower)
- Less control over infrastructure

---

### Option 3: AWS Lambda Functions
**Status**: ⚠️ Not implemented (alternative option)

#### What It Is:
- Generic AWS serverless compute
- More manual than AgentCore Runtime
- You manage more of the infrastructure code

#### How It Would Work:
```python
# lambda_handler.py (hypothetical)
import json
from backend.agents.architecture_agent import get_architecture_agent

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    body = json.loads(event['body'])

    agent = get_architecture_agent()
    response = agent.generate_architecture(body['requirements'])

    return {
        'statusCode': 200,
        'body': json.dumps({'response': response})
    }
```

#### When to Use:
- ✅ When you want serverless but **NOT using AgentCore**
- ✅ Integration with API Gateway, SQS, EventBridge
- ✅ Generic compute tasks beyond AI agents
- ✅ More control than AgentCore Runtime

#### Deployment:
```bash
# Package and deploy to Lambda
zip -r function.zip backend/
aws lambda create-function \
  --function-name skyrchitect-agent \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://function.zip
```

#### Pros:
- Serverless (pay per invocation)
- Integrates with entire AWS ecosystem
- More control than AgentCore Runtime

#### Cons:
- More complex setup than AgentCore
- No built-in agent memory (you implement it)
- Not specifically designed for AI agents

---

## 🔄 How They Relate in Your Application

### Current Architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR CURRENT SETUP                             │
└─────────────────────────────────────────────────────────────────┘

1. DEVELOPMENT (Now):
   React Frontend → FastAPI Backend → Strands Agent → Bedrock

2. HACKATHON SUBMISSION (Recommended):
   React Frontend → AgentCore Runtime → Strands Agent + Memory → Bedrock
                     (via API Gateway)

3. ALTERNATIVE PRODUCTION (Optional):
   React Frontend → API Gateway → Lambda → Strands Agent → Bedrock
```

### The Two Agents in Your Code:

#### **Agent 1: Basic Strands Agent** (`architecture_agent.py`)
- Used by FastAPI backend
- No AgentCore primitives
- For local development and testing
- Simple, straightforward

#### **Agent 2: AgentCore Agent** (`agentcore_architecture_agent.py`)
- Uses Runtime + Memory primitives
- For production deployment
- **This is your hackathon showcase**
- More advanced, AWS-integrated

---

## 💡 Recommended Deployment Strategy

### Phase 1: Development (Now)
```bash
# Use FastAPI for local testing
./start_backend.sh
python3 test_backend_api.py
```

**Why**: Fast iteration, easy debugging, see logs immediately

### Phase 2: Hackathon Demo (Recommended)
```bash
# Deploy AgentCore Runtime for production demo
bedrock-agentcore deploy --function architecture_handler
```

**Why**:
- Shows you understand AgentCore primitives
- Zero infrastructure management
- Built-in memory for conversation context
- Impresses judges with AWS-native approach

### Phase 3: Alternative (If AgentCore issues)
```bash
# Fallback to Lambda if AgentCore deployment fails
# Convert FastAPI endpoints to Lambda handlers
```

**Why**: Backup plan, still serverless, still production-grade

---

## 📋 Side-by-Side Comparison

| Feature | FastAPI Backend | AgentCore Runtime | Lambda Functions |
|---------|----------------|-------------------|------------------|
| **Deployment** | EC2/VM | Serverless | Serverless |
| **Scaling** | Manual | Auto (0-∞) | Auto (0-∞) |
| **Costs** | 24/7 runtime | Per invocation | Per invocation |
| **Setup** | Easy | Medium | Medium |
| **Agent Memory** | You implement | Built-in | You implement |
| **AWS Integration** | External | Native | Native |
| **Best For** | Development | AI Agents | General compute |
| **Hackathon Points** | Basic | ⭐⭐⭐ High | Medium |
| **Cold Starts** | None | First request | First request |
| **Control** | Full | AWS-managed | Partial |

---

## 🎯 What You Should Do

### For Hackathon Submission:

1. **Keep FastAPI for local testing** ✅
   - Test your agent locally
   - Debug issues quickly
   - Validate API responses

2. **Deploy AgentCore Runtime for demo** ⭐
   - Shows advanced AWS knowledge
   - Uses 2 AgentCore primitives (exceeds requirements)
   - Production-ready deployment
   - Built-in conversation memory

3. **Connect React frontend to AgentCore endpoint**
   - Update API base URL to AgentCore endpoint
   - Test end-to-end flow
   - Create demo video showing serverless architecture

### Implementation Plan:

```bash
# Step 1: Test locally with FastAPI
./start_backend.sh
python3 test_backend_api.py

# Step 2: Deploy to AgentCore Runtime
bedrock-agentcore deploy \
  --function architecture_handler \
  --file backend/agents/agentcore_architecture_agent.py

# Step 3: Get deployment URL
bedrock-agentcore describe --function architecture_handler
# Returns: https://xyz.execute-api.us-west-2.amazonaws.com/prod

# Step 4: Update frontend to use AgentCore URL
# In your React app:
const API_BASE = "https://xyz.execute-api.us-west-2.amazonaws.com/prod"
```

---

## 🏆 Why AgentCore Runtime Wins for Hackathon

1. **Meets "strongly recommended" requirement** ✅
   - Uses Runtime primitive (@agent_handler)
   - Uses Memory primitive (conversation context)

2. **Production-grade** ✅
   - Serverless, auto-scaling
   - AWS-managed monitoring
   - Zero infrastructure

3. **Shows technical depth** ✅
   - Beyond basic LLM integration
   - Advanced AWS service usage
   - Modern cloud-native architecture

4. **Demo-friendly** ✅
   - "Our agent runs serverless on AWS"
   - "Zero servers to manage"
   - "Built with AgentCore primitives"

5. **Cost-effective** ✅
   - Pay only when agent is invoked
   - No idle server costs
   - Scales to zero automatically

---

## 🎬 Demo Script for Video

> "Skyrchitect uses **AWS Bedrock AgentCore primitives** for production deployment.
>
> Our AI agent runs serverless using the **AgentCore Runtime primitive** - no servers to manage.
>
> The **AgentCore Memory primitive** provides persistent conversation history across sessions.
>
> This AWS-native architecture auto-scales from zero to millions of requests while only charging for actual usage.
>
> Let me show you the deployed agent in action..."

[Show browser → React frontend → Call AgentCore endpoint → Agent generates architecture → Show conversation memory working]

---

## ❓ FAQ

**Q: Should I remove FastAPI backend?**
A: No! Keep it for local development. Deploy AgentCore for production.

**Q: Can I use both FastAPI and AgentCore?**
A: Yes. FastAPI for development, AgentCore for production deployment.

**Q: Which impresses judges more?**
A: AgentCore Runtime shows you understand AWS-native AI agent deployment.

**Q: What if AgentCore deployment fails?**
A: Fallback to Lambda or deploy FastAPI on EC2 with public URL.

**Q: Do I need API Gateway with AgentCore?**
A: No, AgentCore Runtime includes API endpoint automatically.

---

## 📚 Key Files Reference

| File | Purpose | Deployment |
|------|---------|------------|
| `backend/api/main.py` | FastAPI REST API | Development |
| `backend/agents/architecture_agent.py` | Basic Strands Agent | Used by FastAPI |
| `backend/agents/agentcore_architecture_agent.py` | AgentCore Agent | Production (AgentCore) |
| `start_backend.sh` | Start FastAPI server | Local testing |
| `test_backend_api.py` | Test FastAPI endpoints | Local testing |
| `test_agentcore.py` | Test AgentCore agent | Validate primitives |

---

## ✅ Summary

**FastAPI Backend (REST API)**
- Traditional web server
- For development and testing
- You manage infrastructure
- File: `backend/api/main.py`

**AgentCore Runtime (Serverless)**
- AWS-native serverless for AI agents
- Zero infrastructure management
- Built-in memory and monitoring
- File: `backend/agents/agentcore_architecture_agent.py`
- **Use this for hackathon demo** ⭐

**Lambda Functions**
- Generic serverless compute
- Alternative to AgentCore
- More manual setup
- Not implemented (optional fallback)

---

**Recommendation**: Deploy AgentCore Runtime for your hackathon submission. It showcases advanced AWS integration, uses 2 primitives (exceeds requirements), and is production-ready with zero server management.
