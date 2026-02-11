# File Path Tracking Bug Fix - Design Document

## Overview

This design addresses a critical bug in the SEFS (Semantic Entropy File System) where files that have been moved to semantic folders cannot be opened because the system tracks original paths instead of current physical locations. The solution introduces a dual-path tracking system that maintains both the original file identifier and the current physical location.

## Problem Analysis

### Root Cause
The current implementation has a fundamental flaw in how it tracks files:

1. **State Manager** stores file paths as keys in the `files` dictionary
2. **OS Manager** physically moves files to semantic folders
3. **State Manager** is never updated with the new physical locations
4. **Open File API** receives the original path and tries to open a file that no longer exists there

### Current Data Flow
```
User clicks "Open File" 
  → Frontend sends original path (e.g., "C:\SEFS\sefs_root\travel_guide_3.txt")
  → Backend /open-file endpoint receives original path
  → os.startfile() tries to open file at original location
  → File doesn't exist (it's in "Architecture_Beach_Best" folder)
  → 404 Error
```

### Required Data Flow
```
User clicks "Open File"
  → Frontend sends file identifier
  → Backend resolves current physical location from state
  → Backend opens file at current location
  → File opens successfully
```

## Architecture

### Dual-Path Tracking System

The solution introduces a clear separation between:
- **File Identifier**: Stable identifier for a file (original path or unique ID)
- **Physical Path**: Current location of the file on disk

### Component Changes

#### 1. State Manager Enhancement
- Modify state structure to track both original and current paths
- Add path resolution method
- Maintain backward compatibility with existing state files

#### 2. OS Manager Enhancement
- Return new file paths after move operations
- Provide callback mechanism for path updates

#### 3. API Endpoint Enhancement
- Modify `/open-file` endpoint to resolve current path before opening
- Add proper error handling for missing files

#### 4. Coordinator Enhancement
- Update state manager when files are moved
- Ensure state consistency after reorganization

## Components and Interfaces

### 1. State Manager

#### New State Structure
```python
{
  'files': {
    'original_path': {
      'cluster': cluster_id,
      'preview': content_preview,
      'updated': timestamp,
      'current_path': physical_path  # NEW FIELD
    }
  },
  'clusters': {...},
  'last_updated': timestamp
}
```

#### New Methods
```python
def update_file_location(self, original_path: str, new_path: str) -> None:
    """Update the physical location of a file
    
    Args:
        original_path: Original file identifier
        new_path: New physical location
    """
    
def resolve_current_path(self, file_identifier: str) -> Optional[str]:
    """Resolve the current physical path for a file
    
    Args:
        file_identifier: Original path or file identifier
        
    Returns:
        Current physical path or None if not found
    """
    
def migrate_legacy_state(self) -> None:
    """Migrate old state format to new format with current_path field"""
```

### 2. OS Manager

#### Modified Methods
```python
def move_file(self, file_path: str, cluster_id: int) -> Optional[str]:
    """Move file to cluster folder
    
    Returns:
        New file path if successful, None otherwise
    """
    # Already returns new path - no changes needed
    
def sync_clusters(
    self, 
    cluster_assignments: Dict[str, int], 
    cluster_names: Dict[int, str]
) -> Dict[str, str]:
    """Synchronize OS folders with cluster assignments
    
    Returns:
        Dictionary mapping original_path -> new_path for all moved files
    """
    # Already returns moved_files dict - no changes needed
```

### 3. Coordinator

#### Modified Methods
```python
def _reorganize(self) -> None:
    """Reorganize files based on clustering
    
    Now updates state manager with new file locations
    """
    # After sync_clusters, update state with new paths
    
def _process_file(self, file_path: str) -> None:
    """Process a single file
    
    Ensures state tracks the file's current location
    """
```

### 4. API Endpoint

#### Modified Endpoint
```python
@app.get("/open-file/{file_path:path}")
def open_file(file_path: str):
    """Open a file in the default system application
    
    Now resolves current physical location before opening
    """
    # 1. Resolve current path from state
    # 2. Verify file exists at current location
    # 3. Open file
    # 4. Return appropriate error if not found
```

