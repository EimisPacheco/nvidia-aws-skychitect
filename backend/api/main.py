"""FastAPI Backend for Skyrchitect AI Agent"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.models.schemas import (
    ArchitectureRequirement,
    ComponentOptimizationRequest,
    DiagramAnalysisRequest,
    ArchitectureRecommendation,
    OptimizationSuggestion,
    AgentResponse,
    HealthCheck
)
from backend.agents.architecture_agent import get_architecture_agent, ArchitectureAgent
from backend.utils.response_parser import (
    parse_claude_architecture_response,
    transform_to_ui_format
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Skyrchitect AI Backend...")
    logger.info(f"   AWS Region: {os.getenv('AWS_DEFAULT_REGION', 'us-west-2')}")
    logger.info(f"   Bedrock Model: {os.getenv('BEDROCK_MODEL_ID', 'claude-3-5-sonnet')}")

    try:
        # Initialize agent
        agent = get_architecture_agent()
        logger.info("✅ Architecture Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        logger.warning("   Agent will be initialized on first request")

    yield

    # Shutdown
    logger.info("👋 Shutting down Skyrchitect AI Backend")


# Create FastAPI app
app = FastAPI(
    title="Skyrchitect AI Backend",
    description="AI-powered cloud architecture design and optimization API using AWS Bedrock and Strands Agents",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://localhost:5174",
        "*"  # Allow all for hackathon demo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get agent (supports both Bedrock and SageMaker)
def get_agent():
    """
    Dependency to get architecture agent

    Supports two backends:
    - 'sagemaker': NVIDIA NIMs on SageMaker (NVIDIA-AWS Hackathon)
    - 'bedrock': AWS Bedrock Claude (AWS AI Agent Hackathon)

    Set MODEL_TYPE environment variable to choose backend.
    """
    try:
        model_type = os.getenv("MODEL_TYPE", "sagemaker").lower()

        logger.info(f"🔧 Using model type: {model_type}")

        if model_type == "sagemaker":
            # NVIDIA-AWS Hackathon: Use Llama 3.1 Nemotron + Embedding NIM on SageMaker
            from backend.agents.architecture_agent_sagemaker import get_architecture_agent_sagemaker
            logger.info("✅ Loading SageMaker agent (NVIDIA NIMs)")
            return get_architecture_agent_sagemaker()
        elif model_type == "bedrock":
            # AWS AI Agent Hackathon: Use Claude Sonnet 4 on Bedrock
            from backend.agents.architecture_agent import get_architecture_agent
            logger.info("✅ Loading Bedrock agent (Claude Sonnet 4)")
            return get_architecture_agent()
        else:
            raise ValueError(f"Unknown MODEL_TYPE: {model_type}. Use 'sagemaker' or 'bedrock'")

    except Exception as e:
        logger.error(f"❌ Failed to get agent: {e}")
        logger.error(f"   Make sure to set MODEL_TYPE environment variable")
        raise HTTPException(
            status_code=503,
            detail=f"AI Agent not available: {str(e)}. Check MODEL_TYPE setting and endpoint availability."
        )


# Health check endpoint
@app.get("/", response_model=HealthCheck)
async def root():
    """API root and health check"""
    model_type = os.getenv("MODEL_TYPE", "sagemaker").lower()

    try:
        agent = get_agent()
        agent_ready = True
        bedrock_connected = (model_type == "bedrock")
    except Exception as e:
        logger.warning(f"Agent not ready: {e}")
        agent_ready = False
        bedrock_connected = False

    # Determine model ID based on type
    if model_type == "sagemaker":
        model_id = f"sagemaker:{os.getenv('SAGEMAKER_ENDPOINT_NAME', 'llama-nemotron-endpoint')}"
    else:
        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")

    return HealthCheck(
        status="healthy" if agent_ready else "degraded",
        version="1.0.0-nvidia-aws-hackathon",
        agent_ready=agent_ready,
        bedrock_connected=bedrock_connected,
        model_id=model_id
    )


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "ok", "service": "Skyrchitect AI Backend"}


# AI Agent Endpoints

@app.post("/api/architecture/generate", response_model=AgentResponse)
async def generate_architecture(
    req: ArchitectureRequirement,
    agent: ArchitectureAgent = Depends(get_agent)
):
    """
    Generate cloud architecture based on requirements using AI agent
    """
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"📝 ARCHITECTURE GENERATION REQUEST")
        logger.info(f"{'='*80}")
        logger.info(f"Title: {req.title}")
        logger.info(f"Provider: {req.provider.value}")
        logger.info(f"Optimization Goal: {req.optimization_goal.value}")

        # Format requirements for agent
        requirements_text = f"""
Title: {req.title}
Description: {req.description}
Cloud Provider: {req.provider.value}
Optimization Goal: {req.optimization_goal.value}
"""

        # Add requirements only if they exist and are not empty
        if req.requirements and len(req.requirements) > 0:
            requirements_text += f"""
