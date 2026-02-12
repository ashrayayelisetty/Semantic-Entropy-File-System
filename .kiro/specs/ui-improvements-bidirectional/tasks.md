# Implementation Plan: UI Improvements and Bidirectional File Management

## Overview

This implementation plan transforms the SEFS UI from a read-only force-directed graph into an interactive bidirectional file management system with a box-based cluster layout. The implementation is divided into backend file upload functionality, frontend visualization redesign, and integration testing.

## Tasks

- [x] 1. Implement backend file upload endpoint
  - [x] 1.1 Create POST /upload-file endpoint in main.py
    - Add endpoint that accepts multipart/form-data with file
    - Validate file exists in request
    - Generate safe filename (handle duplicates by appending numbers)
    - Save file to sefs_root directory
    - Return JSON response with status, filename, and path
    - Add error handling for file save failures
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [ ]* 1.2 Write unit tests for upload endpoint
    - Test successful file upload
    - Test duplicate filename handling
    - Test missing file in request (400 error)
    - Test file save failure (500 error)
    - _Requirements: 1.3_
  
  - [ ]* 1.3 Write property test for upload endpoint
    - **Property 1: File upload triggers backend processing**
    - **Validates: Requirements 1.3, 1.4, 5.1**
    - Generate random valid files, upload them, verify they appear in graph data after processing

- [x] 2. Modify backend /graph endpoint for box visualization
  - [x] 2.1 Update get_graph_data() function
    - Change response structure to return separate "clusters" and "files" arrays
    - Add "fileCount" field to each cluster object
    - Remove x, y coordinates from response (calculated client-side)
    - Ensure "Uncategorized" cluster exists for files without assignments
    - _Requirements: 2.1, 2.5, 4.3_
  
  - [ ]* 2.2 Write unit tests for modified graph endpoint
    - Test clusters array structure
    - Test files array structure
    - Test fileCount calculation
    - Test Uncategorized cluster creation
    - _Requirements: 2.5, 4.3_

- [ ] 3. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Create FileUpload component
  - [x] 4.1 Implement FileUpload.js component
    - Create functional component with upload button
    - Add hidden file input element
    - Implement handleFileSelect to trigger file input click
    - Implement handleFileChange to process selected files
    - Create FormData and POST to /upload-file endpoint
    - Show loading state during upload
    - Call onUploadSuccess callback with uploaded filenames
    - Call onUploadError callback on failure
    - Add basic styling for upload button
    - _Requirements: 1.1, 1.2, 1.3, 1.5_
  
  - [ ]* 4.2 Write unit tests for FileUpload component
    - Test component renders upload button
    - Test clicking button triggers file input
    - Test file selection creates FormData
    - Test successful upload calls onUploadSuccess
    - Test failed upload calls onUploadError
    - _Requirements: 1.1, 1.2, 1.5_
  
  - [ ]* 4.3 Write property test for upload feedback
    - **Property 2: Upload feedback is displayed**
    - **Validates: Requirements 1.5**
    - Generate random upload results (success/error), verify feedback always appears

- [x] 5. Create ClusterBoxView component to replace GravityView
  - [x] 5.1 Implement ClusterBoxView.js component skeleton
    - Create functional component with SVG container
    - Add data fetching from /graph endpoint
    - Add polling interval (3 seconds) for updates
    - Add loading state
    - Pass through onActivityUpdate and onFileSelect props
    - _Requirements: 2.1_
  
  - [x] 5.2 Implement cluster box layout algorithm
    - Calculate grid layout based on number of clusters (cols = ceil(sqrt(N)))
    - Calculate box dimensions (width, height) based on viewport and grid
    - Position each cluster box at grid cell coordinates
    - Add padding between boxes (20px)
    - Store cluster box positions and dimensions in state
    - _Requirements: 2.1, 2.2_
  
  - [x] 5.3 Render cluster boxes as SVG rectangles
    - Create SVG rect elements for each cluster
    - Apply border styling (stroke, stroke-width)
    - Apply background fill with semi-transparent color
    - Use d3.schemeCategory10 for cluster colors
    - _Requirements: 2.1, 2.2_
  
  - [x] 5.4 Render cluster names and file counts
    - Add SVG text element at top of each cluster box for name
    - Add SVG circle + text badge for file count in top-right corner
    - Truncate long cluster names with ellipsis
    - Style text elements (font-size, font-weight, fill)
    - _Requirements: 2.3, 4.1, 4.3_
  
  - [ ]* 5.5 Write property test for cluster name display
    - **Property 3: Cluster names are displayed**
    - **Validates: Requirements 2.3, 4.1**
    - Generate random cluster data, verify all cluster names are rendered
  
  - [ ]* 5.6 Write property test for file count display
    - **Property 6: File count is displayed per cluster**
    - **Validates: Requirements 4.3**
    - Generate clusters with varying file counts, verify counts are displayed

