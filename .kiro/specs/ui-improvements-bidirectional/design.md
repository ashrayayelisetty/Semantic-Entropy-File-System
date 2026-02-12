# UI Improvements and Bidirectional File Management - Design Document

## Overview

This feature transforms the SEFS UI from a read-only force-directed graph visualization into an interactive bidirectional file management system with a box-based cluster layout. Users will be able to upload files directly through the UI, and clusters will be displayed as clear visual containers with files grouped inside them.

The design maintains the existing real-time WebSocket architecture while adding file upload capabilities and completely redesigning the visualization component.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  FileUpload    │  │  ClusterBoxView  │  │  App.js     │ │
│  │  Component     │  │  Component       │  │  (Main)     │ │
│  └────────┬───────┘  └────────┬─────────┘  └──────┬──────┘ │
│           │                   │                    │         │
│           └───────────────────┴────────────────────┘         │
│                              │                               │
└──────────────────────────────┼───────────────────────────────┘
                               │
                    HTTP/WebSocket (CORS)
                               │
┌──────────────────────────────┼───────────────────────────────┐
│                        Backend (FastAPI)                      │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐ │
│  │  /upload-file  │  │  /graph          │  │  /ws        │ │
│  │  endpoint      │  │  endpoint        │  │  WebSocket  │ │
│  └────────┬───────┘  └────────┬─────────┘  └──────┬──────┘ │
│           │                   │                    │         │
│           └───────────────────┴────────────────────┘         │
│                              │                               │
│                    ┌─────────┴─────────┐                    │
│                    │  SEFSCoordinator  │                    │
│                    │  (Existing)       │                    │
│                    └───────────────────┘                    │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **File Upload Flow**:
   - User clicks "Upload File" button → File picker opens
   - User selects file(s) → FormData created with file(s)
   - POST to `/upload-file` endpoint → File saved to sefs_root
   - Backend triggers file monitoring → Coordinator processes file
   - WebSocket broadcasts update → UI refreshes with new file

2. **Visualization Update Flow**:
   - Component fetches `/graph` endpoint → Returns cluster and file data
   - ClusterBoxView renders clusters as SVG rectangles
   - Files positioned within their cluster boundaries
   - User interactions (click, hover) trigger metadata display

## Components and Interfaces

### Frontend Components

#### FileUpload Component

```javascript
// New component for file upload functionality
interface FileUploadProps {
  onUploadSuccess: (files: string[]) => void;
  onUploadError: (error: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, onUploadError }) => {
  // Handles file selection and upload
  // Returns: Upload button with file input
}
```

**Responsibilities**:
- Render upload button in UI
- Handle file input element
- Create FormData and POST to backend
- Show upload progress/feedback
- Handle errors and success states

#### ClusterBoxView Component

```javascript
// Replaces GravityView.js with box-based layout
interface ClusterBoxViewProps {
  onActivityUpdate: (activities: Activity[]) => void;
  onFileSelect: (file: FileNode) => void;
}

interface ClusterBox {
  id: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  files: FileNode[];
}

interface FileNode {
  id: string;
  label: string;
  cluster: string;
  clusterName: string;
  size: string;
  modified: string;
  path: string;
  x: number;  // Relative to cluster box
  y: number;  // Relative to cluster box
}
```

**Responsibilities**:
- Fetch cluster and file data from `/graph` endpoint
- Calculate cluster box positions and sizes
- Render clusters as SVG rectangles with borders
- Position files within cluster boundaries
- Display cluster names and file counts
- Handle file click events for metadata display
- Remove legend component

**Layout Algorithm**:
```
1. Calculate number of clusters (N)
2. Determine grid layout: cols = ceil(sqrt(N)), rows = ceil(N / cols)
3. Calculate box dimensions: width = viewWidth / cols, height = viewHeight / rows
4. For each cluster:
   - Position box at grid cell (i, j)
   - Calculate file positions within box using grid or force layout
   - Ensure files stay within box boundaries (padding: 20px)
```

### Backend API Endpoints

#### POST /upload-file

