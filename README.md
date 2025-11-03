# Skyrchitect AI - Cloud Architecture Agent

**AI-powered cloud architecture design platform** using NVIDIA Llama 3.1 Nemotron Nano 8B on Amazon SageMaker.

Generate production-ready AWS architectures from natural language descriptions using autonomous AI agents.

---

## ✨ Features

### 🤖 AI-Powered Architecture Generation
- **Natural Language Input**: Describe your needs in plain English
- **NVIDIA Llama 3.1 Nemotron Nano 8B**: Advanced reasoning model on SageMaker
- **Autonomous Tool Use**: Agent decides which tools to use and when
- **Multi-Cloud Support**: AWS, Azure, and Google Cloud Platform

### 🛠️ 5 Specialized Tools
1. **AWS Service Info**: Get details about AWS services
2. **Cost Calculator**: Estimate infrastructure costs
3. **Cost Optimizer**: Find cost-saving alternatives
4. **Service Comparison**: Compare services across cloud providers
5. **Architecture Validator**: Check designs for best practices

### 🎨 Interactive Visual Diagrams
- **React Flow Integration**: Professional node-based architecture diagrams
- **Real-time Rendering**: Instant visualization of AI-generated architectures
- **Component Details**: Hover for costs, descriptions, and configurations
- **Export & Share**: Save diagrams and share with your team

### 💻 Code Generation
- **Terraform Support**: Generate production-ready Terraform code
- **CloudFormation**: AWS CloudFormation template generation
- **AI-Powered**: Llama generates optimized IaC code

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.13+
- AWS Account with SageMaker access
- Active AWS Marketplace subscription to Llama 3.1 Nemotron Nano 8B

### Installation

```bash
# 1. Clone repository
git clone <your-repo>
cd project

# 2. Install frontend dependencies
npm install

# 3. Install backend dependencies (auto-handled by start script)
# Virtual environment will be created automatically
```

### AWS Setup

1. **Subscribe to NVIDIA Llama NIM** (5 minutes)
   - Visit: https://aws.amazon.com/marketplace/pp/prodview-6wde2hzvft7y4
   - Click "Continue to Subscribe" → "Accept Offer"
   - Subscription is FREE (pay only when endpoint runs)

2. **Deploy to SageMaker** (15-20 minutes)
   ```bash
   # Set AWS credentials
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-west-2
   export AWS_ACCOUNT_ID=your_account_id

   # Activate virtual environment
   source venv/bin/activate

   # Deploy NVIDIA NIM
   python deploy_nvidia_nim.py
   ```

3. **Configure .env**
   ```bash
   MODEL_TYPE=sagemaker
   SAGEMAKER_ENDPOINT_NAME=nvidia-llama-nemotron-endpoint
   AWS_DEFAULT_REGION=us-west-2
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   ```

### Running the Application

```bash
# Terminal 1: Start backend
./start_backend.sh

# Terminal 2: Start frontend
npm run dev

# Open browser
http://localhost:5173
```

---

## 🏗️ Architecture

### Tech Stack

**AI/ML:**
- NVIDIA Llama 3.1 Nemotron Nano 8B (reasoning model)
- Amazon SageMaker (AI endpoint deployment)
- Strands Agents (autonomous agent framework)

**Backend:**
- Python 3.13
- FastAPI (web framework)
- Boto3 (AWS SDK)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Flow (diagrams)

### Project Structure
```
project/
├── src/                          # Frontend (React + TypeScript)
│   ├── components/               # UI components
│   ├── pages/                    # Route pages
│   ├── services/                 # API client
│   └── types/                    # TypeScript types
│
├── backend/                      # Python Backend
│   ├── api/
│   │   └── main.py              # FastAPI routes
│   ├── agents/
│   │   ├── architecture_agent.py              # Bedrock agent (original)
│   │   └── architecture_agent_sagemaker.py    # SageMaker agent (NVIDIA)
│   ├── models/
│   │   └── sagemaker_model.py   # SageMaker adapter
│   ├── tools/
│   │   └── cloud_tools.py       # 5 architecture tools
│   └── utils/                    # Utilities
│
├── deploy_nvidia_nim.py          # Deploy Llama to SageMaker
├── start_backend.sh              # Start backend script
└── README.md                     # This file
```

---

## 🎮 Usage

### Creating an AI-Generated Architecture

1. **Describe Requirements**
   ```
   "E-commerce platform with 100k users, high availability,
   auto-scaling, and cost optimization"
   ```

