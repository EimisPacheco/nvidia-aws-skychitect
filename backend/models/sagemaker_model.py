"""SageMaker Model Adapter for NVIDIA NIMs - Strands Compatible"""

import boto3
import json
import os
from typing import Optional, Dict, Any, List

class SageMakerNIMModel:
    """
    Strands-compatible model that calls SageMaker endpoint with Llama 3.1 Nemotron NIM

    This adapter allows using NVIDIA NIMs deployed on SageMaker with the Strands Agent framework.
    """

    def __init__(
        self,
        endpoint_name: str = None,
        region_name: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        streaming: bool = False
    ):
        """
        Initialize SageMaker NIM Model

        Args:
            endpoint_name: SageMaker endpoint name (e.g., 'llama-nemotron-endpoint')
            region_name: AWS region (e.g., 'us-west-2')
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            streaming: Enable streaming responses (not yet supported)
        """
        self.endpoint_name = endpoint_name or os.getenv(
            "SAGEMAKER_ENDPOINT_NAME",
            "llama-nemotron-endpoint"
        )
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "us-west-2")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming

        # Initialize SageMaker runtime client
        self.runtime = boto3.client(
            'sagemaker-runtime',
            region_name=self.region_name
        )

        print(f"✅ SageMaker NIM Model initialized: {self.endpoint_name} in {self.region_name}")

    def __call__(self, prompt: str, **kwargs) -> str:
        """
        Call SageMaker endpoint with NVIDIA NIM format

        This method is called by Strands Agent framework.

        Args:
            prompt: User prompt or system+user prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text from Llama 3.1 Nemotron
        """
        try:
            # Prepare request payload (NVIDIA NIM format compatible with Llama)
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": False  # Streaming not yet implemented
            }

            print(f"📤 Sending request to SageMaker endpoint: {self.endpoint_name}")
            print(f"   Prompt length: {len(prompt)} chars")

            # Invoke SageMaker endpoint
            response = self.runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )

            # Parse response
            result = json.loads(response['Body'].read().decode())

            print(f"📥 Received response from SageMaker")

            # Extract text from NVIDIA NIM response format
            # Format: {"choices": [{"message": {"content": "..."}}]}
            if 'choices' in result and len(result['choices']) > 0:
                generated_text = result['choices'][0]['message']['content']
                print(f"✅ Generated {len(generated_text)} chars")
                return generated_text

            # Fallback for different response formats
            if 'generated_text' in result:
                return result['generated_text']

            print(f"⚠️ Unexpected response format, returning raw result")
            return str(result)

        except Exception as e:
            print(f"❌ Error calling SageMaker endpoint: {e}")
            raise RuntimeError(f"SageMaker inference failed: {str(e)}")

    def get_model_id(self) -> str:
        """Get model identifier for logging"""
        return f"sagemaker:{self.endpoint_name}"

    def invoke_with_messages(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Invoke with chat messages format

        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        try:
            payload = {
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", 0.9),
            }

            response = self.runtime.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )

            result = json.loads(response['Body'].read().decode())

            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']

            return str(result)

        except Exception as e:
            raise RuntimeError(f"SageMaker inference failed: {str(e)}")


def get_sagemaker_model(
    endpoint_name: Optional[str] = None,
    region: Optional[str] = None,
    temperature: float = 0.7
) -> SageMakerNIMModel:
    """
    Factory function to create SageMaker NIM model

    Args:
        endpoint_name: SageMaker endpoint name
        region: AWS region
        temperature: Sampling temperature

    Returns:
        SageMakerNIMModel instance
    """
    return SageMakerNIMModel(
        endpoint_name=endpoint_name,
        region_name=region,
        temperature=temperature
    )
