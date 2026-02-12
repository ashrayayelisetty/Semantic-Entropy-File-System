# UI Improvements and Bidirectional File Management - Requirements

## Problem Statement
The current SEFS UI is read-only and has visualization issues:
- Users cannot add files through the UI (only by dropping files in the folder)
- The gravity view doesn't clearly show clusters as grouped entities
- Unnecessary legends clutter the interface
- No clear way to see which files belong to which cluster
- Cluster representation is confusing

## Expected Behavior
1. Users can upload/add files directly through the UI
2. Clusters are displayed as visual boxes/containers
3. Files are shown inside their respective cluster boxes
4. Cluster names are prominently displayed
5. Clean, minimal UI without unnecessary elements

## User Stories

### 1.1 As a user, I want to add files through the UI
**Acceptance Criteria:**
- There is a visible "Add File" or "Upload File" button in the UI
- Clicking the button opens a file picker dialog
- Selected files are copied to the sefs_root folder
- The system automatically processes and organizes new files
- User sees feedback when files are added successfully

### 1.2 As a user, I want to see clusters as visual groups
**Acceptance Criteria:**
- Clusters are displayed as boxes/containers in the visualization
- Each cluster box has a clear border and background
- The cluster name is displayed prominently on each box
- Files are visually contained within their cluster boxes
- Uncategorized files are shown in a separate "Uncategorized" box

### 1.3 As a user, I want a clean, minimal UI
**Acceptance Criteria:**
- Unnecessary legends are removed from the visualization
- The interface focuses on the cluster view and file management
- Color coding is intuitive without needing a legend
- The UI is not cluttered with redundant information

### 1.4 As a user, I want to see cluster contents clearly
**Acceptance Criteria:**
- Each cluster box shows its name at the top
- Files within a cluster are listed or displayed inside the box
- File count is visible for each cluster
- I can click on files to see their metadata
- The visualization scales well with different numbers of clusters and files

### 1.5 As a user, I want bidirectional file management
**Acceptance Criteria:**
- I can add files through the UI
- I can still add files by dropping them in the sefs_root folder
- Both methods trigger automatic organization
- The UI updates in real-time when files are added either way

## Technical Context
- Frontend: React application
- Current visualization: GravityView component with force-directed graph
- Backend: FastAPI with file monitoring
- File operations: Python pathlib and shutil

## Constraints
- Must maintain real-time updates via WebSocket
- File uploads should be secure (validate file types)
- UI should remain responsive during file processing
- Must work on Windows, macOS, and Linux