```python
@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to sefs_root directory
    
    Args:
        file: Uploaded file from multipart/form-data
    
    Returns:
        {
            "status": "success",
            "filename": str,
            "path": str
        }
    
    Errors:
        400: Invalid file type
        500: File save error
    """
```

**Implementation**:
- Validate file (check size, type if needed)
- Generate safe filename (handle duplicates)
- Save to sefs_root directory
- Return success response
- File monitoring will automatically detect and process

#### GET /graph (Modified)

```python
@app.get("/graph")
def get_graph_data():
    """
    Get cluster and file data for box visualization
    
    Returns:
        {
            "clusters": [
                {
                    "id": str,
                    "name": str,
                    "fileCount": int
                }
            ],
            "files": [
                {
                    "id": str,
                    "label": str,
                    "cluster": str,
                    "clusterName": str,
                    "size": str,
                    "modified": str,
                    "path": str
                }
            ]
        }
    """
```

**Changes from current implementation**:
- Return separate `clusters` and `files` arrays
- Add `fileCount` to cluster objects
- Remove node positioning (x, y) - calculated client-side
- Group files by cluster for easier rendering

## Data Models

### Cluster Data Model

```typescript
interface Cluster {
  id: string;           // Cluster identifier
  name: string;         // Human-readable cluster name
  fileCount: number;    // Number of files in cluster
  x: number;           // Box x position (calculated client-side)
  y: number;           // Box y position (calculated client-side)
  width: number;       // Box width (calculated client-side)
  height: number;      // Box height (calculated client-side)
}
```

### File Data Model

```typescript
interface FileNode {
  id: string;           // File path (unique identifier)
  label: string;        // Display name (filename)
  cluster: string;      // Cluster ID this file belongs to
  clusterName: string;  // Human-readable cluster name
  size: string;         // Formatted file size (e.g., "1.2 MB")
  modified: string;     // Formatted modification date
  path: string;         // Full file path
  x: number;           // Position within cluster (calculated client-side)
  y: number;           // Position within cluster (calculated client-side)
}
```

### Upload Response Model

