# Draw.io Diagrams - Quick Start Guide

This guide provides step-by-step instructions for creating professional Draw.io versions of the Loan Avengers architecture diagrams using the detailed specifications.

## Prerequisites

1. **Draw.io Access**
   - Open [Draw.io (app.diagrams.net)](https://app.diagrams.net/) in your browser
   - OR install Draw.io desktop application
   - OR use VS Code with Draw.io Integration extension

2. **Specifications Available**
   - [System Architecture Specification](./system-architecture-drawio-spec.md)
   - [Azure Deployment Specification](./azure-deployment-drawio-spec.md)

## Method 1: Manual Creation (Recommended)

### Step 1: Setup Canvas
1. Create new diagram in Draw.io
2. Set canvas size (1400×1000 for System, 1600×1200 for Azure)
3. Enable grid (10px for System, 20px for Azure)
4. Set background color if specified

### Step 2: Import Azure Icons (for Azure diagram)
1. Go to File → Libraries → Search → "Azure"
2. Enable "Azure" library for official Microsoft icons
3. OR use More Shapes → search for "Azure 2019"

### Step 3: Create Layer Structure
1. Use View → Layers to create organized layers:
   - Background layer
   - User layer
   - Application layers
   - Data layers
   - External services

### Step 4: Build Components
1. Follow the specifications for exact positioning (X, Y coordinates)
2. Use specified colors and sizes
3. Add text with proper fonts and sizes
4. Group related components

### Step 5: Add Connections
1. Use specified arrow types and colors
2. Add connection labels where indicated
3. Ensure proper layering (connections behind components)

### Step 6: Final Touches
1. Add legend box as specified
2. Include performance/security information boxes
3. Verify all text is readable
4. Test at different zoom levels

## Method 2: Using Draw.io MCP Server (Advanced)

### Prerequisites for MCP Method
1. **Browser Extension**: Install Draw.io MCP Browser Extension
   - [Chrome Web Store](https://chrome.google.com/webstore/detail/drawio-mcp-extension/okdbbjbbccdhhfaefmcmekalmmdjjide)
   - [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/drawio-mcp-extension/)

2. **MCP Server Running**: The drawio-mcp-server is already configured and running in this environment

3. **Active Draw.io Session**: Have Draw.io open in browser with extension connected (green indicator)

### MCP Server Commands Available
- `add-rectangle` - Create boxes and containers
- `add-edge` - Create connections between components
- `add-cell-of-shape` - Add specific shapes from library
- `get-shape-categories` - Browse available shapes
- `list-paged-model` - Inspect current diagram structure

### Using MCP Commands

#### Create System Architecture Container Groups
```
Use add-rectangle to create the main container groups:

1. User Experience Layer (50, 50, 450, 100) - Light blue background
2. Frontend Layer (50, 200, 450, 120) - Light green background
3. API Gateway Layer (50, 370, 450, 120) - Light orange background
4. Agent Framework Layer (50, 540, 1300, 180) - Light purple background
5. MCP Tools Layer (600, 770, 750, 120) - Light red background
6. Data Layer (50, 770, 500, 120) - Light teal background
7. External Services (800, 940, 550, 120) - Light yellow background
```

#### Create Agent Components
```
Add the four main agents with persona information:

1. John (Eagle Eye) - Validator agent with <5 second target
2. Sarah - Income specialist with <30 second target
3. Marcus - Credit analyst with <60 second target
4. Alex - Risk assessor with <90 second target

Each with their persona file references and tool configurations.
```

#### Create Azure Infrastructure Components
```
Use add-cell-of-shape with Azure icons:

1. Azure Front Door for global load balancing
2. Container Apps Environment with all microservices
3. Redis Cache, Blob Storage, Cosmos DB for data layer
4. Key Vault and Entra ID for security
5. External service integrations
```

## Quick Creation Checklist

### System Architecture Diagram
- [ ] User experience layer with browser and user components
- [ ] Alisha UI coordinator with React components
- [ ] FastAPI backend with streaming capabilities
- [ ] All 4 agents (John, Sarah, Marcus, Alex) with personas
- [ ] 3 MCP servers (ports 8010, 8011, 8012) with tool lists
- [ ] Data models and AgentThread state management
- [ ] External services (Azure OpenAI, Credit/Banking APIs)
- [ ] Proper arrows showing sequential workflow
- [ ] Performance timing annotations
- [ ] Color coding legend

### Azure Deployment Diagram
- [ ] User layer (mobile/web apps)
- [ ] Azure Front Door and CDN
- [ ] Container Apps Environment
- [ ] All Azure services with official icons
- [ ] Security layer (Entra ID, Key Vault)
- [ ] Data services (Redis, Blob, Cosmos)
- [ ] DevOps pipeline (GitHub Actions, Container Registry)
- [ ] External integrations
- [ ] Performance metrics boxes
- [ ] Security features callouts
- [ ] Cost optimization information
- [ ] Network flow indicators

## Quality Assurance

### Before Finalizing
1. **Readability**: All text readable at 100% zoom
2. **Consistency**: Colors match specifications exactly
3. **Alignment**: Components properly aligned to grid
4. **Connections**: All arrows point correctly and are labeled
5. **Completeness**: All components from specifications included
6. **Professional**: Suitable for stakeholder presentations

### Export Settings
1. **Formats**:
   - `.drawio` - Native format for editing
   - `.png` - High resolution (300 DPI) for documents
   - `.svg` - Vector format for scalability
   - `.pdf` - Print-ready format

2. **Quality Settings**:
   - Background: White or specified color
   - Border: 40-50px margins
   - Resolution: 300 DPI minimum for print

## Common Issues & Solutions

### Layout Problems
- **Components overlap**: Use layer management
- **Text too small**: Increase font size, reduce component density
- **Poor alignment**: Enable grid snap, use alignment tools

### Connection Issues
- **Arrows not connecting**: Use connection points on shapes
- **Cluttered lines**: Route through open spaces, use different line styles
- **Missing labels**: Add text boxes on connection lines

### Performance
- **Large file size**: Optimize images, reduce unnecessary details
- **Slow rendering**: Split into multiple diagrams if too complex
- **Memory issues**: Close unused browsers tabs, reduce component count

## Tips for Professional Results

1. **Consistent Spacing**: Use grid to maintain uniform spacing
2. **Visual Hierarchy**: Size components by importance
3. **Color Psychology**: Use Azure blues for trust, greens for success
4. **White Space**: Don't overcrowd - leave breathing room
5. **Typography**: Stick to 2-3 font sizes maximum
6. **Testing**: View at different zoom levels and screen sizes

## Next Steps

Once diagrams are created:
1. **Review**: Have stakeholders review for accuracy
2. **Version Control**: Save versions with timestamps
3. **Documentation**: Update README with actual diagram links
4. **Presentations**: Create simplified versions for different audiences
5. **Maintenance**: Update when architecture changes

## Support Resources

- **Draw.io Documentation**: [app.diagrams.net/doc](https://app.diagrams.net/doc/)
- **Azure Icons Library**: [Azure Architecture Center](https://docs.microsoft.com/azure/architecture/)
- **MCP Server Troubleshooting**: [drawio-mcp-server/TROUBLESHOOTING.md](https://github.com/lgazo/drawio-mcp-server/blob/main/TROUBLESHOOTING.md)
- **Professional Design Guidelines**: [Microsoft Azure branding](https://azure.microsoft.com/mediahandler/files/resourcefiles/azure-brand-guidelines/Azure%20Brand%20Guidelines.pdf)