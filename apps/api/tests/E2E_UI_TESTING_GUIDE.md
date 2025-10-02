# End-to-End UI Testing Guide

## Overview

This guide explains how to perform end-to-end testing of the Loan Avengers UI application, including manual testing procedures and automated testing strategies.

## Architecture

```
┌─────────────────┐
│   React UI      │  (Port 5173)
│  CoordinatorChat│
└────────┬────────┘
         │ HTTP POST /api/chat
         ▼
┌─────────────────┐
│   FastAPI       │  (Port 8000)
│   /api/chat     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Conversation     │
│Orchestrator     │
└────────┬────────┘
         │ When complete
         ▼
┌─────────────────┐
│Sequential       │
│Pipeline         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4 Agents        │
│ (Sequential)    │
└─────────────────┘
```

## Test Scenarios

### 1. Happy Path: Loan Approval

**Goal**: Test complete conversation flow from start to approved loan application.

**Steps**:
1. Open UI at `http://localhost:5173`
2. Verify initial greeting from Cap-ital America appears
3. **Step 1**: Select home price (e.g., "$200K - $400K")
   - Verify progress bar shows 25%
   - Verify down payment options appear
4. **Step 2**: Select down payment percentage (e.g., "20%")
   - Verify progress bar shows 50%
   - Verify income range options appear
5. **Step 3**: Select income range (e.g., "$100K - $250K")
   - Verify progress bar shows 75%
   - Verify personal info form appears
6. **Step 4**: Fill out personal info form
   - Name: "Tony Stark"
   - Email: "tony@starkindustries.com"
   - Last 4 digits: "1234"
   - Click "Submit Application"
   - Verify progress bar shows 100%
   - Verify "AVENGERS ASSEMBLE" message appears
7. **Processing Phase**: Watch agent updates stream in
   - Intake Agent validates (25%)
   - Credit Agent assesses (50%)
   - Income Agent verifies (75%)
   - Risk Agent decides (100%)
8. **Final Result**: Verify loan decision appears

**Expected Result**:
- All steps complete without errors
- Progress updates appear in real-time
- Final decision is rendered

### 2. Session Continuity

**Goal**: Verify session persistence across page refreshes.

**Steps**:
1. Complete Steps 1-2 from Happy Path
2. Note the session ID (check browser dev tools → Network → Response)
3. Refresh the page (F5)
4. Verify conversation state is lost (starts over)
5. **Future Enhancement**: Implement session restoration

**Current Behavior**:
- Sessions are stored server-side
- UI doesn't restore session on refresh (enhancement needed)

**Enhancement Needed**:
- Store session_id in localStorage
- On mount, check for session_id and call `GET /api/sessions/{session_id}`
- Restore conversation state from server

### 3. Error Handling

**Goal**: Test error scenarios and user recovery.

**Test Cases**:

#### A. Network Failure
1. Open browser dev tools → Network tab
2. Set throttling to "Offline"
3. Try to submit a message
4. Verify error message appears
5. Set throttling back to "Online"
6. Verify user can retry

#### B. Invalid Input
1. On personal info form, enter invalid email
2. Try to submit
3. Verify validation message appears
4. Correct email and resubmit
5. Verify processing continues

#### C. Backend Service Down
1. Stop API server (`Ctrl+C`)
2. Try to send message in UI
3. Verify clear error message appears
4. Restart API server
5. Verify user can continue

### 4. Mobile Responsiveness

**Goal**: Verify UI works on mobile devices.

**Steps**:
1. Open browser dev tools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select device (e.g., "iPhone 12 Pro")
4. Run Happy Path test
5. Verify:
   - Chat bubbles are readable
   - Quick reply buttons are tappable
   - Form inputs are usable
   - Progress bar is visible

### 5. Quick Reply vs. Text Input

**Goal**: Test both interaction modes.

**Steps**:
1. **Quick Reply Mode**: Use quick reply buttons for all steps
2. **Text Input Mode**: Type custom values:
   - Home price: "325000"
   - Down payment: "18"
   - Income: "145000"
3. Verify both modes work correctly

### 6. Dummy Data Generation

**Goal**: Test the "Generate Dummy Data" button.

**Steps**:
1. Complete conversation to personal info form
2. Click "Generate Dummy Data" button
3. Verify form fields are populated with Avengers-themed data
4. Submit form
5. Verify processing works with generated data

