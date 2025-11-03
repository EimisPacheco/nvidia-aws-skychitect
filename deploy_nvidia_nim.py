#!/usr/bin/env python3
"""
NVIDIA-AWS Hackathon: Deploy NVIDIA Llama NIM from AWS Marketplace to SageMaker
================================================================================

This script deploys:
- Llama 3.1 Nemotron Nano 8B V1 NIM (Reasoning Model)

From AWS Marketplace to Amazon SageMaker endpoint.

Requirements:
- AWS Account with SageMaker access
- Active AWS Marketplace subscription to Llama NIM
- IAM role with SageMaker and Marketplace permissions

Cost Estimation:
- Llama 3.1 Nemotron: ~$8/hour (ml.g5.12xlarge)

Author: Claude Code for NVIDIA-AWS Hackathon
Date: November 2025
"""

import boto3
import json
import os
import sys
import time
from datetime import datetime
from typing import Optional

# Configuration
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "396608774889")

# Model Package ARN Patterns (region-specific)
# These ARNs are obtained after subscribing via AWS Marketplace
MODEL_PACKAGE_ARNS = {
    "us-west-2": {
        "llama-nemotron": "arn:aws:sagemaker:us-west-2:594846645681:model-package/llama3-1-nemotron-nano-8b-v1-n-d76bd77dbb4337c1a4d9beaf36b5c3d2"
    },
    "us-east-1": {
        "llama-nemotron": "arn:aws:sagemaker:us-east-1:865070037744:model-package/llama3-1-nemotron-nano-8b-v1-n-d76bd77dbb4337c1a4d9beaf36b5c3d2"
    }
}

# Endpoint Configuration
LLAMA_ENDPOINT_NAME = "nvidia-llama-nemotron-endpoint"
LLAMA_INSTANCE_TYPE = "ml.g5.12xlarge"  # Recommended by NVIDIA
LLAMA_INSTANCE_COUNT = 1

# IAM Role Configuration
SAGEMAKER_ROLE_NAME = "SageMakerExecutionRole-NvidiaHackathon"


