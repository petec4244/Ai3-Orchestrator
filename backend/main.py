"""
AI Orchestrator - Main Entry Point
Coordinates multiple AI models based on task analysis
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv

from task_analyzer import TaskAnalyzer
from api_clients import GrokClient, ClaudeClient, ChatGPTClient
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AIOrchestrator:
    """Main orchestrator class that manages AI model interactions"""

    def __init__(self):
        load_dotenv()
        self.config = Config()

        # Initialize AI clients
        self.grok_client = GrokClient(os.getenv('XAI_API_KEY'))
        self.claude_client = ClaudeClient(os.getenv('ANTHROPIC_API_KEY'))
        self.chatgpt_client = ChatGPTClient(os.getenv('OPENAI_API_KEY'))

        # Initialize task analyzer
        self.task_analyzer = TaskAnalyzer()

        logger.info("AI Orchestrator initialized successfully")

    def process_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Main method to process a user prompt

        Args:
            user_prompt: The user's input prompt

        Returns:
            Dictionary containing task breakdown, responses, and final output
        """
        logger.info(f"Processing prompt: {user_prompt[:100]}...")

        try:
            # Step 1: Analyze and break down the prompt
            tasks = self.task_analyzer.analyze(user_prompt)
            logger.info(f"Identified {len(tasks)} tasks: {[t['type'] for t in tasks]}")

            # Step 2: Process each task with appropriate model(s)
            task_responses = []
            for task in tasks:
                response = self._process_task(task)
                task_responses.append({
                    'task': task,
                    'response': response
                })

            # Step 3: Combine responses into final output
            final_output = self._combine_responses(user_prompt, task_responses)

            return {
                'success': True,
                'original_prompt': user_prompt,
                'tasks': tasks,
                'task_responses': task_responses,
                'final_output': final_output
            }

        except Exception as e:
            logger.error(f"Error processing prompt: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'original_prompt': user_prompt
            }

    def _process_task(self, task: Dict[str, Any]) -> str:
        """
        Process a single task based on its type

        Args:
            task: Task dictionary with type and content

        Returns:
            Response string from the appropriate AI model(s)
        """
        task_type = task['type']
        task_content = task['content']

        # Get routing rule from config
        routing_rule = self.config.get_routing_rule(task_type)
        logger.info(f"Processing {task_type} task with rule: {routing_rule}")

        try:
            if routing_rule == "claude":
                logger.info("Using Claude directly (best for coding, writing, automation)")
                response = self.claude_client.complete(task_content)

            elif routing_rule == "chatgpt":
                logger.info("Using ChatGPT directly (best for multimodal, data analysis, integration)")
                response = self.chatgpt_client.complete(task_content)

            elif routing_rule == "grok":
                logger.info("Using Grok directly (best for math, real-time social, creative insights)")
                response = self.grok_client.complete(task_content)

            elif routing_rule == "grok_refine_then_claude":
                # Legacy routing: Use Grok to refine the prompt, then Claude executes
                logger.info("Step 1: Refining prompt with Grok")
                refined_prompt = self.grok_client.refine_prompt(task_content)
                logger.info(f"Grok refined prompt: {refined_prompt[:100]}...")

                logger.info("Step 2: Generating response with Claude")
                response = self.claude_client.complete(refined_prompt)

            else:
                # Default to ChatGPT as most versatile
                logger.warning(f"Unknown routing rule: {routing_rule}, defaulting to ChatGPT")
                response = self.chatgpt_client.complete(task_content)

            return response

        except Exception as e:
            logger.error(f"Error processing task {task_type}: {str(e)}")
            return f"[Error processing task: {str(e)}]"

    def _combine_responses(self, original_prompt: str,
                          task_responses: List[Dict]) -> str:
        """
        Combine multiple task responses into a cohesive final output

        Args:
            original_prompt: The original user prompt
            task_responses: List of task response dictionaries

        Returns:
            Combined final output string
        """
        if len(task_responses) == 1:
            # Single task, return response directly
            return task_responses[0]['response']

        # Multiple tasks, combine intelligently
        combined = f"# Response to: {original_prompt}\n\n"

        for i, task_resp in enumerate(task_responses, 1):
            task_type = task_resp['task']['type']
            response = task_resp['response']

            combined += f"## Part {i}: {task_type.replace('_', ' ').title()}\n\n"
            combined += f"{response}\n\n"
            combined += "---\n\n"

        return combined.strip()


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python main.py '<your prompt>'")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])

    orchestrator = AIOrchestrator()
    result = orchestrator.process_prompt(prompt)

    if result['success']:
        print("\n" + "="*80)
        print("FINAL OUTPUT")
        print("="*80 + "\n")
        print(result['final_output'])
    else:
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
