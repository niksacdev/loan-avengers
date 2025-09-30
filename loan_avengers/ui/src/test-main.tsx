import { createRoot } from 'react-dom/client'

// Absolute minimal React test
const root = createRoot(document.getElementById('root')!)
root.render(<div style={{padding: '20px', background: 'lightblue'}}>✅ React is working! This is a minimal test component.</div>)