## Data Models

### File State Entry
```python
{
  "cluster": int,              # Cluster ID (-1 for uncategorized)
  "preview": str,              # Content preview
  "updated": str,              # ISO timestamp
  "current_path": str          # Current physical location (NEW)
}
```

### Path Resolution Logic
```python
# Priority order for resolving file location:
1. Check state['files'][identifier]['current_path']
2. If not present, check if identifier itself exists as file
3. If not found, return None
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing the acceptance criteria, several properties are redundant:

- **1.3 and 3.2** both test multiple moves - this is subsumed by Property 1 (file opening after moves)
- **1.2 and 2.2** both test state updates after moves - these can be combined into one property
- **2.1** (state structure) is a precondition for other properties, not a separate runtime property

**Consolidated Properties:**
1. File opening works after any number of moves (covers 1.1, 1.3, 3.2)
2. State tracking updates correctly after moves (covers 1.2, 2.2)
3. Path resolution uses current location (covers 2.3)
4. Files in semantic folders can be moved again (covers 3.1)

### Correctness Properties

**Property 1: File opening after relocation**
*For any* file that has been moved to a semantic folder (one or more times), attempting to open that file should succeed by resolving to its current physical location.
**Validates: Requirements 1.1, 1.3, 3.2**

**Property 2: State consistency after file moves**
*For any* file that is moved by the OS manager, the state manager should be updated such that the file's `current_path` field reflects the new physical location.
**Validates: Requirements 1.2, 2.2**

**Property 3: Path resolution correctness**
*For any* file identifier in the system, the path resolution function should return the file's current physical path if the file exists, or None if it doesn't exist.
**Validates: Requirements 2.3**

**Property 4: Semantic folder file operations**
*For any* file already located in a semantic folder, moving it to a different semantic folder should succeed and update the state correctly.
**Validates: Requirements 3.1**

**Property 5: State structure invariant**
*For any* file entry in the state after a move operation, it must contain both an original identifier (the dictionary key) and a `current_path` field.
**Validates: Requirements 2.1**

## Error Handling

### Error Scenarios

#### 1. File Not Found
**Scenario**: File identifier exists in state but physical file is missing
**Handling**: 
- Check if file exists at `current_path`
- If not, check if file exists at original identifier path
- Return 404 with clear message: "File not found at tracked location: {path}"

#### 2. State Corruption
**Scenario**: State file is corrupted or missing `current_path` field
**Handling**:
- Implement state migration on load
- If `current_path` is missing, use original identifier as fallback
- Log warning about legacy state format

#### 3. Move Operation Failure
**Scenario**: OS manager fails to move file
**Handling**:
- OS manager returns None on failure
- Coordinator should not update state if move fails
- Log error with details

#### 4. Path Resolution Failure
**Scenario**: Cannot resolve current path for file identifier
**Handling**:
- Return None from `resolve_current_path()`
- API endpoint returns 404 with message: "File not found: {identifier}"

### Error Response Format
```python
{
  "error": str,           # Error message
  "file_id": str,         # File identifier that failed
  "attempted_path": str,  # Path that was attempted (if applicable)
  "suggestion": str       # Helpful suggestion for user
}
```

## Testing Strategy

### Dual Testing Approach

This bug fix requires both unit tests and property-based tests to ensure correctness:

- **Unit tests**: Verify specific scenarios, edge cases, and error conditions
- **Property tests**: Verify universal properties across all file operations

### Unit Testing Focus

Unit tests should cover:
- Specific examples of file moves and opens
- State migration from legacy format
- Error conditions (missing files, corrupted state)
- API endpoint responses
- Edge cases (special characters in paths, long paths)

### Property-Based Testing

**Library**: Use `hypothesis` for Python property-based testing

**Configuration**: Each property test should run minimum 100 iterations

**Test Tagging**: Each test must reference its design property
- Format: `# Feature: file-path-tracking-bugfix, Property {number}: {property_text}`

