# Spot Edit Frontend

This is the frontend application for Spot Edit, built with React, TypeScript, and Vite.

## Path 5: Frontend Templates & Editing (COMPLETED)

This implementation covers all deliverables for **Path 5** from the parallel development paths:

### ✅ Implemented Components

#### 1. **TemplateLibrary Component** (`src/components/TemplateLibrary.tsx`)
- Lists all saved templates with metadata
- Template cards display name, creation date, field count, and last update
- Search/filter functionality
- Delete template action with confirmation
- Load template button to navigate to edit page
- Empty state when no templates exist
- Error handling and loading states

#### 2. **ChatInterface Component** (`src/components/ChatInterface.tsx`)
- Message input field with send button
- Conversation history display with scrolling
- User vs AI message styling (blue vs gray)
- Loading indicator while AI processes requests
- Display proposed changes in structured format
- Apply/reject buttons for proposed changes
- Error display for failed operations
- Empty state with example commands

#### 3. **DocumentPreview Component** (`src/components/DocumentPreview.tsx`)
- Displays document text with syntax highlighting
- Highlights detected fields with yellow background
- Hover tooltips showing field name and value
- Field legend at the bottom showing all fields
- Efficient rendering using position maps
- Toggle for field highlighting

#### 4. **Edit Page** (`src/pages/Edit.tsx`)
- Loads template from URL parameter
- Split view: Document preview + Chat interface
- Download updated document functionality
- Back to library navigation
- Shows current field values
- Handles update commands through chat
- Export functionality with proper file naming
- Loading and error states

### ✅ Infrastructure

#### 5. **API Client** (`src/api/client.ts`)
- `getTemplates()` - List all templates (metadata only)
- `getTemplate(id)` - Get full template with fields
- `deleteTemplate(id)` - Delete a template
- `updateTemplate(id, command)` - Natural language update
- `applyChanges(id, changes)` - Apply proposed changes
- `downloadTemplate(id)` - Download as file blob
- Includes methods from Path 4 for completeness

#### 6. **State Management** (`src/store/useTemplateStore.ts`)
Using **Zustand** for minimal, efficient state management:
- Template list state with loading/error handling
- Current template state
- Chat history state with messages
- Actions for CRUD operations
- Real-time updates on changes

#### 7. **TypeScript Types** (`src/types/index.ts`)
- `Field` - Document field definition
- `Template` - Complete template structure
- `TemplateMetadata` - List view metadata
- `UpdateRequest` - Natural language command request
- `UpdateResponse` - AI response with proposed changes
- `ChatMessage` - Chat conversation message

#### 8. **Routing** (`src/App.tsx`)
Using **React Router** with routes:
- `/` - Home page with project overview
- `/upload` - Upload new document (placeholder for Path 4)
- `/templates` - Template library
- `/edit/:id` - Edit specific template

#### 9. **Layout Component**
- Responsive navigation header
- Active route highlighting
- Conditional navigation (hidden on edit page)
- Spot Edit branding

## Technology Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 4
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Routing**: React Router 7
- **Package Manager**: npm

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx       # Natural language chat UI
│   │   ├── DocumentPreview.tsx     # Document viewer with field highlighting
│   │   └── TemplateLibrary.tsx     # Template grid/list view
│   ├── pages/
│   │   ├── Home.tsx                # Landing page
│   │   ├── Upload.tsx              # Upload page (placeholder)
│   │   ├── Templates.tsx           # Template library page
│   │   └── Edit.tsx                # Template editing page
│   ├── api/
│   │   └── client.ts               # Axios API client
│   ├── store/
│   │   └── useTemplateStore.ts     # Zustand state management
│   ├── types/
│   │   └── index.ts                # TypeScript type definitions
│   ├── App.tsx                     # Main app with routing
│   ├── main.tsx                    # Entry point
│   └── index.css                   # Global styles with Tailwind
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── tsconfig.json
```

## Features

### Template Library
- Browse all saved templates
- Search by template name
- View template metadata (date, field count)
- Delete templates with confirmation
- Quick navigation to edit page

### Template Editing
- Split-screen interface
- Real-time document preview with field highlighting
- Natural language editing via chat
- Review proposed changes before applying
- Download updated documents
- Conversation history

### Natural Language Commands
Examples of supported commands:
- "Change the due date to next Friday"
- "Update all email addresses to john@example.com"
- "Set the project name to 'Q4 Report'"

## Dependencies on Other Paths

This implementation is designed to work with:

- **Path 3**: Backend API endpoints (not yet implemented)
  - All API calls are configured but will fail until backend is available
  - Mock data can be used for testing

- **Path 4**: Shared types and Upload UI (partially implemented)
  - Types are complete and shared
  - Upload page is a placeholder awaiting Path 4 implementation

## Testing

The application successfully builds without errors:

```bash
✓ built in 2.47s
dist/index.html                   0.46 kB
dist/assets/index-DcWg-y2K.css    4.11 kB
dist/assets/index-C38gY_vs.js   291.70 kB
```

## Next Steps

1. **Backend Integration**: Connect to Path 3 backend API endpoints
2. **Upload Flow**: Complete Path 4 upload and confirmation UI
3. **Testing**: Add unit and integration tests
4. **E2E Testing**: Test complete workflows
5. **Accessibility**: Enhance ARIA labels and keyboard navigation
6. **Mobile**: Optimize responsive design for mobile devices

## Notes

- The application is fully typed with TypeScript
- All components use React functional components with hooks
- State management is minimal and efficient using Zustand
- Styling uses Tailwind utility classes for consistency
- Code follows React best practices and conventions
