# Figma Design Specification: AI Memory Service UI

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [User Personas & Use Cases](#2-user-personas--use-cases)
3. [Information Architecture](#3-information-architecture)
4. [User Flows](#4-user-flows)
5. [UI Components](#5-ui-components)
6. [Screen Layouts](#6-screen-layouts)
7. [Data Visualization](#7-data-visualization)
8. [Interaction Patterns](#8-interaction-patterns)
9. [API Integration Points](#9-api-integration-points)
10. [Design Considerations](#10-design-considerations)

---

## 1. Project Overview

### 1.1 System Description
The AI Memory Service is a cognitive memory system that transforms AI interactions from simple storage into a sophisticated architecture. It evaluates, reinforces, and connects knowledge like a human brain, using MongoDB Atlas vector search and AWS Bedrock AI services.

### 1.2 Core Features
- **Memory Storage**: Stores conversation messages and creates memory nodes
- **Importance Assessment**: AI-powered evaluation of memory significance (0.1-1.0 scale)
- **Memory Reinforcement**: Strengthens memories through repetition
- **Memory Decay**: Gradually reduces importance of unused memories
- **Memory Merging**: Combines related information for coherent knowledge
- **Memory Pruning**: Removes less important memories when capacity is reached (max 5 per user)
- **Hybrid Search**: Combines vector (semantic) and full-text search
- **Context Retrieval**: Retrieves conversation context around specific points
- **AI Summarization**: Generates summaries of conversations and memories

### 1.3 Technical Stack
- **Backend**: FastAPI (Python 3.10+)
- **Database**: MongoDB Atlas with vector search
- **AI Services**: AWS Bedrock (Titan embeddings, Claude LLM)
- **API Port**: 8182 (default)

### 1.4 Key Data Entities

#### Conversation Messages
- `user_id`: Unique user identifier
- `conversation_id`: Groups related messages
- `type`: "human" or "ai"
- `text`: Message content
- `timestamp`: UTC timestamp
- `embeddings`: Vector representation (1536 dimensions)

#### Memory Nodes
- `id`: Unique memory identifier
- `user_id`: Owner of the memory
- `content`: Full memory content
- `summary`: One-sentence summary
- `importance`: AI-assessed importance (0.1-1.0)
- `access_count`: Number of times accessed
- `effective_importance`: Calculated as `importance * (1 + ln(access_count + 1))`
- `timestamp`: Creation time
- `embeddings`: Vector representation

---

## 2. User Personas & Use Cases

### 2.1 Primary Persona: AI Assistant User
**Profile**: Individual using an AI assistant that remembers context across conversations

**Goals**:
- Have the AI remember important information
- Retrieve relevant context from past conversations
- See what the AI remembers about them
- Understand how memories evolve over time

**Pain Points**:
- Forgetting important details between sessions
- Lack of transparency about what's remembered
- No way to see memory importance or relevance

### 2.2 Use Cases

#### UC1: Adding Conversation Messages
**Scenario**: User sends a message to the AI assistant
- User types a message
- System stores the message
- If message is significant (human, >30 chars), creates/updates memory
- User sees confirmation

#### UC2: Retrieving Memories
**Scenario**: User asks a question that requires past context
- User enters a query
- System searches conversations and memory nodes
- Returns relevant conversation context, summary, and similar memories
- User sees organized results with importance scores

#### UC3: Viewing Memory Evolution
**Scenario**: User wants to see how memories have changed
- User views memory list
- Sees importance scores, access counts, timestamps
- Can see which memories were reinforced, merged, or pruned

#### UC4: Understanding Memory Relationships
**Scenario**: User wants to see how memories connect
- User views a memory
- Sees similar memories with similarity scores
- Understands how memories relate to each other

---

## 3. Information Architecture

### 3.1 Data Hierarchy

```
User
├── Conversations (multiple)
│   ├── Messages (multiple per conversation)
│   │   ├── Human messages
│   │   └── AI messages
│   └── Conversation Metadata
└── Memory Nodes (max 5 per user)
    ├── Content
    ├── Summary
    ├── Importance Metrics
    └── Relationships (similarity to other memories)
```

### 3.2 API Endpoints Structure

#### POST `/conversation/`
**Purpose**: Add a message to conversation history

**Request Body**:
```json
{
  "user_id": "string (required, min 1 char)",
  "conversation_id": "string (required, min 1 char)",
  "type": "human" | "ai",
  "text": "string (required, min 1 char)",
  "timestamp": "ISO 8601 UTC string (optional)"
}
```

**Response**:
```json
{
  "message": "Message added successfully"
}
```

**UI Implications**:
- Form with fields: user_id, conversation_id, type selector, text input, optional timestamp
- Submit button
- Success/error feedback
- Auto-triggers memory creation for significant human messages

#### GET `/retrieve_memory/`
**Purpose**: Retrieve memory items, context, and similar memory nodes

**Query Parameters**:
- `user_id`: string (required)
- `text`: string (required) - search query

**Response**:
```json
{
  "related_conversation": [
    {
      "_id": "string",
      "user_id": "string",
      "conversation_id": "string",
      "type": "human" | "ai",
      "text": "string",
      "timestamp": "ISO 8601 UTC string"
    }
  ],
  "conversation_summary": "AI-generated summary string",
  "similar_memories": [
    {
      "content": "string",
      "summary": "string",
      "similarity": 0.0-1.0,
      "importance": 0.1-1.0
    }
  ]
}
```

**UI Implications**:
- Search input field
- Results section with three distinct areas:
  1. Related conversation messages (chronological)
  2. Conversation summary (highlighted)
  3. Similar memories list (with scores)

#### GET `/health`
**Purpose**: Health check

**Response**:
```json
{
  "status": "healthy"
}
```

**UI Implications**:
- Status indicator in header/footer
- System health monitoring

### 3.3 Memory Cognitive Processes

#### Memory Creation Flow
1. User sends significant message (>30 chars, human type)
2. System generates embedding
3. Checks for similar existing memories (similarity > 0.85 = reinforce, else create new)
4. If new: Assesses importance (1-10 scale, normalized to 0.1-1.0)
5. Generates summary
6. Creates memory node
7. Checks for mergeable memories (similarity 0.7-0.85)
8. Updates importance of other memories
9. Prunes if count > MAX_DEPTH (5)

#### Memory Retrieval Flow
1. User enters query
2. System generates query embedding
3. Parallel operations:
   - Hybrid search (vector + full-text) on conversations
   - Vector search on memory nodes
4. Retrieves conversation context around matches
5. Generates conversation summary
6. Calculates effective importance for memories
7. Returns combined results

---

## 4. User Flows

### 4.1 Flow 1: Starting a Conversation

```
[User opens app]
    ↓
[User enters user_id and conversation_id]
    ↓
[User types message]
    ↓
[User selects message type: human/ai]
    ↓
[User clicks "Send Message"]
    ↓
[System processes message]
    ↓
[If significant human message: Creates/updates memory]
    ↓
[Shows success confirmation]
    ↓
[Optionally shows memory creation notification]
```

**UI Screens Needed**:
- Conversation input form
- Success message/toast
- Memory creation notification (optional)

### 4.2 Flow 2: Searching Memories

```
[User navigates to search]
    ↓
[User enters search query]
    ↓
[User clicks "Search" or presses Enter]
    ↓
[Loading state shown]
    ↓
[Results displayed in three sections:]
    ├─ Related Conversation (messages with context)
    ├─ Conversation Summary (AI-generated)
    └─ Similar Memories (with scores)
    ↓
[User can expand/collapse sections]
    ↓
[User can click on memory to see details]
```

**UI Screens Needed**:
- Search interface
- Loading state
- Results page with three sections
- Memory detail view (optional)

### 4.3 Flow 3: Viewing Memory Dashboard

```
[User navigates to Memory Dashboard]
    ↓
[System loads user's memory nodes]
    ↓
[Displays memory list with:]
    ├─ Summary
    ├─ Importance score (visual indicator)
    ├─ Access count
    ├─ Last accessed time
    └─ Similarity relationships
    ↓
[User can filter/sort memories]
    ↓
[User can view memory details]
    ↓
[User can see memory evolution timeline]
```

**UI Screens Needed**:
- Memory dashboard/list view
- Memory detail view
- Memory evolution timeline
- Filter/sort controls

### 4.4 Flow 4: Understanding Memory Relationships

```
[User views a memory]
    ↓
[System shows memory details]
    ↓
[System displays similar memories section]
    ↓
[Shows similarity scores (0.0-1.0)]
    ↓
[User can click on similar memory]
    ↓
[Navigates to that memory's detail view]
    ↓
[Shows relationship visualization]
```

**UI Screens Needed**:
- Memory detail view
- Similar memories list
- Relationship visualization (network graph optional)

---

## 5. UI Components

### 5.1 Form Components

#### Message Input Form
**Purpose**: Add conversation messages

**Fields**:
- `User ID` (text input, required)
- `Conversation ID` (text input, required)
- `Message Type` (radio buttons or dropdown: "Human" | "AI")
- `Message Text` (textarea, required, min 1 char)
- `Timestamp` (datetime picker, optional, defaults to now)

**Actions**:
- Submit button ("Send Message")
- Clear/Reset button

**Validation**:
- All required fields must be filled
- Message type must be "human" or "ai"
- Text must be at least 1 character
- Timestamp must be valid ISO 8601 format

**Visual States**:
- Default
- Validating
- Submitting (loading)
- Success
- Error

#### Search Form
**Purpose**: Search memories and conversations

**Fields**:
- `User ID` (text input, required)
- `Search Query` (text input, required, placeholder: "Enter your search query...")

**Actions**:
- Search button ("Search" or icon)
- Clear button

**Visual States**:
- Default
- Searching (loading)
- Results displayed
- No results
- Error

### 5.2 Display Components

#### Conversation Message Card
**Purpose**: Display individual conversation messages

**Content**:
- Message type indicator (Human/AI badge)
- Message text
- Timestamp (formatted, relative time option)
- Conversation ID (optional, collapsible)

**Visual Design**:
- Different styling for human vs AI messages
- Timestamp in muted color
- Expandable for long messages

#### Memory Node Card
**Purpose**: Display memory node information

**Content**:
- Summary (prominent)
- Full content (expandable)
- Importance score (0.1-1.0) with visual indicator
- Access count
- Effective importance (calculated)
- Timestamp (creation time)
- Last accessed time

**Visual Design**:
- Importance score as progress bar or gauge
- Color coding based on importance (low/medium/high)
- Expandable content section
- Similarity scores to other memories (if shown)

#### Conversation Summary Card
**Purpose**: Display AI-generated conversation summary

**Content**:
- Summary text (formatted, multi-paragraph support)
- Source conversation ID
- Generated timestamp

**Visual Design**:
- Highlighted/emphasized styling
- Readable typography
- Optional expand/collapse

#### Similar Memories List
**Purpose**: Display related memory nodes

**Content**:
- List of memory cards
- Similarity score for each (0.0-1.0)
- Sortable by similarity or importance

**Visual Design**:
- Similarity score as percentage or decimal
- Visual similarity indicator (bar, color)
- Clickable to view full memory

### 5.3 Navigation Components

#### Header/Navigation Bar
**Purpose**: Main navigation

**Elements**:
- App logo/name ("AI Memory Service")
- Navigation links:
  - Home/Conversations
  - Search Memories
  - Memory Dashboard
  - Health Status indicator
- User ID display (if applicable)

#### Sidebar (Optional)
**Purpose**: Secondary navigation or filters

**Elements**:
- Quick filters
- Recent searches
- Memory categories (if implemented)

### 5.4 Feedback Components

#### Loading Spinner
**Purpose**: Indicate processing

**Use Cases**:
- Sending message
- Searching memories
- Loading memory dashboard

#### Toast Notifications
**Purpose**: Show success/error messages

**Types**:
- Success (green): "Message added successfully"
- Error (red): Error messages with details
- Info (blue): Memory created/updated notifications
- Warning (yellow): Validation warnings

#### Empty States
**Purpose**: Handle no data scenarios

**Scenarios**:
- No conversations found
- No memories found
- No search results
- Empty memory dashboard

### 5.5 Data Visualization Components

#### Importance Score Indicator
**Purpose**: Visualize memory importance

**Options**:
- Progress bar (0-100% based on 0.1-1.0 scale)
- Gauge/chart
- Color-coded badge
- Star rating (5 stars = 1.0, scaled)

#### Similarity Score Indicator
**Purpose**: Visualize similarity between memories

**Options**:
- Percentage display
- Progress bar
- Color gradient (red = low, green = high)
- Visual connection line thickness

#### Memory Timeline
**Purpose**: Show memory evolution over time

**Elements**:
- Timeline axis (chronological)
- Memory nodes as points/events
- Importance changes over time
- Access events
- Merge/prune events

#### Memory Network Graph (Advanced)
**Purpose**: Visualize relationships between memories

**Elements**:
- Nodes = memories
- Edges = similarity relationships
- Node size = importance
- Edge thickness = similarity score
- Color coding = categories (if implemented)

---

## 6. Screen Layouts

### 6.1 Home/Conversation Input Screen

**Layout Structure**:
```
┌─────────────────────────────────────────┐
│ Header: AI Memory Service              │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Add Conversation Message        │   │
│  ├─────────────────────────────────┤   │
│  │ User ID: [____________]         │   │
│  │ Conversation ID: [________]     │   │
│  │                                 │   │
│  │ Message Type: ( ) Human ( ) AI  │   │
│  │                                 │   │
│  │ Message:                        │   │
│  │ ┌─────────────────────────────┐ │   │
│  │ │                             │ │   │
│  │ │                             │ │   │
│  │ └─────────────────────────────┘ │   │
│  │                                 │   │
│  │ Timestamp: [Optional]           │   │
│  │                                 │   │
│  │ [Send Message] [Clear]          │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Recent Messages / Activity Feed]     │
│                                         │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Centered form card
- Clear field labels
- Helpful placeholders
- Recent activity section (optional)

### 6.2 Search Results Screen

**Layout Structure**:
```
┌─────────────────────────────────────────┐
│ Header: AI Memory Service              │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Search Memories                 │   │
│  ├─────────────────────────────────┤   │
│  │ User ID: [____________]         │   │
│  │ Query: [___________________] 🔍 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Loading State / Results]              │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Related Conversation             │   │
│  ├─────────────────────────────────┤   │
│  │ [Message Card 1]                 │   │
│  │ [Message Card 2]                 │   │
│  │ [Message Card 3]                 │   │
│  │ ...                              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Conversation Summary            │   │
│  ├─────────────────────────────────┤   │
│  │ [Summary text displayed here]   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Similar Memories                │   │
│  ├─────────────────────────────────┤   │
│  │ [Memory Card 1]                  │   │
│  │   Similarity: 0.85              │   │
│  │   Importance: 0.7               │   │
│  │                                  │   │
│  │ [Memory Card 2]                  │   │
│  │   Similarity: 0.72              │   │
│  │   Importance: 0.9               │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Search form at top
- Three distinct result sections
- Expandable/collapsible sections
- Clear visual hierarchy
- Empty state when no results

### 6.3 Memory Dashboard Screen

**Layout Structure**:
```
┌─────────────────────────────────────────┐
│ Header: AI Memory Service              │
├─────────────────────────────────────────┤
│                                         │
│  Memory Dashboard                       │
│  ┌─────────────────────────────────┐   │
│  │ Filters: [All] [High] [Medium]   │   │
│  │ Sort: [Importance] [Recent]      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Memory 1                         │   │
│  │ Summary: "User prefers Python..."│   │
│  │ Importance: ████████░░ 0.8      │   │
│  │ Accesses: 12 | Created: 2d ago   │   │
│  │ [View Details]                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Memory 2                         │   │
│  │ Summary: "Contact: email@..."    │   │
│  │ Importance: ██████████ 1.0       │   │
│  │ Accesses: 25 | Created: 5d ago  │   │
│  │ [View Details]                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Memory 3, 4, 5...]                    │
│                                         │
│  Status: 5/5 memories (at capacity)    │
│                                         │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Filter and sort controls
- Memory cards in list/grid
- Visual importance indicators
- Capacity indicator (X/5 memories)
- Empty state when no memories

### 6.4 Memory Detail Screen

**Layout Structure**:
```
┌─────────────────────────────────────────┐
│ Header: AI Memory Service              │
│ [← Back to Dashboard]                   │
├─────────────────────────────────────────┤
│                                         │
│  Memory Details                         │
│  ┌─────────────────────────────────┐   │
│  │ Summary                          │   │
│  │ "User prefers Python for backend │   │
│  │  and React for frontend..."      │   │
│  ├─────────────────────────────────┤   │
│  │ Full Content                     │   │
│  │ [Expandable content section]     │   │
│  ├─────────────────────────────────┤   │
│  │ Metrics                          │   │
│  │ Importance: 0.8                  │   │
│  │ Effective Importance: 1.2        │   │
│  │ Access Count: 12                 │   │
│  │ Created: Jan 15, 2024            │   │
│  │ Last Accessed: Jan 17, 2024      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Similar Memories                       │
│  ┌─────────────────────────────────┐   │
│  │ [Memory Card] Similarity: 0.85   │   │
│  │ [Memory Card] Similarity: 0.72   │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Breadcrumb navigation
- Full memory information
- Metrics display
- Related memories section
- Action buttons (if editing is implemented)

### 6.5 Health Status Screen (Optional)

**Layout Structure**:
```
┌─────────────────────────────────────────┐
│ Header: AI Memory Service              │
├─────────────────────────────────────────┤
│                                         │
│  System Health                          │
│  ┌─────────────────────────────────┐   │
│  │ Status: 🟢 Healthy               │   │
│  │                                 │   │
│  │ API: Operational                │   │
│  │ Database: Connected             │   │
│  │ Bedrock: Available              │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 7. Data Visualization

### 7.1 Importance Score Visualization

**Design Options**:

#### Option A: Progress Bar
```
Importance: [████████░░] 0.8
```
- Simple, clear
- Easy to compare across memories
- Color coding: Red (0.1-0.4), Yellow (0.4-0.7), Green (0.7-1.0)

#### Option B: Circular Gauge
```
     ┌───┐
    ╱ 80% ╲
   │       │
   └───────┘
```
- More visually interesting
- Takes more space
- Good for detail views

#### Option C: Star Rating
```
Importance: ★★★★☆ (4/5 stars = 0.8)
```
- Intuitive
- Familiar pattern
- Less precise

**Recommendation**: Use Progress Bar for list views, Gauge for detail views

### 7.2 Similarity Score Visualization

**Design Options**:

#### Option A: Percentage with Color
```
Similarity: 85% [████████░░] (green)
```
- Clear percentage
- Color indicates strength
- Bar shows relative value

#### Option B: Decimal with Badge
```
Similarity: 0.85 [High]
```
- Precise decimal
- Categorical label (Low/Medium/High)
- Compact

**Recommendation**: Use Percentage with Color Bar

### 7.3 Memory Timeline Visualization

**Design**:
```
Timeline: ─────●─────●─────●─────●─────●─────
              Jan 1  Jan 5  Jan 8 Jan 12 Jan 15
              
Memory Events:
● Created (Importance: 0.6)
● Reinforced (Importance: 0.7)
● Accessed (Count: 5)
● Merged with Memory X
● Pruned (if applicable)
```

**Elements**:
- Horizontal timeline axis
- Memory events as markers
- Event details on hover/click
- Color coding by event type

### 7.4 Memory Network Graph (Advanced)

**Design**:
```
        [Memory 1]
         /    \
        /      \
   [Memory 2] [Memory 3]
        \      /
         \    /
        [Memory 4]
```

**Properties**:
- Node size = Importance (larger = more important)
- Edge thickness = Similarity (thicker = more similar)
- Edge color = Similarity strength
- Node color = Category (if implemented)
- Interactive: Click to view details, drag to rearrange

**Use Case**: Advanced view for power users to understand memory relationships

---

## 8. Interaction Patterns

### 8.1 Form Interactions

#### Message Input Form
- **Real-time Validation**: Show errors as user types
- **Auto-fill**: Remember last used user_id and conversation_id
- **Keyboard Shortcuts**: Enter to submit (with Ctrl/Cmd)
- **Loading State**: Disable submit button, show spinner during processing
- **Success Feedback**: Toast notification + form reset (optional)
- **Error Handling**: Show specific error messages, highlight invalid fields

#### Search Form
- **Auto-search**: Optional debounced search as user types
- **Search History**: Remember recent searches
- **Keyboard Shortcuts**: Enter to search, Escape to clear
- **Loading State**: Show spinner, disable input during search
- **Results Highlighting**: Highlight matching terms in results

### 8.2 List Interactions

#### Memory List
- **Infinite Scroll**: Load more as user scrolls (if >5 memories)
- **Pagination**: Alternative to infinite scroll
- **Filtering**: Real-time filter application
- **Sorting**: Click column headers to sort
- **Selection**: Multi-select for bulk actions (if implemented)
- **Expand/Collapse**: Expand memory cards to see full content

#### Conversation List
- **Chronological Order**: Default sort by timestamp
- **Grouping**: Group by conversation_id
- **Expandable**: Show/hide conversation threads
- **Context Highlighting**: Highlight search matches

### 8.3 Card Interactions

#### Memory Card
- **Hover**: Show preview of full content
- **Click**: Navigate to detail view
- **Expand**: Inline expansion of full content
- **Actions**: Context menu (view, edit, delete if implemented)

#### Message Card
- **Hover**: Highlight message
- **Click**: Show in context (surrounding messages)
- **Copy**: Copy message text
- **Timestamp**: Show relative time, hover for absolute time

### 8.4 Navigation Patterns

#### Breadcrumbs
- Home > Memory Dashboard > Memory Detail
- Clickable navigation path

#### Back Button
- Browser back button support
- Explicit back button in header

#### Deep Linking
- Support URL parameters for direct navigation
- Shareable links to specific memories

### 8.5 Feedback Patterns

#### Loading States
- **Skeleton Screens**: Show content structure while loading
- **Spinners**: For quick operations
- **Progress Bars**: For longer operations
- **Optimistic Updates**: Show expected result immediately

#### Error States
- **Inline Errors**: Show near relevant fields
- **Toast Notifications**: For API errors
- **Error Pages**: For critical failures
- **Retry Mechanisms**: Allow user to retry failed operations

#### Success States
- **Toast Notifications**: Brief success messages
- **Visual Confirmation**: Checkmarks, animations
- **Auto-dismiss**: Success messages fade after 3-5 seconds

---

## 9. API Integration Points

### 9.1 Endpoint Mapping

#### POST `/conversation/`
**UI Integration**:
- Form submission handler
- Request body construction from form fields
- Response handling (success/error)
- Optional: Poll for memory creation status

**Error Handling**:
- 400: Validation errors (show field-specific errors)
- 500: Server errors (show generic error message)
- Network errors: Show connection error

**Loading States**:
- Disable form during submission
- Show loading spinner
- Prevent duplicate submissions

#### GET `/retrieve_memory/`
**UI Integration**:
- Search form submission
- Query parameter construction
- Response parsing and display
- Three-section layout for results

**Error Handling**:
- 400: Invalid parameters (show error)
- 404: No results (show empty state)
- 500: Server errors (show error message)

**Loading States**:
- Show skeleton screens or spinner
- Disable search during request
- Show "Searching..." message

#### GET `/health`
**UI Integration**:
- Periodic health checks (every 30-60 seconds)
- Status indicator in header
- Optional: Health dashboard page

**Display**:
- Green indicator: Healthy
- Red indicator: Unhealthy
- Yellow indicator: Unknown/Checking

### 9.2 Data Transformation

#### Request Transformation
- Convert form data to API format
- Handle timestamp formatting (ISO 8601)
- Validate before sending
- Sanitize user input

#### Response Transformation
- Parse JSON responses
- Format timestamps for display
- Calculate derived values (effective importance)
- Handle null/empty responses

### 9.3 Real-time Updates (Future Enhancement)

**Potential Features**:
- WebSocket connection for real-time memory updates
- Push notifications for memory creation/reinforcement
- Live updates to memory dashboard

**UI Considerations**:
- Connection status indicator
- Auto-refresh mechanisms
- Conflict resolution for concurrent updates

### 9.4 Caching Strategy

**Client-side Caching**:
- Cache recent search results
- Cache memory dashboard data
- Cache user preferences
- Invalidate on updates

**UI Implications**:
- Show cached data immediately
- Update in background
- Indicate when data is stale

---

## 10. Design Considerations

### 10.1 Visual Hierarchy

#### Primary Actions
- **Send Message**: Primary button, prominent
- **Search**: Primary action, always visible
- **View Memory**: Secondary action, in cards

#### Information Priority
1. **Search Results**: Most important, top of page
2. **Memory Summaries**: Key information, prominent
3. **Importance Scores**: Visual indicators, easy to scan
4. **Metadata**: Timestamps, IDs, secondary information

#### Typography Hierarchy
- **H1**: Page titles
- **H2**: Section headers
- **H3**: Card titles
- **Body**: Content text
- **Small**: Metadata, timestamps

### 10.2 Color System

#### Semantic Colors
- **Primary**: Actions, links (Blue)
- **Success**: Confirmations, positive states (Green)
- **Warning**: Cautions, medium importance (Yellow/Orange)
- **Error**: Errors, low importance (Red)
- **Info**: Information, neutral (Blue/Gray)

#### Importance Color Mapping
- **High (0.7-1.0)**: Green
- **Medium (0.4-0.7)**: Yellow/Orange
- **Low (0.1-0.4)**: Red

#### Message Type Colors
- **Human Messages**: Blue/User color
- **AI Messages**: Gray/System color

### 10.3 Spacing & Layout

#### Grid System
- 12-column grid (desktop)
- 8-column grid (tablet)
- 4-column grid (mobile)
- Consistent gutters (16px, 24px, 32px)

#### Card Spacing
- 16px padding inside cards
- 24px margin between cards
- 32px margin between sections

#### Form Spacing
- 16px between form fields
- 24px between form sections
- 32px margin around form

### 10.4 Responsive Design

#### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

#### Mobile Adaptations
- Stack form fields vertically
- Full-width cards
- Collapsible sections
- Bottom navigation (optional)
- Touch-friendly targets (min 44px)

#### Tablet Adaptations
- Two-column layouts where appropriate
- Sidebar navigation (optional)
- Optimized card sizes

#### Desktop Adaptations
- Multi-column layouts
- Sidebar navigation
- Hover states
- Keyboard navigation support

### 10.5 Accessibility

#### WCAG Compliance
- **Contrast Ratios**: Minimum 4.5:1 for text
- **Keyboard Navigation**: All interactive elements accessible
- **Screen Readers**: Proper ARIA labels
- **Focus Indicators**: Visible focus states

#### Implementation
- Semantic HTML
- ARIA labels for icons and buttons
- Alt text for images
- Form labels associated with inputs
- Error messages associated with fields

### 10.6 Performance Considerations

#### Loading Optimization
- Lazy load memory lists
- Pagination or infinite scroll
- Skeleton screens during loading
- Optimistic UI updates

#### Data Optimization
- Debounce search inputs
- Cache API responses
- Minimize API calls
- Batch operations where possible

### 10.7 User Experience Principles

#### Clarity
- Clear labels and instructions
- Obvious primary actions
- Intuitive navigation
- Helpful error messages

#### Feedback
- Immediate visual feedback
- Loading states for all async operations
- Success/error notifications
- Progress indicators

#### Efficiency
- Keyboard shortcuts
- Auto-save drafts (optional)
- Remember user preferences
- Quick actions

#### Consistency
- Consistent component usage
- Uniform spacing and styling
- Predictable interactions
- Standard patterns

### 10.8 Design System Components

#### Recommended Component Library
- Material-UI (MUI)
- Ant Design
- Chakra UI
- Custom design system

#### Key Components Needed
- Buttons (primary, secondary, text)
- Input fields (text, textarea, select)
- Cards
- Badges/Tags
- Progress bars
- Toast notifications
- Modals/Dialogs
- Loading spinners
- Empty states

### 10.9 Micro-interactions

#### Subtle Animations
- Button hover effects
- Card hover elevation
- Form field focus states
- Loading spinner rotation
- Toast slide-in animations

#### Transitions
- Page transitions (fade, slide)
- Modal open/close
- Expand/collapse animations
- List item animations

#### Feedback
- Button press animations
- Success checkmark animation
- Error shake animation
- Progress bar fill animation

---

## Appendix A: Data Model Reference

### A.1 MessageInput Model
```typescript
interface MessageInput {
  user_id: string;           // Required, min 1 char
  conversation_id: string;    // Required, min 1 char
  type: "human" | "ai";      // Required
  text: string;              // Required, min 1 char
  timestamp?: string;        // Optional, ISO 8601 UTC
}
```

### A.2 MemoryNode Model
```typescript
interface MemoryNode {
  id: string;                // MongoDB ObjectId as string
  user_id: string;
  content: string;           // Full memory content
  summary: string;           // One-sentence summary
  importance: number;        // 0.1 to 1.0
  access_count: number;      // Integer, starts at 0
  effective_importance: number; // Calculated: importance * (1 + ln(access_count + 1))
  timestamp: string;         // ISO 8601 UTC
  last_accessed?: string;    // ISO 8601 UTC
  embeddings: number[];     // 1536-dimensional vector
}
```

### A.3 Search Response Model
```typescript
interface SearchResponse {
  related_conversation: ConversationMessage[] | "No conversation found";
  conversation_summary: string | "No summary found";
  similar_memories: SimilarMemory[] | "No similar memories found";
}

interface ConversationMessage {
  _id: string;
  user_id: string;
  conversation_id: string;
  type: "human" | "ai";
  text: string;
  timestamp: string;         // ISO 8601 UTC
}

interface SimilarMemory {
  content: string;
  summary: string;
  similarity: number;        // 0.0 to 1.0
  importance: number;        // 0.1 to 1.0
}
```

---

## Appendix B: Configuration Parameters

### B.1 Memory System Parameters
- **MAX_DEPTH**: 5 (maximum memories per user)
- **SIMILARITY_THRESHOLD**: 0.7 (for reinforcement/merging)
- **DECAY_FACTOR**: 0.99 (memory decay rate)
- **REINFORCEMENT_FACTOR**: 1.1 (memory reinforcement rate)

### B.2 Search Parameters
- **Hybrid Search Weight**: 0.8 (vector) vs 0.2 (full-text)
- **Top N Results**: 5 (conversations), 3 (similar memories)
- **Similarity Thresholds**:
  - > 0.85: Reinforce existing memory
  - 0.7-0.85: Merge with existing memory
  - < 0.7: Create new memory

### B.3 Memory Creation Thresholds
- **Minimum Message Length**: 30 characters (for human messages)
- **Importance Assessment**: 1-10 scale, normalized to 0.1-1.0

---

## Appendix C: Example User Scenarios

### C.1 Scenario: First-time User
1. User opens application
2. Enters user_id: "alex_chen"
3. Creates new conversation_id: "conv_001"
4. Sends message: "Hello, I'm Alex and I work as a data scientist"
5. System creates memory with importance ~0.6
6. User sees confirmation and memory creation notification

### C.2 Scenario: Returning User with Existing Memories
1. User opens application
2. Enters user_id: "alex_chen"
3. Searches: "What do you know about me?"
4. System retrieves:
   - Related conversations about user's profession
   - Summary: "User is a data scientist named Alex"
   - Similar memories with importance scores
5. User views memory dashboard to see all 5 stored memories

### C.3 Scenario: Memory Evolution
1. User sends message about Python preference
2. System creates memory (importance: 0.7)
3. User later mentions Python again in different context
4. System reinforces memory (importance: 0.77, access_count: 1)
5. User views memory and sees updated importance score
6. System shows memory evolution timeline

### C.4 Scenario: Memory Merging
1. User has memory about "contact: email@old.com"
2. User sends message: "My new email is email@new.com"
3. System creates new memory (similarity: 0.75 to old memory)
4. System merges memories into: "Contact: email@new.com (updated from email@old.com)"
5. User sees single merged memory with higher importance

### C.5 Scenario: Memory Pruning
1. User has 5 memories (at capacity)
2. User sends new significant message
3. System creates new memory
4. System prunes least important memory (importance: 0.2)
5. User still has 5 memories, but oldest/lowest importance removed
6. User can see pruning event in memory timeline (if implemented)

---

## Appendix D: Design Checklist

### D.1 Core Screens
- [ ] Home/Conversation Input Screen
- [ ] Search Results Screen
- [ ] Memory Dashboard Screen
- [ ] Memory Detail Screen
- [ ] Health Status Screen (optional)

### D.2 Components
- [ ] Message Input Form
- [ ] Search Form
- [ ] Conversation Message Card
- [ ] Memory Node Card
- [ ] Conversation Summary Card
- [ ] Similar Memories List
- [ ] Importance Score Indicator
- [ ] Similarity Score Indicator
- [ ] Loading Spinner
- [ ] Toast Notifications
- [ ] Empty States

### D.3 Interactions
- [ ] Form validation and submission
- [ ] Search functionality
- [ ] Memory card interactions
- [ ] Navigation patterns
- [ ] Error handling
- [ ] Loading states
- [ ] Success feedback

### D.4 Responsive Design
- [ ] Mobile layouts
- [ ] Tablet layouts
- [ ] Desktop layouts
- [ ] Touch-friendly targets
- [ ] Keyboard navigation

### D.5 Accessibility
- [ ] WCAG contrast compliance
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] ARIA labels
- [ ] Focus indicators

### D.6 Visual Design
- [ ] Color system
- [ ] Typography hierarchy
- [ ] Spacing system
- [ ] Icon system
- [ ] Animation guidelines

---

## Conclusion

This design specification provides a comprehensive guide for designing the AI Memory Service UI in Figma. The document covers all aspects from user flows to component specifications, ensuring a cohesive and user-friendly interface that effectively communicates the sophisticated memory system's capabilities.

Key design priorities:
1. **Clarity**: Make complex memory operations understandable
2. **Transparency**: Show users what the system remembers and why
3. **Efficiency**: Enable quick access to memories and context
4. **Visualization**: Use clear indicators for importance and similarity
5. **Feedback**: Provide clear feedback for all user actions

Use this document as a reference when creating Figma designs, ensuring all screens, components, and interactions align with the system's architecture and user needs.