```typescript
interface UploadResponse {
  status: "success" | "error";
  filename?: string;    // Original filename
  path?: string;        // Saved file path
  error?: string;       // Error message if status is "error"
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing the acceptance criteria, I identified the following testable properties. I've reviewed them for redundancy:

- Properties 2.4 and 4.2 both test that files are positioned within cluster boundaries - these can be combined into a single comprehensive property
- Properties 1.3, 1.4, and 5.1 all relate to the file upload flow - these can be combined into one property about the complete upload pipeline
- Properties 5.2, 5.3, and 5.4 all test the real-time update mechanism - these can be combined into one property about bidirectional updates

The consolidated properties below eliminate this redundancy while maintaining complete coverage.

### Property 1: File upload triggers backend processing
*For any* valid file uploaded through the UI, the file should be saved to sefs_root and automatically processed by the semantic engine, resulting in the file appearing in a cluster.
**Validates: Requirements 1.3, 1.4, 5.1**

### Property 2: Upload feedback is displayed
*For any* file upload operation (success or failure), the UI should display feedback to the user indicating the result.
**Validates: Requirements 1.5**

### Property 3: Cluster names are displayed
*For any* cluster in the visualization, the cluster name should be rendered as a text element within or at the top of the cluster box.
**Validates: Requirements 2.3, 4.1**

### Property 4: Files are contained within cluster boundaries
*For any* file node in the visualization, its position (x, y) should be within the boundaries of its parent cluster box (accounting for padding).
**Validates: Requirements 2.4, 4.2**

### Property 5: Uncategorized files have a default cluster
*For any* file without a cluster assignment, it should be assigned to a cluster named "Uncategorized" and displayed in that cluster's box.
**Validates: Requirements 2.5**

### Property 6: File count is displayed per cluster
*For any* cluster box, the number of files it contains should be displayed as a text element.
**Validates: Requirements 4.3**

### Property 7: File click shows metadata
*For any* file node, clicking it should trigger the metadata panel to become visible with that file's information.
**Validates: Requirements 4.4**

### Property 8: Bidirectional file addition triggers updates
*For any* file added either through the UI or by dropping it in sefs_root, the file should be detected, processed, and the UI should update in real-time via WebSocket.
**Validates: Requirements 5.2, 5.3, 5.4**

## Error Handling

### Frontend Error Handling

**File Upload Errors**:
- File too large: Display error message "File exceeds maximum size limit"
- Network error: Display error message "Upload failed. Please check your connection"
- Invalid file type (if validation added): Display error message "File type not supported"
- Duplicate filename: Backend handles by appending number, no error shown

**Visualization Errors**:
- Empty data: Display message "No files to display. Upload files to get started"
- API fetch failure: Retry with exponential backoff (3 attempts), then show error
- WebSocket disconnect: Attempt reconnection, fall back to polling

### Backend Error Handling

**Upload Endpoint Errors**:
- No file provided: Return 400 with error message
- File save failure: Return 500 with error message, log details
- Disk space full: Return 507 with error message

**Graph Endpoint Errors**:
- Coordinator not initialized: Return 503 with error message
- State retrieval failure: Return 500 with error message, log details

**Security Considerations**:
- Validate file paths to prevent directory traversal
- Sanitize filenames to prevent injection attacks
- Limit file upload size (default: 100MB)
- Check available disk space before accepting uploads

## Testing Strategy

### Unit Testing

**Frontend Unit Tests** (Jest + React Testing Library):
- FileUpload component renders upload button
- FileUpload component opens file picker on click
- FileUpload component shows success message after upload
- FileUpload component shows error message on failure
- ClusterBoxView component renders cluster boxes
- ClusterBoxView component renders cluster names
- ClusterBoxView component renders file count badges
- ClusterBoxView component positions files within clusters
- ClusterBoxView component shows metadata panel on file click
- ClusterBoxView component handles empty data gracefully

**Backend Unit Tests** (pytest):
- Upload endpoint saves file to correct directory
- Upload endpoint handles duplicate filenames
- Upload endpoint validates file data
- Upload endpoint returns correct response format
- Graph endpoint returns clusters and files
- Graph endpoint handles missing coordinator
- Graph endpoint formats file metadata correctly

### Property-Based Testing

**Property Test Configuration**:
- Library: fast-check (JavaScript) for frontend, Hypothesis (Python) for backend
- Minimum iterations: 100 per test
- Each test tagged with: **Feature: ui-improvements-bidirectional, Property {number}: {property_text}**

**Frontend Property Tests**:
1. **Property 2**: Generate random upload results (success/error), verify feedback always appears
2. **Property 3**: Generate random cluster data, verify all cluster names are rendered
3. **Property 4**: Generate random file positions, verify all are within cluster bounds
4. **Property 5**: Generate files with and without clusters, verify uncategorized files appear in "Uncategorized" box
5. **Property 6**: Generate clusters with varying file counts, verify counts are displayed
6. **Property 7**: Generate random file nodes, simulate clicks, verify metadata panel appears

**Backend Property Tests**:
1. **Property 1**: Generate random valid files, upload them, verify they appear in graph data
8. **Property 8**: Generate random files, add via both methods, verify WebSocket broadcasts updates

### Integration Testing

**End-to-End Tests** (Playwright or Cypress):
- Complete file upload flow: select file → upload → see in visualization
- Bidirectional sync: drop file in folder → see in UI
- Cluster visualization: verify boxes, names, counts, file positions
- Metadata display: click file → see metadata panel → close panel
- Real-time updates: add file → verify WebSocket update → verify UI refresh

**Test Data**:
- Small files (< 1KB)
- Medium files (1-10MB)
- Large files (10-50MB)
- Various file types (PDF, TXT, DOCX, etc.)
- Edge cases: empty files, files with special characters in names

### Performance Testing

**Load Testing**:
- Test with 100+ files across 10+ clusters
- Verify visualization renders within 2 seconds
- Verify file upload completes within 5 seconds for 10MB file
- Verify WebSocket updates propagate within 1 second

**Scalability Testing**:
- Test cluster layout algorithm with 1, 5, 10, 20, 50 clusters
- Verify file positioning algorithm with 10, 50, 100, 500 files per cluster
- Verify UI remains responsive with large datasets