## Automated UI Testing

### Playwright Setup

```bash
# Install Playwright
cd apps/ui
npm install -D @playwright/test
npx playwright install

# Run tests
npx playwright test
```

### Sample Playwright Test

```typescript
// apps/ui/e2e/loan-application.spec.ts
import { test, expect } from '@playwright/test';

test('complete loan application flow', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:5173');

  // Wait for initial message
  await expect(page.getByText(/Hi there! I'm Cap-ital America/)).toBeVisible();

  // Step 1: Select home price
  await page.getByRole('button', { name: '$200K - $400K' }).click();
  await expect(page.getByText(/down payment/i)).toBeVisible();

  // Step 2: Select down payment
  await page.getByRole('button', { name: '20%' }).click();
  await expect(page.getByText(/income/i)).toBeVisible();

  // Step 3: Select income
  await page.getByRole('button', { name: '$100K - $250K' }).click();
  await expect(page.getByText(/personal/i)).toBeVisible();

  // Step 4: Fill personal info
  await page.getByLabel('Full Name').fill('Tony Stark');
  await page.getByLabel('Email').fill('tony@starkindustries.com');
  await page.getByLabel('Last 4 Digits').fill('1234');
  await page.getByRole('button', { name: 'Submit Application' }).click();

  // Wait for processing
  await expect(page.getByText(/AVENGERS.*ASSEMBLE/)).toBeVisible();

  // Verify agent updates appear
  await expect(page.getByText(/Intake Agent/)).toBeVisible({ timeout: 30000 });
  await expect(page.getByText(/Credit Agent/)).toBeVisible({ timeout: 30000 });
});

test('session persistence', async ({ page }) => {
  // Start application
  await page.goto('http://localhost:5173');
  await page.getByRole('button', { name: '$200K - $400K' }).click();

  // Get session ID from network
  const sessionId = await page.evaluate(() => {
    return sessionStorage.getItem('session_id');
  });

  // Refresh page
  await page.reload();

  // TODO: Verify session restored (needs implementation)
});
```

## Performance Testing

### Load Testing with k6

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 }, // Ramp up
    { duration: '1m', target: 20 },  // Stay at 20 users
    { duration: '30s', target: 0 },  // Ramp down
  ],
};

export default function () {
  // Start conversation
  let res1 = http.post('http://localhost:8000/api/chat', JSON.stringify({
    user_message: '300000',
    session_id: null,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(res1, {
    'status is 200': (r) => r.status === 200,
    'has session_id': (r) => JSON.parse(r.body).session_id !== null,
  });

  const sessionId = JSON.parse(res1.body).session_id;

  // Continue conversation
  http.post('http://localhost:8000/api/chat', JSON.stringify({
    user_message: '20',
    session_id: sessionId,
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  sleep(1);
}
```

Run: `k6 run load-test.js`

## Monitoring During E2E Tests

### Things to Watch

1. **Browser Console**: Check for JavaScript errors
2. **Network Tab**: Verify API calls succeed
3. **API Logs**: Watch agent processing logs
4. **Performance**:
   - Time to first message: < 500ms
   - Time per agent update: < 2s
   - Total processing time: < 30s

### Debug Mode

Enable debug logging:
```bash
# API
export LOG_LEVEL=DEBUG

# UI
localStorage.setItem('debug', 'loan-avengers:*')
```

## Common Issues

### Issue: "Connection refused" errors

**Cause**: API server not running

**Fix**:
```bash
cd apps/api
uv run python -m loan_avengers.api.app
```

### Issue: Agents not processing

**Cause**: Missing Azure AI configuration

**Fix**:
```bash
export AZURE_AI_PROJECT_ENDPOINT="your-endpoint"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model"
```

### Issue: CORS errors

**Cause**: API not configured for UI origin

**Fix**: Check `APP_CORS_ORIGINS` in `.env`

## Next Steps

1. **Implement Playwright tests** for automated UI testing
2. **Add session restoration** in UI for better UX
3. **Implement WebSocket** for real-time agent updates (current: polling)
4. **Add visual regression testing** with Percy or similar
5. **Set up CI/CD pipeline** to run E2E tests on PRs

## Resources

- [Playwright Documentation](https://playwright.dev)
- [React Testing Library](https://testing-library.com/react)
- [k6 Load Testing](https://k6.io/docs)