Requirements:
{chr(10).join(f"- {r}" for r in req.requirements)}
"""

        if req.budget:
            requirements_text += f"\nBudget: ${req.budget}/month"

        if req.expected_users:
            requirements_text += f"\nExpected Users: {req.expected_users:,}"

        logger.info(f"\n📤 Sending to AI:\n{requirements_text}")

        # Get agent recommendation
        response = agent.generate_architecture(requirements_text)

        logger.info(f"\n📥 AI Response received (length: {len(str(response))} chars)")
        logger.info(f"✅ Architecture generated successfully")
        logger.info(f"{'='*80}\n")

        # Parse hybrid response (JSON + markdown)
        architecture_json, markdown_reasoning = parse_claude_architecture_response(str(response))

        if architecture_json:
            logger.info(f"📊 Parsed Architecture JSON:")
            logger.info(f"   - Services: {len(architecture_json.get('architecture', {}).get('services', []))}")
            logger.info(f"   - Connections: {len(architecture_json.get('architecture', {}).get('connections', []))}")
            logger.info(f"   - Total Cost: ${architecture_json.get('architecture', {}).get('total_cost', 0)}/mo")

            # Transform to UI format
            ui_architecture = transform_to_ui_format(architecture_json, req.provider.value)

            return AgentResponse(
                success=True,
                message="Architecture generated successfully",
                data=ui_architecture,
                reasoning=markdown_reasoning
            )
        else:
            # Fallback if JSON extraction fails - return raw response
            logger.warning("⚠️ Could not extract JSON from response, returning raw format")
            return AgentResponse(
                success=True,
                message="Architecture generated successfully",
                data={
                    "architecture": str(response),
                    "provider": req.provider.value,
                    "optimization_goal": req.optimization_goal.value
                },
                reasoning=str(response)
            )

    except Exception as e:
        logger.error(f"Error generating architecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/architecture/optimize", response_model=AgentResponse)
async def optimize_architecture(
    req: ComponentOptimizationRequest,
    agent: ArchitectureAgent = Depends(get_agent)
):
    """
    Optimize existing architecture for cost or performance
    """
    try:
        logger.info(f"Optimizing architecture (goal: {req.optimization_goal.value})")

        # Format current architecture
        arch_description = f"""
Provider: {req.provider.value}
Current Monthly Cost: ${req.current_cost}
Optimization Goal: {req.optimization_goal.value}

Current Components:
{chr(10).join(f"- {c}" for c in req.components)}
"""

        # Get optimization recommendations
        response = agent.optimize_architecture(
            arch_description,
            req.optimization_goal.value
        )

        logger.info("✅ Optimization completed")

        return AgentResponse(
            success=True,
            message="Optimization recommendations generated",
            data={
                "optimizations": str(response),
                "current_cost": req.current_cost,
                "goal": req.optimization_goal.value
            },
            reasoning=str(response)
        )

    except Exception as e:
        logger.error(f"Error optimizing architecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/architecture/validate", response_model=AgentResponse)
async def validate_architecture(
    req: DiagramAnalysisRequest,
    agent: ArchitectureAgent = Depends(get_agent)
):
    """
    Validate architecture design and provide best practice recommendations
    """
    try:
        logger.info("Validating architecture design")

        # Format architecture for validation
        arch_description = f"""
Provider: {req.provider.value}

Services:
{chr(10).join(f"- {node}" for node in req.nodes)}

Connections:
{chr(10).join(f"- {edge}" for edge in req.edges)}
"""

        if req.requirements:
            arch_description += f"\nRequirements: {req.requirements}"

        # Validate with agent
        response = agent.validate_design(arch_description)

        logger.info("✅ Validation completed")

        return AgentResponse(
            success=True,
            message="Architecture validated",
            data={"validation": str(response)},
            reasoning=str(response)
        )

    except Exception as e:
        logger.error(f"Error validating architecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cloud/compare/{service_name}", response_model=AgentResponse)
async def compare_cloud_services(
    service_name: str,
    agent: ArchitectureAgent = Depends(get_agent)
):
    """
    Compare a service across AWS, Azure, and GCP
    """
    try:
        logger.info(f"Comparing service: {service_name}")

        response = agent.compare_providers(service_name)

        return AgentResponse(
            success=True,
            message=f"Comparison for {service_name}",
            data={"comparison": str(response)},
            reasoning=str(response)
        )

    except Exception as e:
        logger.error(f"Error comparing services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=AgentResponse)
async def chat_with_agent(
    question: dict,
    agent: ArchitectureAgent = Depends(get_agent)
):
    """
    Ask the AI agent a question about cloud architecture
    """
    try:
        user_question = question.get("question", "")
        context = question.get("context", None)

        logger.info(f"Chat question: {user_question[:50]}...")

        response = agent.answer_question(user_question, context)

        return AgentResponse(
            success=True,
            message="Response from AI agent",
            data={"answer": str(response)},
            reasoning=str(response)
        )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/code/generate", response_model=AgentResponse)
async def generate_infrastructure_code(
    request: dict
):
    """
    Generate Infrastructure as Code (Terraform or CloudFormation) based on architecture
    """
    try:
        import boto3
        import json

        architecture = request.get("architecture")
        code_type = request.get("code_type", "terraform")  # "terraform" or "cloudformation"

        logger.info(f"\n{'='*80}")
        logger.info(f"💻 CODE GENERATION REQUEST")
        logger.info(f"{'='*80}")
        logger.info(f"Code Type: {code_type.upper()}")
        logger.info(f"Provider: {architecture.get('provider', 'aws')}")
        logger.info(f"Components: {len(architecture.get('components', []))}")

        # Create prompt for code generation
        components_desc = "\n".join([
            f"- {comp.get('name', 'Unknown')}: {comp.get('description', '')}"
            for comp in architecture.get('components', [])
        ])

        prompt = f"""Generate complete, production-ready {code_type.upper()} code for this cloud architecture:

