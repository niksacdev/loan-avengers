# Draw.io System Architecture Diagram Specification

This document provides detailed specifications for creating a professional Draw.io version of the Loan Avengers system architecture.

## Overall Layout
- **Canvas Size**: 1400px width × 1000px height
- **Grid**: Enable grid with 10px spacing
- **Margins**: 40px on all sides
- **Orientation**: Landscape

## Color Palette

### Layer Colors
- **User Layer**: Light Blue (#E3F2FD) with Blue borders (#1976D2)
- **UI Layer**: Light Green (#E8F5E8) with Green borders (#388E3C)
- **API Layer**: Light Orange (#FFF3E0) with Orange borders (#F57C00)
- **Agent Layer**: Light Purple (#F3E5F5) with Purple borders (#7B1FA2)
- **MCP Layer**: Light Red (#FFEBEE) with Red borders (#D32F2F)
- **Data Layer**: Light Teal (#E0F2F1) with Teal borders (#00796B)
- **External Layer**: Light Yellow (#FFF8E1) with Amber borders (#FFA000)

## Component Specifications

### 1. User Experience Layer (Top - Y: 50-150)

#### User Component (X: 100, Y: 75)
- **Shape**: Rounded rectangle (20px radius)
- **Size**: 120px × 50px
- **Text**: "👤 User\n\"I need a $250K loan\""
- **Fill**: #E3F2FD
- **Border**: 2px solid #1976D2
- **Font**: Arial, 12pt, bold

#### Browser Component (X: 300, Y: 75)
- **Shape**: Rounded rectangle
- **Size**: 140px × 50px
- **Text**: "🌐 Web Browser\nReact 19 + TypeScript"
- **Fill**: #E3F2FD
- **Border**: 2px solid #1976D2

### 2. Frontend Layer - Alisha UI Coordinator (Y: 200-320)

#### Container Group (X: 50, Y: 200, Width: 450px, Height: 120px)
- **Background**: Light green (#E8F5E8)
- **Border**: 2px dashed #388E3C
- **Title**: "🎨 Frontend Layer - Alisha (UI Coordinator)"

#### UI Component (X: 70, Y: 230)
- **Shape**: Rounded rectangle
- **Size**: 160px × 60px
- **Text**: "🌟 Alisha - UI Coordinator\nReact Components\nReal-time Updates"
- **Fill**: #E8F5E8
- **Border**: 2px solid #388E3C

#### Theme Toggle (X: 250, Y: 230)
- **Shape**: Rounded rectangle
- **Size**: 120px × 25px
- **Text**: "🌙 Dark Mode Toggle\nVite-inspired Design"
- **Fill**: #E8F5E8

#### Progress Tracker (X: 250, Y: 270)
- **Shape**: Rounded rectangle
- **Size**: 120px × 25px
- **Text**: "📊 Progress Tracker\nAgent Status Display"
- **Fill**: #E8F5E8

#### Confetti (X: 380, Y: 240)
- **Shape**: Circle
- **Size**: 40px diameter
- **Text**: "🎉"
- **Fill**: #E8F5E8

### 3. API Gateway Layer (Y: 370-490)

#### Container Group (X: 50, Y: 370, Width: 450px, Height: 120px)
- **Background**: Light orange (#FFF3E0)
- **Border**: 2px dashed #F57C00
- **Title**: "🚀 API Gateway Layer"

#### FastAPI Component (X: 70, Y: 400)
- **Shape**: Rounded rectangle
- **Size**: 140px × 60px
- **Text**: "⚡ FastAPI Backend\nAsync Request Handling\nEntra ID Auth"
- **Fill**: #FFF3E0
- **Border**: 2px solid #F57C00

#### Stream Component (X: 230, Y: 400)
- **Shape**: Rounded rectangle
- **Size**: 140px × 60px
- **Text**: "📡 Server-Sent Events\nReal-time Streaming\nMCP Streamable HTTP"
- **Fill**: #FFF3E0

#### Thread Manager (X: 390, Y: 400)
- **Shape**: Rounded rectangle
- **Size**: 100px × 60px
- **Text**: "🧵 AgentThread Manager\nConversation State\nContext Persistence"
- **Fill**: #FFF3E0

### 4. Microsoft Agent Framework - Sequential Workflow (Y: 540-720)

#### Container Group (X: 50, Y: 540, Width: 1300px, Height: 180px)
- **Background**: Light purple (#F3E5F5)
- **Border**: 2px dashed #7B1FA2
- **Title**: "🦸‍♂️ Microsoft Agent Framework - Sequential Workflow"

#### John Agent (X: 80, Y: 580)
- **Shape**: Rounded rectangle with persona box below
- **Size**: 140px × 100px
- **Text**: "🦅 John \"Eagle Eye\"\nLightning Validation\n<5 seconds"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2
- **Persona Box**: "📋 Persona: intake-agent-persona.md\n🎯 Mission: Validate & Route\n⚡ Tools: None (Speed optimized)"

#### Sarah Agent (X: 340, Y: 580)
- **Shape**: Rounded rectangle with persona box below
- **Size**: 140px × 100px
- **Text**: "💼 Sarah - Income Specialist\nEmployment Verification\n<30 seconds"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2
- **Persona Box**: "📋 Persona: income-agent-persona.md\n🎯 Mission: Income Analysis\n🔧 Tools: Document + Financial"

#### Marcus Agent (X: 600, Y: 580)
- **Shape**: Rounded rectangle with persona box below
- **Size**: 140px × 100px
- **Text**: "📊 Marcus - Credit Analyst\nCredit Assessment\n<60 seconds"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2
- **Persona Box**: "📋 Persona: credit-agent-persona.md\n🎯 Mission: Credit Evaluation\n🔧 Tools: Application + Financial"

#### Alex Agent (X: 860, Y: 580)
- **Shape**: Rounded rectangle with persona box below
- **Size**: 140px × 100px
- **Text**: "🛡️ Alex - Risk Assessor\nFinal Decision\n<90 seconds"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2
- **Persona Box**: "📋 Persona: risk-agent-persona.md\n🎯 Mission: Risk Analysis\n🔧 Tools: All MCP Servers"

#### Workflow Arrows
- **John → Sarah**: Thick arrow (#7B1FA2, 4px width)
- **Sarah → Marcus**: Thick arrow (#7B1FA2, 4px width)
- **Marcus → Alex**: Thick arrow (#7B1FA2, 4px width)

### 5. MCP Server Tool Integration (Y: 770-890)

#### Container Group (X: 600, Y: 770, Width: 750px, Height: 120px)
- **Background**: Light red (#FFEBEE)
- **Border**: 2px dashed #D32F2F
- **Title**: "🔧 MCP Server Tool Integration"

#### MCP1 - Application Verification (X: 620, Y: 800)
- **Shape**: Rounded rectangle
- **Size**: 160px × 80px
- **Text**: "🔍 Application Verification\nPort 8010\nSSE Protocol\n\n🛠️ Tools:\n• verify_identity\n• get_credit_report\n• validate_documents"
- **Fill**: #FFEBEE
- **Border**: 2px solid #D32F2F

#### MCP2 - Document Processing (X: 800, Y: 800)
- **Shape**: Rounded rectangle
- **Size**: 160px × 80px
- **Text**: "📄 Document Processing\nPort 8011\nSSE Protocol\n\n🛠️ Tools:\n• extract_income_data\n• process_pay_stubs\n• validate_employment"
- **Fill**: #FFEBEE
- **Border**: 2px solid #D32F2F

#### MCP3 - Financial Calculations (X: 980, Y: 800)
- **Shape**: Rounded rectangle
- **Size**: 160px × 80px
- **Text**: "💰 Financial Calculations\nPort 8012\nSSE Protocol\n\n🛠️ Tools:\n• calculate_dti_ratio\n• assess_affordability\n• compute_risk_score"
- **Fill**: #FFEBEE
- **Border**: 2px solid #D32F2F

### 6. Data Models & State Management (Y: 770-890, Left Side)

#### Container Group (X: 50, Y: 770, Width: 500px, Height: 120px)
- **Background**: Light teal (#E0F2F1)
- **Border**: 2px dashed #00796B
- **Title**: "📊 Data Models & State Management"

#### Core Data Models (X: 70, Y: 800)
- **Shape**: Rounded rectangle
- **Size**: 140px × 80px
- **Text**: "💾 Core Data Models\n(Pydantic v2)\n\n📋 LoanApplication\n📈 AgentAssessment\n✅ LoanDecision"
- **Fill**: #E0F2F1
- **Border**: 2px solid #00796B

#### Conversation State (X: 230, Y: 800)
- **Shape**: Rounded rectangle
- **Size**: 140px × 80px
- **Text**: "🧵 Conversation State\n\n🧵 AgentThread\n⚡ Redis Cache\n30-min TTL"
- **Fill**: #E0F2F1
- **Border**: 2px solid #00796B

### 7. External Service Integration (Y: 940-1060, Right Side)

#### Container Group (X: 800, Y: 940, Width: 550px, Height: 120px)
- **Background**: Light yellow (#FFF8E1)
- **Border**: 2px dashed #FFA000
- **Title**: "🌍 External Service Integration"

#### Azure OpenAI (X: 820, Y: 970)
- **Shape**: Cloud shape or rounded rectangle
- **Size**: 120px × 80px
- **Text**: "🧠 Azure OpenAI\nGPT-4 Models\nAgent reasoning"
- **Fill**: #FFF8E1
- **Border**: 2px solid #FFA000

#### Credit API (X: 960, Y: 970)
- **Shape**: Rounded rectangle
- **Size**: 120px × 80px
- **Text**: "📊 Credit Bureau APIs\nCredit reports\nIdentity verification"
- **Fill**: #FFF8E1
- **Border**: 2px solid #FFA000

#### Banking API (X: 1100, Y: 970)
- **Shape**: Rounded rectangle
- **Size**: 120px × 80px
- **Text**: "🏦 Banking APIs\nIncome verification\nEmployment data"
- **Fill**: #FFF8E1
- **Border**: 2px solid #FFA000

#### Document Storage (X: 1240, Y: 970)
- **Shape**: Cylinder or rounded rectangle
- **Size**: 100px × 80px
- **Text**: "📦 Azure Blob Storage\nDocument uploads\nSecure storage"
- **Fill**: #FFF8E1
- **Border**: 2px solid #FFA000

## Connection Specifications

### User Flow Connections
- **User → Browser**: Simple arrow (2px, #1976D2)
- **Browser → UI**: Simple arrow (2px, #1976D2)
- **UI → FastAPI**: Simple arrow (2px, #388E3C → #F57C00)

### Agent Workflow Connections
- **FastAPI → ThreadMgr**: Simple arrow (2px, #F57C00)
- **ThreadMgr → John**: Thick arrow (4px, #F57C00 → #7B1FA2)
- **Agent sequence**: John → Sarah → Marcus → Alex (4px, #7B1FA2)

### Tool Integration Connections
- **Sarah → MCP2, MCP3**: Dotted lines (2px, #7B1FA2 → #D32F2F)
- **Marcus → MCP1, MCP3**: Dotted lines (2px, #7B1FA2 → #D32F2F)
- **Alex → All MCP servers**: Dotted lines (2px, #7B1FA2 → #D32F2F)

### External Service Connections
- **MCP1 → Credit API, Azure OpenAI**: Simple arrows (2px, #D32F2F → #FFA000)
- **MCP2 → Banking API, Document Storage**: Simple arrows (2px, #D32F2F → #FFA000)
- **MCP3 → Azure OpenAI**: Simple arrow (2px, #D32F2F → #FFA000)

### State Management Connections
- **ThreadMgr → AgentThread**: Simple arrow (2px, #F57C00 → #00796B)
- **AgentThread → Redis Cache**: Simple arrow (2px, #00796B)
- **All agents → Assessment models**: Dotted lines (1px, respective colors → #00796B)

### Real-time Update Connections
- **Alex → Stream**: Curved arrow (3px, #7B1FA2 → #F57C00)
- **Stream → Progress**: Curved arrow (3px, #F57C00 → #388E3C)
- **Decision → Confetti**: Curved arrow (3px, #00796B → #388E3C)

## Legend Box (Bottom Right)
- **Position**: X: 1150, Y: 950
- **Size**: 200px × 100px
- **Background**: White with black border
- **Content**:
  - Color coding explanation
  - Arrow type meanings
  - Performance timing indicators

## Typography Guidelines
- **Headers**: Arial, 14pt, Bold, respective layer colors
- **Component Names**: Arial, 12pt, Bold, Black
- **Descriptions**: Arial, 10pt, Regular, Dark Gray
- **Technical Details**: Arial, 9pt, Regular, Medium Gray
- **Emojis**: 14pt for headers, 12pt for components

## Export Settings
- **Format**: .drawio (native), .png (1400×1000, 300 DPI), .svg (vector)
- **Background**: White
- **Quality**: High resolution for presentations
- **Compression**: Optimize for file size while maintaining quality