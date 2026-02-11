# File Path Tracking Bug Fix - Requirements

## Problem Statement
When files are moved to semantic folders by the SEFS system, the state manager continues to store the original file paths. This causes the "Open File" functionality to fail with a 404 error because the backend tries to open files at their old locations instead of their current locations.

## Current Behavior
1. User clicks "Open File" on a file in the UI
2. Frontend sends request to `/open-file/{original_path}`
3. Backend receives the original path (e.g., `C:\SEFS\sefs-project\sefs_root\travel_guide_3.txt`)
4. File doesn't exist at that location (it's been moved to `Architecture_Beach_Best` folder)
5. Backend returns 404 error

## Expected Behavior
1. User clicks "Open File" on a file in the UI
2. Frontend sends request with file identifier
3. Backend resolves the current physical location of the file
4. Backend opens the file at its current location
5. File opens successfully

## User Stories

### 1.1 As a user, I want to open files that have been moved to semantic folders
**Acceptance Criteria:**
- When I click "Open File" on any file in the UI, it should open successfully
- The system should track the current physical location of files after they are moved
- The open file functionality should work regardless of how many times a file has been reorganized

### 1.2 As a developer, I want the state to reflect current file locations
**Acceptance Criteria:**
- The state manager should store both the original file path (as identifier) and current physical path
- When files are moved, the state should be updated with the new physical location
- The API should use the current physical path when opening files

### 1.3 As a user, I want file operations to be reliable after reorganization
**Acceptance Criteria:**
- All file operations (open, read, move) should work with files in semantic folders
- The system should handle files that have been moved multiple times
- Error messages should be clear when a file truly doesn't exist vs. path tracking issues

## Technical Context
- Backend: Python FastAPI
- State storage: JSON file (`.sefs_state.json`)
- File operations: `os_manager.py` handles file moves
- State management: `state_manager.py` tracks file metadata
- API endpoint: `/open-file/{file_path}` in `main.py`

## Constraints
- Must maintain backward compatibility with existing state files
- Should not break existing file tracking functionality
- Must handle Windows file paths correctly
