"""
Task Analyzer - Breaks down prompts into categorized sub-tasks
"""

import re
from typing import List, Dict, Any


class TaskAnalyzer:
    """Analyzes user prompts and breaks them into categorized tasks"""

    # Keywords for different task types
    # Based on AI Comparison Summary - Claude excels at coding
    CODING_KEYWORDS = [
        'code', 'function', 'program', 'script', 'algorithm', 'debug',
        'implement', 'api', 'class', 'method', 'variable', 'python',
        'javascript', 'java', 'c++', 'programming', 'develop', 'build',
        'refactor', 'optimize', 'lint', 'test', 'unittest', 'swe-bench',
        'github', 'pull request', 'commit', 'repository', 'codebase',
        'software engineering', 'dev', 'developer', 'coding', 'compiler',
        'syntax', 'semantic', 'logic error', 'bug fix', 'code review',
        'autonomous coding', 'long-term task', 'production code',
        'typescript', 'rust', 'go', 'kotlin', 'swift', 'ruby', 'php',
        'sql', 'database', 'backend', 'frontend', 'full stack'
    ]

    # ChatGPT excels at summarization and versatile tasks
    SUMMARIZATION_KEYWORDS = [
        'summarize', 'summary', 'tldr', 'brief', 'overview', 'digest',
        'condense', 'shorten', 'recap', 'key points', 'main ideas',
        'abstract', 'executive summary', 'synopsis', 'outline', 'review',
        'distill', 'extract', 'highlights', 'takeaways', 'conclusion'
    ]

    # ChatGPT best for data analysis and multimodal
    DATA_ANALYSIS_KEYWORDS = [
        'analyze', 'data', 'statistics', 'chart', 'graph', 'metrics',
        'trends', 'insights', 'visualization', 'dataset', 'csv', 'excel',
        'spreadsheet', 'pandas', 'numpy', 'analysis', 'statistical',
        'correlation', 'regression', 'forecast', 'prediction', 'model',
        'dashboard', 'report', 'kpi', 'analytics', 'business intelligence'
    ]

    # Claude excels at creative writing and long-form content
    CREATIVE_KEYWORDS = [
        'write', 'story', 'poem', 'creative', 'imagine', 'fiction',
        'novel', 'character', 'plot', 'narrative', 'essay',
        'article', 'blog post', 'prose', 'dialogue', 'screenplay',
        'storytelling', 'author', 'composition', 'literary', 'creative writing',
        'long-form', 'detailed writing', 'nuanced', 'engaging narrative'
    ]

    # Grok excels at mathematical and STEM reasoning
    MATHEMATICAL_KEYWORDS = [
        'math', 'calculate', 'equation', 'formula', 'solve', 'proof',
        'theorem', 'calculus', 'algebra', 'geometry', 'trigonometry',
        'derivative', 'integral', 'matrix', 'vector', 'statistics',
        'probability', 'combinatorics', 'logic', 'mathematical reasoning',
        'aime', 'stem', 'physics', 'chemistry', 'biology', 'scientific',
        'research', 'hypothesis', 'experiment', 'quantum', 'computation',
        'number theory', 'discrete math', 'linear algebra', 'differential equations'
    ]

    # Grok excels at real-time data and social intelligence
    REALTIME_SOCIAL_KEYWORDS = [
        'twitter', 'x.com', 'social media', 'trending', 'viral', 'sentiment',
        'real-time', 'live', 'breaking news', 'current events', 'latest',
        'social listening', 'brand monitoring', 'market sentiment', 'opinion',
        'public reaction', 'social trends', 'influencer', 'engagement',
        'hashtag', 'tweet', 'post', 'community feedback', 'buzz'
    ]

    # ChatGPT excels at multimodal tasks (voice, video, image)
    MULTIMODAL_KEYWORDS = [
        'image', 'picture', 'photo', 'visual', 'video', 'audio', 'voice',
        'speech', 'generate image', 'create picture', 'draw', 'dalle',
        'illustration', 'diagram', 'infographic', 'multimodal', 'vision',
        'ocr', 'image analysis', 'face detection', 'object recognition',
        'transcribe', 'speech-to-text', 'text-to-speech', 'real-time voice'
    ]

    # Claude excels at long-form reasoning and document processing
    DOCUMENT_PROCESSING_KEYWORDS = [
        'document', 'pdf', 'long document', 'book', 'manuscript', 'thesis',
        'research paper', 'academic', 'technical documentation', 'manual',
        'guide', 'comprehensive analysis', 'deep dive', 'detailed review',
        'full-book summary', 'literature review', 'annotate', 'cite',
        'reference', 'bibliography', 'extract from document', '200k context'
    ]

    # Claude excels at professional and technical writing
    PROFESSIONAL_WRITING_KEYWORDS = [
        'technical writing', 'documentation', 'api docs', 'user guide',
        'specification', 'requirements', 'professional', 'business writing',
        'proposal', 'white paper', 'case study', 'report writing',
        'compliance', 'legal', 'contract', 'policy', 'procedure',
        'sop', 'standard operating procedure', 'technical specification'
    ]

    # Grok excels at creative insights and unconventional perspectives
    CREATIVE_INSIGHT_KEYWORDS = [
        'brainstorm', 'ideation', 'creative solution', 'think outside the box',
        'unique perspective', 'innovative', 'unconventional', 'original idea',
        'fresh approach', 'alternative viewpoint', 'creative problem solving',
        'lateral thinking', 'novel approach', 'inventive', 'imaginative solution'
    ]

    # Claude excels at desktop automation and UI tasks
    AUTOMATION_KEYWORDS = [
        'automate', 'automation', 'gui', 'ui automation', 'desktop',
        'click', 'navigate', 'process automation', 'workflow',
        'rpa', 'robotic process automation', 'macro', 'script automation',
        'selenium', 'puppeteer', 'computer use', 'control interface'
    ]

    # ChatGPT excels at integration and API tasks
    INTEGRATION_KEYWORDS = [
        'integrate', 'api integration', 'webhook', 'zapier', 'connector',
        'third-party', 'service integration', 'rest api', 'graphql',
        'microservice', 'plugin', 'extension', 'middleware', 'oauth',
        'authentication', 'authorization', 'endpoint', 'sdk'
    ]

    def __init__(self):
        pass

    def analyze(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Analyze a prompt and break it into tasks

        Args:
            prompt: User's input prompt

        Returns:
            List of task dictionaries with 'type' and 'content'
        """
        # Check if prompt contains multiple distinct requests
        tasks = self._split_multiple_requests(prompt)

        if len(tasks) > 1:
            # Multiple requests found, categorize each
            return [self._categorize_task(task) for task in tasks]
        else:
            # Single task, categorize it
            return [self._categorize_task(prompt)]

    def _split_multiple_requests(self, prompt: str) -> List[str]:
        """
        Split prompt into multiple requests if present

        Looks for patterns like:
        - "First... then..."
        - "1. ... 2. ..."
        - "Also, ..."
        """
        # Check for numbered lists
        numbered_pattern = r'\d+[\.\\)]\s+'
        if re.search(numbered_pattern, prompt):
            parts = re.split(numbered_pattern, prompt)
            return [p.strip() for p in parts if p.strip()]

        # Check for "and also", "then", "additionally" patterns
        split_patterns = [
            r'\bthen\b',
            r'\balso\b',
            r'\badditionally\b',
            r'\bafter that\b'
        ]

        for pattern in split_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                parts = re.split(pattern, prompt, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) > 1:
                    return [p.strip() for p in parts if p.strip()]

        # No clear split found, return as single task
        return [prompt]

    def _categorize_task(self, task: str) -> Dict[str, Any]:
        """
        Categorize a single task based on keywords

        Args:
            task: Task string to categorize

        Returns:
            Dictionary with 'type' and 'content' keys
        """
        task_lower = task.lower()

        # Count keyword matches for each category
        coding_score = sum(1 for kw in self.CODING_KEYWORDS if kw in task_lower)
        summary_score = sum(1 for kw in self.SUMMARIZATION_KEYWORDS if kw in task_lower)
        data_score = sum(1 for kw in self.DATA_ANALYSIS_KEYWORDS if kw in task_lower)
        creative_score = sum(1 for kw in self.CREATIVE_KEYWORDS if kw in task_lower)
        math_score = sum(1 for kw in self.MATHEMATICAL_KEYWORDS if kw in task_lower)
        realtime_score = sum(1 for kw in self.REALTIME_SOCIAL_KEYWORDS if kw in task_lower)
        multimodal_score = sum(1 for kw in self.MULTIMODAL_KEYWORDS if kw in task_lower)
        document_score = sum(1 for kw in self.DOCUMENT_PROCESSING_KEYWORDS if kw in task_lower)
        professional_score = sum(1 for kw in self.PROFESSIONAL_WRITING_KEYWORDS if kw in task_lower)
        insight_score = sum(1 for kw in self.CREATIVE_INSIGHT_KEYWORDS if kw in task_lower)
        automation_score = sum(1 for kw in self.AUTOMATION_KEYWORDS if kw in task_lower)
        integration_score = sum(1 for kw in self.INTEGRATION_KEYWORDS if kw in task_lower)

        # Determine task type based on highest score
        scores = {
            'coding': coding_score,
            'summarization': summary_score,
            'data_analysis': data_score,
            'creative_writing': creative_score,
            'mathematical_reasoning': math_score,
            'realtime_social': realtime_score,
            'multimodal': multimodal_score,
            'document_processing': document_score,
            'professional_writing': professional_score,
            'creative_insight': insight_score,
            'automation': automation_score,
            'integration': integration_score,
            'general': 0  # Default category
        }

        task_type = max(scores, key=scores.get)

        # If no strong match, classify as general
        if scores[task_type] == 0:
            task_type = 'general'

        return {
            'type': task_type,
            'content': task,
            'confidence': scores[task_type]
        }
