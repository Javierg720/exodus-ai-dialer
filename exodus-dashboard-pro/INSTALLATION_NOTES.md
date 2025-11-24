# Toast Notification System - Installation Notes

## Required Package Installation

The toast notification system requires `react-hot-toast` to be installed.

Run the following command in the `exodus-dashboard-pro` directory:

```bash
cd exodus-dashboard-pro
npm install react-hot-toast
```

## What Was Updated

1. **main.tsx** - Added Toaster component for displaying toast notifications
2. **src/lib/api.ts** - Added toast notifications for API errors

## Usage

After installation, the dashboard will automatically show toast notifications for:
- API errors (network failures, server errors, etc.)
- Failed requests with user-friendly error messages

Toast notifications will appear in the top-right corner of the screen.