**Property Test Implementation**:
1. **Property 1 Test**: Generate random files, move them 1-N times, verify open succeeds
2. **Property 2 Test**: Generate random files, move them, verify state has correct current_path
3. **Property 3 Test**: Generate random file identifiers, verify resolution returns correct path
4. **Property 4 Test**: Generate files in semantic folders, move them, verify success
5. **Property 5 Test**: Generate random file operations, verify state structure invariant

### Test Data Generation

For property-based tests, generate:
- Random file names (with various characters, lengths)
- Random folder names (semantic folder names)
- Random number of moves (1-10)
- Random cluster assignments

### Integration Testing

Integration tests should verify:
- End-to-end flow: add file → reorganize → open file
- Multiple reorganizations don't break tracking
- State persistence across system restarts
- Frontend-backend integration for open file

## Implementation Notes

### Backward Compatibility

The solution must handle existing state files that don't have the `current_path` field:

```python
def migrate_legacy_state(self):
    """Migrate old state format to new format"""
    for file_path, file_data in self.state['files'].items():
        if 'current_path' not in file_data:
            # For legacy entries, check if file exists at original path
            if Path(file_path).exists():
                file_data['current_path'] = file_path
            else:
                # Try to find file in semantic folders
                file_name = Path(file_path).name
                found_path = self._search_for_file(file_name)
                file_data['current_path'] = found_path if found_path else file_path
```

### Path Normalization

All paths should be normalized to handle:
- Windows vs Unix path separators
- Relative vs absolute paths
- Path case sensitivity (Windows)

```python
def normalize_path(self, path: str) -> str:
    """Normalize path for consistent comparison"""
    return str(Path(path).resolve())
```

### Atomic State Updates

State updates should be atomic to prevent corruption:

```python
def update_file_location(self, original_path: str, new_path: str):
    """Update file location atomically"""
    # Update in-memory state
    if original_path in self.state['files']:
        self.state['files'][original_path]['current_path'] = new_path
        # Save to disk immediately
        self.save_state()
```

### Performance Considerations

- Path resolution should be O(1) lookup in state dictionary
- State file should be kept reasonably sized (limit history entries)
- File existence checks should be cached when possible

## Deployment Considerations

### Migration Strategy

1. **Phase 1**: Deploy code with backward-compatible state reading
2. **Phase 2**: Run migration script to update existing state files
3. **Phase 3**: Monitor logs for any path resolution failures

### Rollback Plan

If issues arise:
1. State file format is backward compatible (old code can read new format)
2. `current_path` field is optional - old code ignores it
3. Can rollback code without data migration

### Monitoring

Add logging for:
- Path resolution failures
- State migration events
- File open failures with path details
- Move operations and state updates

## Security Considerations

### Path Traversal Prevention

The open file endpoint must validate paths:

```python
def open_file(file_path: str):
    # Resolve current path
    current_path = coordinator.state_manager.resolve_current_path(file_path)
    
    if not current_path:
        return JSONResponse(status_code=404, content={"error": "File not found"})
    
    # Security check - ensure file is within sefs_root
    full_path = Path(current_path).resolve()
    root_path = Path(ROOT_DIR).resolve()
    
    if not str(full_path).startswith(str(root_path)):
        return JSONResponse(
            status_code=403, 
            content={"error": "Access denied: file outside root directory"}
        )
    
    # Verify file exists
    if not full_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    
    # Open file...
```

### Input Validation

- Validate file identifiers are strings
- Sanitize paths before file operations
- Limit path length to prevent buffer issues

## Future Enhancements

### Potential Improvements

1. **File UUID System**: Replace path-based identifiers with UUIDs for more robust tracking
2. **Path History**: Track all historical locations of a file
3. **Conflict Resolution**: Better handling of duplicate file names
4. **Symbolic Links**: Support for symlinks in addition to physical moves
5. **Batch Operations**: Optimize state updates for bulk file moves

### API Evolution

Consider adding:
- `GET /file/{file_id}/history` - Get move history for a file
- `POST /file/{file_id}/restore` - Restore file to original location
- `GET /files/orphaned` - Find files with broken path tracking