Provider: {architecture.get('provider', 'aws')}
Architecture: {architecture.get('name', 'Cloud Architecture')}

Components:
{components_desc}

Requirements:
- Include all necessary resources
- Add proper security configurations
- Include networking setup (VPC, subnets, security groups)
- Add resource tags for organization
- Include output variables for important endpoints
- Follow best practices for {architecture.get('provider', 'aws')}
- Keep the code concise and well-commented

Return ONLY the {code_type} code, no additional explanation."""

        # Use direct Bedrock API call to avoid conversation history buildup
        bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'))

        model_id = os.getenv('BEDROCK_MODEL_ID', 'us.anthropic.claude-sonnet-4-20250514-v1:0')

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,  # Limit response length
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        code_response = response_body['content'][0]['text']

        logger.info(f"✅ Code generated successfully (length: {len(code_response)} chars)")
        logger.info(f"{'='*80}\n")

        return AgentResponse(
            success=True,
            message=f"{code_type.capitalize()} code generated successfully",
            data={
                "code": str(code_response),
                "code_type": code_type,
                "provider": architecture.get('provider', 'aws')
            },
            reasoning=str(code_response)
        )

    except Exception as e:
        logger.error(f"❌ Error generating code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deploy", response_model=AgentResponse)
async def deploy_architecture(
    request: dict,
    agent: ArchitectureAgent = Depends(get_agent)
):
    """
    Deploy architecture to cloud provider (simulation for hackathon)
    """
    try:
        architecture = request.get("architecture")
        config = request.get("config", {})

        provider = config.get("provider", architecture.get("provider", "aws"))
        region = config.get("region", "us-west-2")
        stack_name = config.get("stack_name", "skyrchitect-stack")

        logger.info(f"Deploying to {provider} in {region}...")

        # For hackathon: simulate deployment with AI-generated deployment plan
        deployment_prompt = f"""
Create a detailed deployment plan for the following architecture:

Provider: {provider}
Region: {region}
Stack Name: {stack_name}
Architecture: {architecture.get('name', 'Cloud Architecture')}

Components: {len(architecture.get('components', []))} resources

Generate a step-by-step deployment plan including:
1. Pre-deployment checks
2. Resource creation order
3. Configuration steps
4. Post-deployment validation
5. Estimated deployment time

Format as deployment logs with timestamps.
"""

        deployment_plan = agent.answer_question(deployment_prompt)

        # Simulate deployment logs
        logs = [
            f"[INFO] Initializing deployment to {provider}...",
            f"[INFO] Region: {region}",
            f"[INFO] Stack: {stack_name}",
            "[INFO] Validating architecture configuration...",
            "[SUCCESS] Configuration validated",
            "[INFO] Creating VPC and networking resources...",
            "[SUCCESS] Network infrastructure created",
            "[INFO] Deploying compute resources...",
            "[SUCCESS] Compute resources deployed",
            "[INFO] Configuring storage services...",
            "[SUCCESS] Storage configured",
            "[INFO] Setting up databases...",
            "[SUCCESS] Database instances created",
            "[INFO] Finalizing deployment...",
            "[SUCCESS] Deployment completed successfully!",
            f"[INFO] Access URL: https://{provider}-app-{stack_name}.example.com"
        ]

        return AgentResponse(
            success=True,
            message="Deployment completed successfully",
            data={
                "status": "success",
                "deployment_logs": logs,
                "deployment_plan": str(deployment_plan),
                "endpoint": f"https://{provider}-app-{stack_name}.example.com",
                "provider": provider,
                "region": region
            },
            reasoning=str(deployment_plan)
        )

    except Exception as e:
        logger.error(f"Error deploying architecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn backend.api.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
