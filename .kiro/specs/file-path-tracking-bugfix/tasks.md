# Implementation Plan: File Path Tracking Bug Fix

## Overview

This implementation plan addresses the bug where files moved to semantic folders cannot be opened because the system tracks original paths instead of current physical locations. The solution introduces dual-path tracking in the state manager and updates all components to maintain path consistency.

## Tasks

- [ ] 1. Enhance State Manager with dual-path tracking
  - [ ] 1.1 Add `current_path` field to file state structure
    - Modify `update_file()` method to accept and store `current_path`
    - Ensure new field is included when creating file entries
    - _Requirements: 2.1_
  
  - [ ] 1.2 Implement `update_file_location()` method
    - Create method to update a file's current physical location
    - Ensure atomic state updates (update memory + save to disk)
    - Add path normalization for consistent comparison
    - _Requirements: 1.2, 2.2_
  
  - [ ] 1.3 Implement `resolve_current_path()` method
    - Create method to resolve file identifier to current physical path
    - Return `current_path` if present, fallback to identifier, return None if not found
    - Add logging for path resolution attempts
    - _Requirements: 2.3_
  
  - [ ] 1.4 Implement legacy state migration
    - Create `migrate_legacy_state()` method to handle old state format
    - Check for missing `current_path` fields and populate them
    - Search semantic folders for moved files if needed
    - Call migration automatically on state load
    - _Requirements: 2.1_
  
  - [ ]* 1.5 Write property test for state consistency after moves
    - **Property 2: State consistency after file moves**
    - **Validates: Requirements 1.2, 2.2**
  
  - [ ]* 1.6 Write property test for path resolution correctness
    - **Property 3: Path resolution correctness**
    - **Validates: Requirements 2.3**
  
  - [ ]* 1.7 Write unit tests for state manager enhancements
    - Test `update_file_location()` with various paths
    - Test `resolve_current_path()` with existing and missing files
    - Test legacy state migration with old format
    - Test path normalization edge cases
    - _Requirements: 1.2, 2.1, 2.3_

- [ ] 2. Update Coordinator to maintain path consistency
  - [ ] 2.1 Modify `_reorganize()` to update file locations in state
    - After `sync_clusters()`, iterate through `moved_files` dictionary
    - Call `state_manager.update_file_location()` for each moved file
    - Ensure state is updated before adding history snapshot
    - _Requirements: 1.2, 2.2_
  
  - [ ] 2.2 Modify `_process_file()` to initialize current_path
    - When adding new files, set `current_path` to the file's initial location
    - Update `state_manager.update_file()` calls to include current_path
    - _Requirements: 2.1_
  
  - [ ]* 2.3 Write property test for semantic folder file operations
    - **Property 4: Semantic folder file operations**
    - **Validates: Requirements 3.1**
  
  - [ ]* 2.4 Write unit tests for coordinator path tracking
    - Test that reorganization updates state with new paths
    - Test that new files are initialized with current_path
    - Test multiple reorganizations maintain correct paths
    - _Requirements: 1.2, 2.2, 3.1_

- [ ] 3. Checkpoint - Ensure state tracking tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Update API endpoint to resolve current paths
  - [ ] 4.1 Modify `/open-file` endpoint to use path resolution
    - Replace direct path usage with `state_manager.resolve_current_path()`
    - Add validation that resolved path is within sefs_root (security)
    - Verify file exists at resolved location before opening
    - Update error responses with clear messages
    - _Requirements: 1.1, 2.3_
  
  - [ ] 4.2 Enhance error handling in `/open-file` endpoint
    - Return 404 with "File not found" when resolution returns None
    - Return 403 with "Access denied" for paths outside root
    - Return 500 with details for other failures
    - Include file identifier in error responses
    - _Requirements: 3.3_
  
  - [ ]* 4.3 Write property test for file opening after relocation
    - **Property 1: File opening after relocation**
    - **Validates: Requirements 1.1, 1.3, 3.2**
  
  - [ ]* 4.4 Write unit tests for API endpoint
    - Test opening file at original location
    - Test opening file after one move
    - Test opening file after multiple moves
    - Test 404 error for non-existent files
    - Test 403 error for paths outside root
    - Test error messages are clear and helpful
    - _Requirements: 1.1, 1.3, 3.3_

- [ ] 5. Add path normalization utilities
  - [ ] 5.1 Implement path normalization helper
    - Create `normalize_path()` method in state manager
    - Handle Windows vs Unix path separators
    - Convert to absolute paths using Path.resolve()
    - Use normalized paths for all comparisons
    - _Requirements: 2.1, 2.3_
  
  - [ ]* 5.2 Write unit tests for path normalization
    - Test Windows paths with backslashes
    - Test Unix paths with forward slashes
    - Test relative paths conversion to absolute
    - Test paths with special characters
    - _Requirements: 2.1_

- [ ] 6. Integration and end-to-end testing
  - [ ]* 6.1 Write integration test for complete workflow
    - Test: add file → reorganize → open file succeeds
    - Test: multiple reorganizations → open file succeeds
    - Test: system restart → state persists → open file succeeds
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2_
  
  - [ ]* 6.2 Write property test for state structure invariant
    - **Property 5: State structure invariant**
    - **Validates: Requirements 2.1**

- [ ] 7. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties across many generated inputs
- Unit tests validate specific examples and edge cases
- The implementation maintains backward compatibility with existing state files
- Path normalization ensures consistent behavior across Windows and Unix systems
