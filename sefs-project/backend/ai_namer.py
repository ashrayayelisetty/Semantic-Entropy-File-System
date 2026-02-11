"""AI-Powered Cluster Naming using CrewAI
Generates intelligent folder names based on cluster content"""

import os
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Check if environment variables are set
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini/gemini-1.5-flash")

# Only import CrewAI if API keys are available
AI_AVAILABLE = GEMINI_KEY or OPENAI_KEY

if AI_AVAILABLE:
    try:
        from crewai import Agent, Task, Crew, Process
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_openai import ChatOpenAI
        logger.info("CrewAI loaded successfully")
    except ImportError as e:
        logger.warning(f"CrewAI not available: {e}")
        AI_AVAILABLE = False


class AIClusterNamer:
    """AI-powered cluster naming using CrewAI"""
    
    def __init__(self):
        """Initialize AI namer"""
        self.ai_available = AI_AVAILABLE
        
        if self.ai_available:
            self._setup_llm()
            self._setup_agents()
        else:
            logger.info("AI naming not available - using fallback")
    
    def _setup_llm(self):
        """Setup the language model"""
        try:
            if GEMINI_KEY:
                # Use Gemini
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=GEMINI_KEY,
                    temperature=0.7
                )
                logger.info("Using Gemini AI for naming")
            elif OPENAI_KEY:
                # Use OpenAI
                model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
                self.llm = ChatOpenAI(
                    model=model,
                    api_key=OPENAI_KEY,
                    temperature=0.7
                )
                logger.info(f"Using OpenAI {model} for naming")
        except Exception as e:
            logger.error(f"Error setting up LLM: {e}")
            self.ai_available = False
    
    def _setup_agents(self):
        """Setup CrewAI agents"""
        try:
            # Semantic Namer Agent
            self.namer_agent = Agent(
                role='Semantic Folder Namer',
                goal='Generate concise, meaningful folder names based on file content',
                backstory="""You are an expert at analyzing document content and creating 
                descriptive, professional folder names. You understand semantic relationships 
                and can identify the core theme of a group of documents.""",
                llm=self.llm,
                verbose=False,
                allow_delegation=False
            )
            
            logger.info("CrewAI agents initialized")
        except Exception as e:
            logger.error(f"Error setting up agents: {e}")
            self.ai_available = False
    
    def generate_names(
        self, 
        cluster_assignments: Dict[str, int],
        file_contents: Dict[str, str]
    ) -> Dict[int, str]:
        """Generate AI-powered names for clusters
        
        Args:
            cluster_assignments: Dict mapping file paths to cluster IDs
            file_contents: Dict mapping file paths to content previews
            
        Returns:
            Dict mapping cluster IDs to generated names
        """
        if not self.ai_available:
            logger.info("AI not available, using fallback naming")
            return self._fallback_naming(cluster_assignments, file_contents)
        
        try:
            # Group files by cluster
            clusters = {}
            for file_path, cluster_id in cluster_assignments.items():
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(file_path)
            
            # Generate names for each cluster
            cluster_names = {}
            
            for cluster_id, files in clusters.items():
                if cluster_id == -1:
                    cluster_names[cluster_id] = "Uncategorized"
                    continue
                
                # Get content summaries
                summaries = []
                for file_path in files[:5]:  # Limit to 5 files per cluster
                    content = file_contents.get(file_path, "")
                    if content:
                        # Get first 200 chars as summary
                        summary = content[:200].replace("\n", " ")
                        filename = Path(file_path).stem
                        summaries.append(f"- {filename}: {summary}")
                
                if not summaries:
                    cluster_names[cluster_id] = f"Cluster_{cluster_id}"
                    continue
                
                # Create naming task
                summary_text = "\n".join(summaries)
                
                task = Task(
                    description=f"""Analyze these {len(files)} files and generate a concise, 
                    professional folder name (2-4 words, use underscores instead of spaces):
                    
                    {summary_text}
                    
                    Requirements:
                    - 2-4 words maximum
                    - Use underscores instead of spaces (e.g., Machine_Learning_Papers)
                    - Capitalize each word
                    - Be specific and descriptive
                    - Avoid generic terms like "Files" or "Documents"
                    - Return ONLY the folder name, nothing else
                    """,
                    agent=self.namer_agent,
                    expected_output="A concise folder name with underscores"
                )
                
                # Execute task
                crew = Crew(
                    agents=[self.namer_agent],
                    tasks=[task],
                    process=Process.sequential,
                    verbose=False
                )
                
                result = crew.kickoff()
                
                # Clean up the result
                name = str(result).strip()
                # Remove quotes if present
                name = name.strip('"\'')
                # Remove any extra text
                name = name.split('\n')[0].split('.')[0]
                # Ensure underscores
                name = name.replace(' ', '_')
                # Sanitize
                name = ''.join(c for c in name if c.isalnum() or c == '_')
                
                cluster_names[cluster_id] = name if name else f"Cluster_{cluster_id}"
                logger.info(f"Generated name for cluster {cluster_id}: {cluster_names[cluster_id]}")
            
            return cluster_names
            
        except Exception as e:
            logger.error(f"Error generating AI names: {e}")
            return self._fallback_naming(cluster_assignments, file_contents)
    
    def _fallback_naming(
        self,
        cluster_assignments: Dict[str, int],
        file_contents: Dict[str, str]
    ) -> Dict[int, str]:
        """Fallback to TF-IDF based naming"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from collections import Counter
        import re
        
        # Group files by cluster
        clusters = {}
        for file_path, cluster_id in cluster_assignments.items():
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(file_path)
        
        # Generate names
        cluster_names = {}
        for cluster_id, files in clusters.items():
            if cluster_id == -1:
                cluster_names[cluster_id] = "Uncategorized"
                continue
            
            # Get content for this cluster
            texts = []
            for file_path in files:
                content = file_contents.get(file_path, "")
                if content:
                    texts.append(content)
            
            # Try TF-IDF if we have content
            if texts and len(texts) > 0:
                try:
                    # Use TF-IDF to extract important keywords
                    vectorizer = TfidfVectorizer(
                        max_features=3,
                        stop_words='english',
                        ngram_range=(1, 1),
                        min_df=1
                    )
                    vectorizer.fit_transform(texts)
                    
                    # Get top keywords
                    keywords = vectorizer.get_feature_names_out()
                    
                    if len(keywords) > 0:
                        # Format as folder name
                        name = "_".join([k.capitalize() for k in keywords])
                        cluster_names[cluster_id] = name
                        logger.info(f"TF-IDF generated name for cluster {cluster_id}: {name}")
                        continue
                except Exception as e:
                    logger.warning(f"TF-IDF naming failed for cluster {cluster_id}: {e}")
            
            # Fallback to filename-based naming if TF-IDF fails
            words = []
            for file_path in files:
                name = Path(file_path).stem
                words.extend(re.findall(r'\w+', name.lower()))
            
            # Find most common words
            common_words = Counter(words).most_common(3)
            
            if common_words:
                name = "_".join([word for word, count in common_words])
                cluster_names[cluster_id] = name.capitalize()
            else:
                cluster_names[cluster_id] = f"Cluster_{cluster_id}"
        
        return cluster_names


# Singleton instance
_namer_instance = None

def get_ai_namer() -> AIClusterNamer:
    """Get or create AI namer instance"""
    global _namer_instance
    if _namer_instance is None:
        _namer_instance = AIClusterNamer()
    return _namer_instance
