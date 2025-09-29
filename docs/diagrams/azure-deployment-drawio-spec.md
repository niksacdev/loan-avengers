# Draw.io Azure Deployment Architecture Specification

This document provides detailed specifications for creating a professional Draw.io version of the Loan Avengers Azure deployment architecture.

## Overall Layout
- **Canvas Size**: 1600px width × 1200px height
- **Grid**: Enable grid with 20px spacing
- **Margins**: 50px on all sides
- **Orientation**: Landscape
- **Background**: Light Azure blue (#F0F8FF)

## Azure Color Palette

### Service Categories
- **User Layer**: Light Blue (#E1F5FE) with Blue borders (#0277BD)
- **Azure Global Services**: Azure Orange (#FF8F00) with Orange borders (#EF6C00)
- **Container Apps**: Green (#2E7D32) with Dark Green borders (#1B5E20)
- **Data Services**: Purple (#7B1FA2) with Dark Purple borders (#4A148C)
- **External Services**: Red (#C62828) with Dark Red borders (#B71C1C)
- **Security Services**: Dark Blue (#1565C0) with Navy borders (#0D47A1)

## Azure Icons
Use official Azure icons from Draw.io's Azure shape library:
- Azure Front Door, Container Apps, Key Vault, etc.
- If unavailable, use blue rounded rectangles with appropriate text

## Component Specifications

### 1. User Experience Layer (Top - Y: 60-160)

#### User Component (X: 100, Y: 80)
- **Shape**: Rounded rectangle with user icon
- **Size**: 100px × 60px
- **Text**: "👤 User"
- **Fill**: #E1F5FE
- **Border**: 2px solid #0277BD
- **Font**: Arial, 12pt, bold

#### Mobile App (X: 250, Y: 80)
- **Shape**: Mobile phone shape or rounded rectangle
- **Size**: 80px × 60px
- **Text**: "📱 Mobile App"
- **Fill**: #E1F5FE
- **Border**: 2px solid #0277BD

#### Web App (X: 370, Y: 80)
- **Shape**: Browser shape or rounded rectangle
- **Size**: 100px × 60px
- **Text**: "🌐 Web App"
- **Fill**: #E1F5FE
- **Border**: 2px solid #0277BD

### 2. Azure Front Door & CDN Layer (Y: 200-280)

#### Container Group (X: 50, Y: 200, Width: 500px, Height: 80px)
- **Background**: Light orange (#FFF3E0)
- **Border**: 2px dashed #FF8F00
- **Title**: "Azure Front Door & CDN"

#### Azure Front Door (X: 80, Y: 220)
- **Shape**: Azure Front Door icon or hexagon
- **Size**: 120px × 50px
- **Text**: "🌍 Azure Front Door\nGlobal Load Balancer"
- **Fill**: #FFF3E0
- **Border**: 2px solid #FF8F00

#### Azure CDN (X: 220, Y: 220)
- **Shape**: Azure CDN icon or cloud shape
- **Size**: 120px × 50px
- **Text**: "🚀 Azure CDN\nStatic Assets"
- **Fill**: #FFF3E0
- **Border**: 2px solid #FF8F00

### 3. Identity & Security Layer (Y: 320-400)

#### Container Group (X: 600, Y: 200, Width: 400px, Height: 200px)
- **Background**: Light blue (#E3F2FD)
- **Border**: 2px dashed #1565C0
- **Title**: "Identity & Security"

#### Entra ID (X: 620, Y: 230)
- **Shape**: Azure AD icon or shield shape
- **Size**: 120px × 60px
- **Text**: "🔐 Entra ID\nAuthentication"
- **Fill**: #E3F2FD
- **Border**: 2px solid #1565C0

#### Key Vault (X: 620, Y: 320)
- **Shape**: Azure Key Vault icon or key shape
- **Size**: 120px × 60px
- **Text**: "🔑 Azure Key Vault\nSecrets Management"
- **Fill**: #E3F2FD
- **Border**: 2px solid #1565C0

### 4. Azure Container Apps Environment (Y: 450-650)

#### Container Group (X: 50, Y: 450, Width: 900px, Height: 200px)
- **Background**: Light green (#E8F5E8)
- **Border**: 2px dashed #2E7D32
- **Title**: "Azure Container Apps Environment"

#### Container Apps Subgroup (X: 80, Y: 480)
- **Background**: Lighter green (#F1F8E9)
- **Border**: 1px solid #2E7D32
- **Size**: 400px × 80px
- **Title**: "Container Apps"

#### UI Container App (X: 100, Y: 500)
- **Shape**: Container icon or rounded rectangle
- **Size**: 120px × 50px
- **Text**: "🎨 Loan Avengers UI\nReact + Vite\nContainer App"
- **Fill**: #E8F5E8
- **Border**: 2px solid #2E7D32

#### API Container App (X: 240, Y: 500)
- **Shape**: Container icon or rounded rectangle
- **Size**: 140px × 50px
- **Text**: "🚀 FastAPI Backend\nMicrosoft Agent Framework\nContainer App"
- **Fill**: #E8F5E8
- **Border**: 2px solid #2E7D32

#### MCP Servers Subgroup (X: 500, Y: 480)
- **Background**: Lighter green (#F1F8E9)
- **Border**: 1px solid #2E7D32
- **Size**: 420px × 140px
- **Title**: "MCP Servers"

#### MCP1 Server (X: 520, Y: 500)
- **Shape**: Rounded rectangle
- **Size**: 110px × 40px
- **Text**: "🔍 Application Verification\nMCP Server\nPort 8010"
- **Fill**: #E8F5E8
- **Border**: 1px solid #2E7D32

#### MCP2 Server (X: 650, Y: 500)
- **Shape**: Rounded rectangle
- **Size**: 110px × 40px
- **Text**: "📄 Document Processing\nMCP Server\nPort 8011"
- **Fill**: #E8F5E8
- **Border**: 1px solid #2E7D32

#### MCP3 Server (X: 780, Y: 500)
- **Shape**: Rounded rectangle
- **Size**: 110px × 40px
- **Text**: "💰 Financial Calculations\nMCP Server\nPort 8012"
- **Fill**: #E8F5E8
- **Border**: 1px solid #2E7D32

### 5. Data & Storage Layer (Y: 700-820)

#### Container Group (X: 50, Y: 700, Width: 800px, Height: 120px)
- **Background**: Light purple (#F3E5F5)
- **Border**: 2px dashed #7B1FA2
- **Title**: "Data & Storage Layer"

#### Redis Cache (X: 80, Y: 730)
- **Shape**: Azure Cache icon or cylinder
- **Size**: 140px × 70px
- **Text**: "⚡ Azure Cache for Redis\nAgentThread State\n30-min TTL"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2

#### Blob Storage (X: 250, Y: 730)
- **Shape**: Azure Blob Storage icon or box
- **Size**: 140px × 70px
- **Text**: "📦 Azure Blob Storage\nDocument Uploads\nSecure Container"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2

#### Cosmos DB (X: 420, Y: 730)
- **Shape**: Azure Cosmos DB icon or globe
- **Size**: 140px × 70px
- **Text**: "🌍 Azure Cosmos DB\nCompleted Applications\nGlobal Distribution"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2

### 6. DevOps & Registry Layer (Y: 860-940)

#### Container Group (X: 600, Y: 700, Width: 350px, Height: 240px)
- **Background**: Light gray (#F5F5F5)
- **Border**: 2px dashed #757575
- **Title**: "DevOps & Registry"

#### Container Registry (X: 620, Y: 730)
- **Shape**: Azure Container Registry icon or box
- **Size**: 140px × 70px
- **Text**: "🐳 Azure Container Registry\nPrivate Images\nVulnerability Scanning"
- **Fill**: #F5F5F5
- **Border**: 2px solid #757575

#### GitHub Actions (X: 620, Y: 820)
- **Shape**: GitHub icon or circular arrow
- **Size**: 140px × 70px
- **Text**: "🔄 GitHub Actions\nCI/CD Pipeline"
- **Fill**: #F5F5F5
- **Border**: 2px solid #757575

### 7. External Integrations (Y: 980-1100)

#### Container Group (X: 400, Y: 980, Width: 800px, Height: 120px)
- **Background**: Light red (#FFEBEE)
- **Border**: 2px dashed #C62828
- **Title**: "External Integrations"

#### Azure OpenAI (X: 430, Y: 1010)
- **Shape**: Brain or cloud icon
- **Size**: 140px × 70px
- **Text**: "🧠 Azure OpenAI\nGPT-4 Models\nAgent Framework"
- **Fill**: #FFEBEE
- **Border**: 2px solid #C62828

#### Credit Bureau APIs (X: 590, Y: 1010)
- **Shape**: Rounded rectangle with API symbol
- **Size**: 140px × 70px
- **Text**: "📊 Credit Bureau APIs\nExternal Verification"
- **Fill**: #FFEBEE
- **Border**: 2px solid #C62828

#### Banking APIs (X: 750, Y: 1010)
- **Shape**: Bank building icon or rounded rectangle
- **Size**: 140px × 70px
- **Text**: "🏦 Banking APIs\nIncome Verification"
- **Fill**: #FFEBEE
- **Border**: 2px solid #C62828

## Connection Specifications

### User Traffic Flow
- **User → Mobile/Web**: Simple arrows (2px, #0277BD)
- **Mobile/Web → Azure Front Door**: Thick arrows (4px, #0277BD → #FF8F00)
- **Azure Front Door → CDN**: Simple arrow (2px, #FF8F00)
- **Azure Front Door → UI Container**: Thick arrow (4px, #FF8F00 → #2E7D32)

### Authentication Flow
- **UI → Entra ID**: Dashed arrow (2px, #2E7D32 → #1565C0)
- **API → Entra ID**: Dashed arrow (2px, #2E7D32 → #1565C0)

### Container Communication
- **UI → API**: Thick arrow (4px, #2E7D32)
- **API → MCP Servers**: Multiple arrows (3px, #2E7D32 to each MCP server)

### Data Access
- **API → Redis**: Simple arrow (2px, #2E7D32 → #7B1FA2)
- **API → Blob Storage**: Simple arrow (2px, #2E7D32 → #7B1FA2)
- **API → Cosmos DB**: Simple arrow (2px, #2E7D32 → #7B1FA2)

### Security Access
- **API → Key Vault**: Dashed arrow (2px, #2E7D32 → #1565C0)
- **All MCP Servers → Key Vault**: Multiple dashed arrows (1px, #2E7D32 → #1565C0)

### External Service Connections
- **API → Azure OpenAI**: Simple arrow (2px, #2E7D32 → #C62828)
- **MCP1 → Credit Bureau**: Simple arrow (2px, #2E7D32 → #C62828)
- **MCP2 → Banking APIs**: Simple arrow (2px, #2E7D32 → #C62828)

### DevOps Flow
- **GitHub Actions → Container Registry**: Simple arrow (2px, #757575)
- **Container Registry → All Container Apps**: Multiple arrows (2px, #757575 → #2E7D32)

## Performance & Cost Information Boxes

### Performance Targets Box (X: 1050, Y: 450)
- **Shape**: Rounded rectangle with light yellow background
- **Size**: 200px × 150px
- **Border**: 2px solid #FFA000
- **Content**:
  ```
  📊 Performance Targets

  • UI Response: <200ms
  • API Latency: <500ms
  • Agent Processing: <3min
  • Auto-scaling: 0-100 instances
  ```

### Security Features Box (X: 1050, Y: 620)
- **Shape**: Rounded rectangle with light blue background
- **Size**: 200px × 150px
- **Border**: 2px solid #1565C0
- **Content**:
  ```
  🛡️ Security Features

  • Zero Trust Architecture
  • Managed Identity
  • Network Isolation
  • SOC 2, GDPR, CCPA Ready
  ```

### Cost Optimization Box (X: 1050, Y: 790)
- **Shape**: Rounded rectangle with light green background
- **Size**: 200px × 150px
- **Border**: 2px solid #2E7D32
- **Content**:
  ```
  💰 Cost Optimization

  • Serverless Compute
  • Auto-scaling to Zero
  • Reserved Capacity
  • Application Insights
  ```

## Azure Regions & Availability

### Primary Region Indicator (X: 1300, Y: 300)
- **Shape**: Globe or Azure region icon
- **Size**: 80px × 80px
- **Text**: "🌍 Primary Region\nEast US 2"
- **Fill**: #E3F2FD
- **Border**: 2px solid #1565C0

### Backup Region Indicator (X: 1300, Y: 400)
- **Shape**: Globe or Azure region icon
- **Size**: 80px × 80px
- **Text**: "🌍 Backup Region\nWest US 2"
- **Fill**: #F3E5F5
- **Border**: 2px solid #7B1FA2

## Network Flow Indicators

### High Traffic Paths
- Use thicker arrows (4-6px) for:
  - User to Front Door
  - Front Door to Container Apps
  - API to MCP Servers

### Secure Connections
- Use dashed lines for:
  - Authentication flows
  - Key Vault access
  - Cross-region replication

### API Calls
- Use dotted lines for:
  - External service integrations
  - Third-party API calls

## Typography Guidelines
- **Title**: Arial, 16pt, Bold, Azure Blue (#0078D4)
- **Service Names**: Arial, 12pt, Bold, Black
- **Descriptions**: Arial, 10pt, Regular, Dark Gray (#333333)
- **Technical Details**: Arial, 9pt, Regular, Medium Gray (#666666)
- **Performance Metrics**: Arial, 10pt, Bold, respective category colors

## Legend Box (Bottom Right)
- **Position**: X: 1300, Y: 1000
- **Size**: 250px × 150px
- **Background**: White with Azure blue border
- **Content**:
  - Service category color coding
  - Arrow type meanings (solid, dashed, dotted)
  - Performance and security indicators
  - Azure service icons explanation

## Export Settings
- **Format**: .drawio (native), .png (1600×1200, 300 DPI), .svg (vector)
- **Background**: Light Azure blue (#F0F8FF)
- **Quality**: High resolution for executive presentations
- **Compression**: Optimize for file size while maintaining Azure brand quality
- **Print**: A3 landscape orientation for poster printing

## Accessibility
- **Color Contrast**: Ensure WCAG 2.1 AA compliance
- **Text Size**: Minimum 9pt for all text
- **Alternative Text**: Include descriptions for screen readers
- **High Contrast**: Provide alternative version for accessibility needs