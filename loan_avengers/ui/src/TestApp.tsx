/**
 * Minimal test component to debug React rendering issues
 */
export function TestApp() {
  return (
    <div style={{ padding: '20px', background: '#f0f0f0', minHeight: '100vh' }}>
      <h1>🎯 React Test App</h1>
      <p>If you can see this, React is working!</p>
      <div style={{ background: 'white', padding: '20px', margin: '20px 0', border: '1px solid #ddd' }}>
        <h2>Component Test</h2>
        <p>This is a minimal React component with inline styles (no Tailwind dependencies).</p>
        <button
          onClick={() => alert('React event handling works!')}
          style={{ padding: '10px 20px', background: '#007bff', color: 'white', border: 'none', cursor: 'pointer' }}
        >
          Test Button
        </button>
      </div>
    </div>
  );
}