2. **AI Agent Works Autonomously**
   - Analyzes requirements
   - Calls tools as needed (get AWS info, calculate costs)
   - Reasons about best architecture
   - Generates complete design

3. **Review Architecture**
   - Interactive diagram shows all components
   - See connections between services
   - Review estimated costs
   - Check configuration details

4. **Generate Code**
   - Click "Generate Code"
   - Choose Terraform or CloudFormation
   - Download and deploy to AWS

### Example Prompts

```
"Microservices architecture for social media app with 50k users,
using containers, managed database, and CDN"

"Serverless API with Lambda, DynamoDB, API Gateway,
optimized for cost under $200/month"

"High-availability e-commerce with auto-scaling, load balancer,
RDS, and Redis cache"
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Model Backend Selection
MODEL_TYPE=sagemaker              # 'sagemaker' or 'bedrock'

# SageMaker Configuration (NVIDIA NIM)
SAGEMAKER_ENDPOINT_NAME=nvidia-llama-nemotron-endpoint
SAGEMAKER_REGION=us-west-2

# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-west-2
AWS_ACCOUNT_ID=your_account_id

# Bedrock Configuration (alternative backend)
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0
```

### Dual Backend Support

Switch between NVIDIA NIMs and AWS Bedrock:

```bash
# Use NVIDIA Llama on SageMaker (NVIDIA-AWS Hackathon)
MODEL_TYPE=sagemaker

# Use Claude Sonnet 4 on Bedrock (AWS AI Agent Hackathon)
MODEL_TYPE=bedrock
```

---

## 💰 Cost Management

### SageMaker Endpoint Costs

**While running:**
- Llama endpoint: ~$8/hour (ml.g5.12xlarge)

**To stop charges:**
```bash
python deploy_nvidia_nim.py --cleanup
```

**AWS Marketplace subscription:** FREE (no charges unless endpoint runs)

---

## 🛠️ Development

### Backend Development

```bash
# Start backend with auto-reload
./start_backend.sh

# Test endpoint
python deploy_nvidia_nim.py --test-only

# Check logs
# Backend logs appear in terminal
```

### Frontend Development

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/api/architecture/generate` | POST | Generate architecture |
| `/api/architecture/optimize` | POST | Optimize existing architecture |
| `/api/architecture/validate` | POST | Validate architecture design |
| `/api/cloud/compare/{service}` | GET | Compare cloud services |
| `/api/chat` | POST | Chat with agent |
| `/api/code/generate` | POST | Generate IaC code |
| `/api/deploy` | POST | Deploy simulation |

---

## 🎯 NVIDIA-AWS Hackathon

This project demonstrates:

### Requirements Met
✅ **llama-3.1-nemotron-nano-8B-v1** (reasoning model)
✅ **Deployed as NVIDIA NIM** (inference microservice)
✅ **Amazon SageMaker AI endpoint** (managed deployment)
✅ **Agentic Application** (autonomous tool use, multi-step reasoning)

### Key Features
- **Autonomous Agent**: Decides which tools to use and when
- **Tool Calling**: 5 specialized cloud architecture tools
- **Multi-Step Reasoning**: Breaks down complex requirements
- **Production Ready**: Clean code, error handling, monitoring

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start - port in use:**
```bash
./kill_port.sh
./start_backend.sh
```

**Module not found errors:**
```bash
# Recreate virtual environment
rm -rf venv
./start_backend.sh
```

**SageMaker endpoint not found:**
```bash
# Deploy endpoint first
python deploy_nvidia_nim.py
```

**Frontend can't connect to backend:**
- Check backend is running on port 8000
- Verify CORS settings in backend/api/main.py

---

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Detailed project structure
- **[ARCHITECTURE_EXPLAINED.md](ARCHITECTURE_EXPLAINED.md)** - System architecture

---

## 🔐 Security

- **Input Validation**: Comprehensive client and server validation
- **XSS Protection**: Content Security Policy enabled
- **Environment Variables**: Sensitive data in .env (gitignored)
- **Network Isolation**: SageMaker endpoints with network isolation

---

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## 🙏 Acknowledgments

- **NVIDIA**: Llama 3.1 Nemotron Nano 8B model
- **AWS**: SageMaker, Bedrock platforms
- **Strands**: Autonomous agent framework
- **React Flow**: Professional diagram library
- **FastAPI**: High-performance Python backend

---

## 📄 License

This project is licensed under the MIT License.

---

Built for the **NVIDIA-AWS Agentic AI Unleashed Hackathon** 🚀
