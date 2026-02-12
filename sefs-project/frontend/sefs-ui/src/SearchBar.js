import React, { useState } from 'react';

const SearchBar = ({ onFileSelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async (searchQuery) => {
    setQuery(searchQuery);
    
    if (searchQuery.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setResults(data.results || []);
      setShowResults(true);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleResultClick = (result) => {
    if (onFileSelect) {
      onFileSelect({
        id: result.path,
        label: result.name,
        clusterName: result.cluster,
        size: result.size,
        path: result.path
      });
    }
    setShowResults(false);
    setQuery('');
  };

  return (
    <div className="search-bar">
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          type="text"
          className="search-input"
          placeholder="Search files by name or content..."
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => query.length >= 2 && setShowResults(true)}
        />
        {isSearching && <span className="search-loading">⏳</span>}
      </div>

      {showResults && results.length > 0 && (
        <div className="search-results">
          {results.map((result, index) => (
            <div
              key={index}
              className="search-result-item"
              onClick={() => handleResultClick(result)}
            >
              <div className="search-result-name">
                📄 {result.name}
                <span className="search-result-badge">{result.matchType}</span>
              </div>
              <div className="search-result-meta">
                📁 {result.cluster} • {result.size}
              </div>
              {result.snippet && (
                <div className="search-result-snippet">{result.snippet}</div>
              )}
            </div>
          ))}
        </div>
      )}

      {showResults && results.length === 0 && query.length >= 2 && !isSearching && (
        <div className="search-results">
          <div className="search-no-results">No files found</div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