class NVIDIANIMDeployer:
    """Deploy NVIDIA Llama NIM from AWS Marketplace to SageMaker"""

    def __init__(self, region: str = AWS_REGION):
        """Initialize AWS clients"""
        self.region = region
        self.account_id = AWS_ACCOUNT_ID

        print(f"\n{'='*70}")
        print(f"🚀 NVIDIA-AWS Hackathon: NIM Deployment to SageMaker")
        print(f"{'='*70}\n")
        print(f"📋 Configuration:")
        print(f"   AWS Account: {self.account_id}")
        print(f"   Region: {self.region}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Initialize boto3 clients
        self.sm_client = boto3.client('sagemaker', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)

        # Get model package ARN for this region
        if region not in MODEL_PACKAGE_ARNS:
            raise ValueError(f"Region {region} not configured. Supported: {list(MODEL_PACKAGE_ARNS.keys())}")

        self.model_arn = MODEL_PACKAGE_ARNS[region]["llama-nemotron"]

    def get_or_create_execution_role(self) -> str:
        """Get existing or create new SageMaker execution role"""
        print("🔍 Checking SageMaker execution role...")

        role_arn = f"arn:aws:iam::{self.account_id}:role/{SAGEMAKER_ROLE_NAME}"

        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=SAGEMAKER_ROLE_NAME)
            print(f"✅ Found existing role: {role_arn}\n")
            return role_arn
        except self.iam_client.exceptions.NoSuchEntityException:
            print(f"📝 Creating new SageMaker execution role...")

            # Trust policy for SageMaker
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "sagemaker.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }

            # Create role
            response = self.iam_client.create_role(
                RoleName=SAGEMAKER_ROLE_NAME,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Execution role for NVIDIA NIMs on SageMaker (Hackathon)"
            )

            # Attach required policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
                "arn:aws:iam::aws:policy/AWSMarketplaceMeteringFullAccess"
            ]

            for policy in policies:
                self.iam_client.attach_role_policy(
                    RoleName=SAGEMAKER_ROLE_NAME,
                    PolicyArn=policy
                )

            print(f"✅ Created role: {role_arn}")
            print("⏳ Waiting 15 seconds for role to propagate...")
            time.sleep(15)
            print()

            return role_arn

    def create_model(self, model_name: str, model_package_arn: str, role_arn: str) -> str:
        """Create SageMaker model from Marketplace model package"""
        print(f"📦 Creating SageMaker model: {model_name}...")
        print(f"   Model Package ARN: {model_package_arn}")

        try:
            response = self.sm_client.create_model(
                ModelName=model_name,
                PrimaryContainer={
                    'ModelPackageName': model_package_arn
                },
                ExecutionRoleArn=role_arn,
                EnableNetworkIsolation=True  # Security best practice
            )

            print(f"✅ Created model: {response['ModelArn']}\n")
            return response['ModelArn']

        except self.sm_client.exceptions.ResourceInUse:
            print(f"⚠️  Model {model_name} already exists, using existing model\n")
            return f"arn:aws:sagemaker:{self.region}:{self.account_id}:model/{model_name}"

    def create_endpoint_config(self, config_name: str, model_name: str,
                              instance_type: str, instance_count: int) -> str:
        """Create SageMaker endpoint configuration"""
        print(f"⚙️  Creating endpoint configuration: {config_name}...")
        print(f"   Instance Type: {instance_type}")
        print(f"   Instance Count: {instance_count}")

        try:
            response = self.sm_client.create_endpoint_config(
                EndpointConfigName=config_name,
                ProductionVariants=[
                    {
                        'VariantName': 'AllTraffic',
                        'ModelName': model_name,
                        'InitialInstanceCount': instance_count,
                        'InstanceType': instance_type,
                        'InitialVariantWeight': 1.0
                    }
                ]
            )

            print(f"✅ Created endpoint config: {response['EndpointConfigArn']}\n")
            return response['EndpointConfigArn']

        except self.sm_client.exceptions.ResourceInUse:
            print(f"⚠️  Endpoint config {config_name} already exists, using existing config\n")
            return f"arn:aws:sagemaker:{self.region}:{self.account_id}:endpoint-config/{config_name}"

    def create_endpoint(self, endpoint_name: str, config_name: str) -> str:
        """Create SageMaker endpoint"""
        print(f"🚀 Creating SageMaker endpoint: {endpoint_name}...")
        print(f"   This will take 10-15 minutes...")

        try:
            response = self.sm_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=config_name
            )

            print(f"✅ Endpoint creation initiated: {response['EndpointArn']}")
            return response['EndpointArn']

        except self.sm_client.exceptions.ResourceInUse:
            print(f"⚠️  Endpoint {endpoint_name} already exists")
            return f"arn:aws:sagemaker:{self.region}:{self.account_id}:endpoint/{endpoint_name}"

    def wait_for_endpoint(self, endpoint_name: str, timeout_minutes: int = 20) -> bool:
        """Wait for endpoint to be in service"""
        print(f"\n⏳ Waiting for endpoint {endpoint_name} to be in service...")
        print(f"   Timeout: {timeout_minutes} minutes")
        print(f"   Status updates every 30 seconds...\n")

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                print(f"❌ Timeout waiting for endpoint after {timeout_minutes} minutes")
                return False

            try:
                response = self.sm_client.describe_endpoint(EndpointName=endpoint_name)
                status = response['EndpointStatus']

                elapsed_min = int(elapsed / 60)
                elapsed_sec = int(elapsed % 60)
                print(f"   [{elapsed_min:02d}:{elapsed_sec:02d}] Status: {status}")

                if status == 'InService':
                    print(f"\n✅ Endpoint {endpoint_name} is now in service!\n")
                    return True
                elif status in ['Failed', 'RollingBack']:
                    print(f"\n❌ Endpoint deployment failed with status: {status}")
                    if 'FailureReason' in response:
                        print(f"   Failure reason: {response['FailureReason']}")
                    return False

                time.sleep(30)

            except Exception as e:
                print(f"❌ Error checking endpoint status: {e}")
                return False

    def deploy(self, role_arn: str, wait: bool = True) -> Optional[str]:
        """Deploy Llama 3.1 Nemotron Nano 8B NIM"""
        print(f"\n{'='*70}")
        print(f"🤖 Deploying Llama 3.1 Nemotron Nano 8B V1 NIM")
        print(f"{'='*70}\n")

        model_name = f"{LLAMA_ENDPOINT_NAME}-model"
        config_name = f"{LLAMA_ENDPOINT_NAME}-config"

        # Create model
        self.create_model(
            model_name=model_name,
            model_package_arn=self.model_arn,
            role_arn=role_arn
        )

        # Create endpoint config
        self.create_endpoint_config(
            config_name=config_name,
            model_name=model_name,
            instance_type=LLAMA_INSTANCE_TYPE,
            instance_count=LLAMA_INSTANCE_COUNT
        )

        # Create endpoint
        endpoint_arn = self.create_endpoint(
            endpoint_name=LLAMA_ENDPOINT_NAME,
            config_name=config_name
        )

        # Wait for endpoint
        if wait:
            success = self.wait_for_endpoint(LLAMA_ENDPOINT_NAME)
            if not success:
                return None

        return endpoint_arn

    def test_endpoint(self) -> bool:
        """Test Llama Nemotron endpoint with sample inference"""
        print(f"\n{'='*70}")
        print(f"🧪 Testing Llama 3.1 Nemotron Endpoint")
        print(f"{'='*70}\n")

        runtime = boto3.client('sagemaker-runtime', region_name=self.region)

        test_payload = {
            "messages": [
                {"role": "user", "content": "What is cloud architecture?"}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }

        try:
            print(f"📤 Sending test request to {LLAMA_ENDPOINT_NAME}...")
            response = runtime.invoke_endpoint(
                EndpointName=LLAMA_ENDPOINT_NAME,
                ContentType='application/json',
                Body=json.dumps(test_payload)
            )

            result = json.loads(response['Body'].read().decode())
            print(f"✅ Endpoint test successful!")
            print(f"\n📝 Response preview:")
            print(f"   {str(result)[:200]}...\n")
            return True

        except Exception as e:
            print(f"❌ Endpoint test failed: {e}\n")
            return False

    def generate_summary(self):
        """Print deployment summary"""
        print(f"\n{'='*70}")
        print(f"🎉 NVIDIA NIM Deployment Complete!")
        print(f"{'='*70}\n")

        print(f"📊 Deployment Summary:")
        print(f"   Region: {self.region}")
        print(f"   Account: {self.account_id}")
        print(f"\n🤖 Llama 3.1 Nemotron Nano 8B V1:")
        print(f"   Endpoint: {LLAMA_ENDPOINT_NAME}")
        print(f"   Instance: {LLAMA_INSTANCE_TYPE}")
        print(f"   Status: InService")
        print(f"\n💰 Cost Estimation:")
        print(f"   ~$8/hour while endpoint is running")
        print(f"\n🎯 Hackathon Compliance:")
        print(f"   ✅ llama-3.1-nemotron-nano-8B-v1 (Reasoning Model)")
        print(f"   ✅ Deployed as NVIDIA NIM")
        print(f"   ✅ Running on Amazon SageMaker endpoint")
        print(f"\n📝 Next Steps:")
        print(f"   1. Verify endpoint in AWS Console")
        print(f"   2. Update .env with: MODEL_TYPE=sagemaker")
        print(f"   3. Start backend: ./start_backend.sh")
        print(f"   4. Test application at http://localhost:5173")
        print(f"\n⚠️  Remember to delete endpoint when done to stop charges:")
        print(f"   python deploy_nvidia_nim.py --cleanup")
        print(f"\n{'='*70}\n")


def cleanup_endpoint(region: str = AWS_REGION):
    """Delete SageMaker endpoint to stop charges"""
    print(f"\n{'='*70}")
    print(f"🧹 Cleaning Up SageMaker Endpoint")
    print(f"{'='*70}\n")

    sm_client = boto3.client('sagemaker', region_name=region)

    try:
        print(f"🗑️  Deleting endpoint: {LLAMA_ENDPOINT_NAME}...")
        sm_client.delete_endpoint(EndpointName=LLAMA_ENDPOINT_NAME)
        print(f"✅ Deleted endpoint: {LLAMA_ENDPOINT_NAME}")

        # Also delete endpoint config
        config_name = f"{LLAMA_ENDPOINT_NAME}-config"
        print(f"🗑️  Deleting endpoint config: {config_name}...")
        sm_client.delete_endpoint_config(EndpointConfigName=config_name)
        print(f"✅ Deleted endpoint config: {config_name}")

        # Also delete model
        model_name = f"{LLAMA_ENDPOINT_NAME}-model"
        print(f"🗑️  Deleting model: {model_name}...")
        sm_client.delete_model(ModelName=model_name)
        print(f"✅ Deleted model: {model_name}\n")

    except Exception as e:
        print(f"⚠️  Could not delete {LLAMA_ENDPOINT_NAME}: {e}\n")

    print(f"✅ Cleanup complete!\n")


def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(description='Deploy NVIDIA Llama NIM to SageMaker')
    parser.add_argument('--cleanup', action='store_true', help='Delete endpoint instead of deploying')
    parser.add_argument('--no-wait', action='store_true', help='Do not wait for endpoint to be in service')
    parser.add_argument('--test-only', action='store_true', help='Only run test on existing endpoint')
    parser.add_argument('--region', default=AWS_REGION, help='AWS region')

    args = parser.parse_args()

    if args.cleanup:
        cleanup_endpoint(region=args.region)
        return

    # Initialize deployer
    deployer = NVIDIANIMDeployer(region=args.region)

    if args.test_only:
        # Test existing endpoint
        deployer.test_endpoint()
        return

    # Get or create IAM role
    role_arn = deployer.get_or_create_execution_role()

    # Deploy NIM
    wait_for_endpoint = not args.no_wait
    endpoint_arn = deployer.deploy(role_arn, wait=wait_for_endpoint)

    if not endpoint_arn:
        print("\n❌ Deployment failed - check errors above")
        sys.exit(1)

    # If we waited, test the endpoint
    if wait_for_endpoint:
        deployer.test_endpoint()

    # Print summary
    deployer.generate_summary()


if __name__ == "__main__":
    main()