- [x] 6. Implement file positioning within cluster boxes
  - [x] 6.1 Create file positioning algorithm
    - For each cluster, calculate available space (box dimensions minus padding)
    - Use grid layout for files: calculate cols based on sqrt(fileCount)
    - Calculate file positions within cluster boundaries
    - Add spacing between files (10px)
    - Ensure all file positions are within cluster bounds
    - _Requirements: 2.4, 4.2_
  
  - [x] 6.2 Render file nodes within clusters
    - Create SVG circle elements for each file
    - Position files at calculated coordinates (relative to cluster box)
    - Add file icon emoji (📄 for PDF, 📝 for others)
    - Add file label text below each file node
    - Apply cluster color to file node borders
    - _Requirements: 2.4, 4.2_
  
  - [ ]* 6.3 Write property test for file containment
    - **Property 4: Files are contained within cluster boundaries**
    - **Validates: Requirements 2.4, 4.2**
    - Generate random file positions, verify all are within cluster bounds
  
  - [ ]* 6.4 Write property test for uncategorized files
    - **Property 5: Uncategorized files have a default cluster**
    - **Validates: Requirements 2.5**
    - Generate files with and without clusters, verify uncategorized files appear in "Uncategorized" box

- [x] 7. Add file interaction handlers
  - [x] 7.1 Implement file click handler
    - Add onClick event to file node groups
    - Call onFileSelect prop with file data
    - Add hover effect (scale up file node on mouseenter)
    - Remove hover effect on mouseleave
    - _Requirements: 4.4_
  
  - [ ]* 7.2 Write property test for file click metadata
    - **Property 7: File click shows metadata**
    - **Validates: Requirements 4.4**
    - Generate random file nodes, simulate clicks, verify metadata panel appears

- [x] 8. Integrate FileUpload and ClusterBoxView into App.js
  - [x] 8.1 Update App.js to use new components
    - Import FileUpload and ClusterBoxView components
    - Replace GravityView with ClusterBoxView
    - Add FileUpload component to header section
    - Implement handleUploadSuccess to show activity feed message
    - Implement handleUploadError to show error message
    - Remove legend-related code (no longer needed)
    - _Requirements: 1.1, 2.1, 3.1_
  
  - [x] 8.2 Update App.css for new layout
    - Add styles for FileUpload button
    - Remove legend styles
    - Adjust layout for cleaner appearance
    - Ensure metadata panel still works with new visualization
    - _Requirements: 3.1, 3.2_

- [ ] 9. Checkpoint - Ensure frontend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Test bidirectional file management
  - [ ]* 10.1 Write integration test for UI upload flow
    - Test complete flow: click upload → select file → verify in visualization
    - Test upload feedback appears
    - Test file appears in correct cluster
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 10.2 Write integration test for file system monitoring
    - Test dropping file in sefs_root folder
    - Verify file is detected and processed
    - Verify UI updates via WebSocket
    - _Requirements: 5.2, 5.3, 5.4_
  
  - [ ]* 10.3 Write property test for bidirectional updates
    - **Property 8: Bidirectional file addition triggers updates**
    - **Validates: Requirements 5.2, 5.3, 5.4**
    - Generate random files, add via both methods, verify WebSocket broadcasts updates

- [ ] 11. Final checkpoint - End-to-end testing
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The visualization redesign (tasks 5-7) is the most complex part
- File upload (tasks 1, 4) should be implemented first for quick wins
- Integration tests (task 10) verify the complete bidirectional flow
