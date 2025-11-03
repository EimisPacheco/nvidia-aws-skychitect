"""Strands Agent for Cloud Architecture - SageMaker/NVIDIA NIM Version

This version uses:
- Llama 3.1 Nemotron Nano 8B (NVIDIA NIM on SageMaker)
- Custom cloud architecture tools

Required for NVIDIA-AWS Hackathon.
"""

import os
from typing import Optional
from strands import Agent
from backend.models.sagemaker_model import SageMakerNIMModel
from backend.tools.cloud_tools import (
    get_aws_service_info,
    calculate_architecture_cost,
    suggest_cost_optimization,
    get_service_alternatives,
    validate_architecture
)


class ArchitectureAgentSageMaker:
    """
    AI Agent for cloud architecture design using NVIDIA Llama NIM on SageMaker

    Features:
    - Llama 3.1 Nemotron Nano 8B for architecture generation
    - Custom tools for cloud service information and cost calculation
    """

    def __init__(
        self,
        llm_endpoint: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize with SageMaker endpoint

        Args:
            llm_endpoint: SageMaker endpoint for Llama 3.1 Nemotron
            region: AWS region
        """
        self.region = region or os.getenv("AWS_DEFAULT_REGION", "us-west-2")

        print(f"\n{'='*80}")
        print(f"🚀 Initializing Architecture Agent (NVIDIA-AWS Hackathon Version)")
        print(f"{'='*80}")

        # Initialize NVIDIA Llama 3.1 Nemotron NIM on SageMaker
        self.model = SageMakerNIMModel(
            endpoint_name=llm_endpoint or os.getenv("SAGEMAKER_ENDPOINT_NAME"),
            region_name=self.region,
            temperature=0.7,
            streaming=False
        )

        # System prompt for architecture agent
        system_prompt = """You are an expert cloud architecture AI agent specialized in AWS, Azure, and Google Cloud Platform.

Your role is to help users design optimal, secure, and cost-effective cloud architectures.

Key Responsibilities:
1. Analyze user requirements and recommend appropriate cloud services
2. Design complete architectures with proper service connections
3. Estimate costs accurately using your tools
4. Suggest cost optimizations and alternatives
5. Validate architectures for best practices and security
6. Provide clear reasoning for your recommendations

Available Tools:
- get_aws_service_info: Get details about AWS services
- calculate_architecture_cost: Calculate total architecture cost
- suggest_cost_optimization: Find cost-saving alternatives
- get_service_alternatives: Get equivalent services across cloud providers
- validate_architecture: Check architecture for best practices

Guidelines:
- Always use tools to get accurate service information and costs
- Provide specific, actionable recommendations
- Consider security, scalability, and cost in all designs
- Explain trade-offs between different approaches
- Follow cloud best practices (high availability, disaster recovery, monitoring)

CRITICAL OUTPUT FORMAT:
You MUST return your response in this EXACT JSON structure, followed by detailed markdown reasoning:

```json
{
  "architecture": {
    "title": "Project Title",
    "description": "Brief project description",
    "provider": "aws|azure|gcp",
    "total_cost": 229.00,
    "services": [
      {
        "id": "service-1",
        "name": "EC2 Instance",
        "type": "compute",
        "cost": 29.20,
        "description": "Primary application server",
        "icon": "server",
        "position": {"x": 300, "y": 200}
      }
    ],
    "connections": [
      {"from": "service-1", "to": "service-2", "type": "HTTP/HTTPS"}
    ],
    "alternatives": [
      {
        "service_id": "service-1",
        "alternative_name": "EC2 t3.small",
        "cost": 14.60,
        "savings": 14.60,
        "performance": 70,
        "description": "Smaller instance size"
      }
    ]
  }
}
```

IMPORTANT NODE POSITIONING RULES:
- Space nodes FAR APART to prevent visual clutter
- Minimum horizontal spacing: 400 pixels
- Minimum vertical spacing: 300 pixels
- Arrange in logical layers (frontend, backend, data)

Then provide detailed markdown explanation with:
- Architecture overview
- Security best practices
- Cost breakdown
- Optimization recommendations
- Implementation steps"""

        # Create agent with SageMaker model and tools
        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            tools=[
                get_aws_service_info,
                calculate_architecture_cost,
                suggest_cost_optimization,
                get_service_alternatives,
                validate_architecture
            ]
        )

        print(f"✅ Agent initialized with NVIDIA Llama 3.1 Nemotron Nano 8B")
        print(f"   - Tools: 5 cloud architecture tools")
        print(f"{'='*80}\n")

    def generate_architecture(self, requirements: str) -> str:
        """
        Generate architecture based on requirements

        Args:
            requirements: User's architecture requirements

        Returns:
            Agent's architecture recommendation with JSON and reasoning
        """
        print(f"\n{'='*60}")
        print(f"🏗️ ARCHITECTURE GENERATION")
        print(f"{'='*60}")
        print(f"Requirements: {requirements[:100]}...")

        prompt = f"""Design a cloud architecture based on these requirements:

{requirements}

Please:
1. Recommend specific AWS services (use get_aws_service_info for details)
2. Calculate the total cost (use calculate_architecture_cost)
3. Suggest how services should connect
4. Validate the architecture (use validate_architecture)
5. Provide security best practices
6. Suggest cost optimizations if possible

Be specific and provide a complete, production-ready architecture."""

        print(f"\n🤖 Calling Llama 3.1 Nemotron on SageMaker...")

        # Call agent
        response = self.agent(prompt)

        print(f"✅ Architecture generated successfully")
        print(f"{'='*60}\n")

        return response

    def optimize_architecture(self, current_architecture: str, optimization_goal: str) -> str:
        """
        Optimize existing architecture

        Args:
            current_architecture: Description of current architecture
            optimization_goal: 'cost', 'performance', or 'balanced'

        Returns:
            Optimization recommendations
        """
        print(f"\n{'='*60}")
        print(f"⚡ ARCHITECTURE OPTIMIZATION")
        print(f"{'='*60}")
        print(f"Goal: {optimization_goal}")

        prompt = f"""Analyze and optimize this architecture with goal: {optimization_goal}

Current Architecture:
{current_architecture}

Please:
1. Identify optimization opportunities using suggest_cost_optimization
2. Calculate potential savings
3. Suggest alternative services where beneficial
4. Maintain or improve performance
5. Ensure security is not compromised
6. Provide implementation steps

Focus on practical, high-impact optimizations."""

        print(f"\n🤖 Calling Llama 3.1 Nemotron on SageMaker...")
        response = self.agent(prompt)

        print(f"✅ Optimization completed")
        print(f"{'='*60}\n")

        return response

    def validate_design(self, architecture_description: str) -> str:
        """
        Validate architecture design

        Args:
            architecture_description: Architecture to validate

        Returns:
            Validation results with recommendations
        """
        prompt = f"""Validate this cloud architecture design:

{architecture_description}

Use the validate_architecture tool and provide:
1. Validation results
2. Security concerns
3. Scalability issues
4. Best practice violations
5. Recommended improvements
6. Priority of each issue"""

        return self.agent(prompt)

    def compare_providers(self, service_name: str) -> str:
        """
        Compare a service across cloud providers

        Args:
            service_name: Service to compare

        Returns:
            Comparison across AWS, Azure, GCP
        """
        prompt = f"""Compare the service "{service_name}" across AWS, Azure, and Google Cloud.

Use get_service_alternatives tool and provide:
1. Equivalent services in each cloud
2. Key feature differences
3. Cost comparison (if available)
4. When to choose each provider
5. Migration considerations"""

        return self.agent(prompt)

    def answer_question(self, question: str, context: Optional[str] = None) -> str:
        """
        Answer general architecture questions

        Args:
            question: User's question
            context: Optional context about their architecture

        Returns:
            Agent's answer
        """
        if context:
            prompt = f"""Context: {context}

Question: {question}

Provide a clear, practical answer using tools if needed."""
        else:
            prompt = question

        return self.agent(prompt)


# Singleton instance
_agent_instance_sagemaker: Optional[ArchitectureAgentSageMaker] = None


def get_architecture_agent_sagemaker() -> ArchitectureAgentSageMaker:
    """Get or create the SageMaker architecture agent singleton"""
    global _agent_instance_sagemaker

    if _agent_instance_sagemaker is None:
        _agent_instance_sagemaker = ArchitectureAgentSageMaker()

    return _agent_instance_sagemaker
