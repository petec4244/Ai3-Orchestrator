import React, { useState } from 'react';
import { FileText, Code, Settings, Book } from 'lucide-react';

const AIOrchestratorDocs = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const files = {
    overview: {
      title: 'Project Overview & Setup',
      icon: Book,
      content: `# AI3 Orchestrator System
## "One Source to Rule Them All"

### Project Structure
\`\`\`
ai3-orchestrator/
├── backend/
│   ├── main.py              # Main orchestrator logic
│   ├── task_analyzer.py     # Prompt analysis and task breakdown
│   ├── api_clients.py       # API client wrappers
│   ├── config.py            # Configuration management
│   ├── requirements.txt     # Python dependencies
│   └── task_rules.json      # Task routing configuration
├── vscode-extension/
│   ├── src/
│   │   └── extension.ts     # Extension entry point
│   ├── package.json         # Extension manifest
│   ├── tsconfig.json        # TypeScript config
│   └── .vscodeignore        # Files to exclude from package
├── docs/
│   └── AIOrchestratorDocs.tsx  # This documentation component
├── .env.example             # Example environment variables
└── README.md                # Setup instructions
\`\`\`

### Quick Setup Instructions

#### 1. Backend Setup
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
\`\`\`

#### 2. Environment Variables
Create a \`.env\` file in the backend directory:
\`\`\`
XAI_API_KEY=your_xai_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
\`\`\`

#### 3. VS Code Extension Setup
\`\`\`bash
cd vscode-extension
npm install
npm run compile
\`\`\`

#### 4. Install Extension
Press F5 in VS Code to launch Extension Development Host, or:
\`\`\`bash
npm run package
code --install-extension ai3-orchestrator-*.vsix
\`\`\`

### Key Features
- **Intelligent Task Breakdown**: Analyzes prompts to identify sub-tasks
- **Multi-Model Orchestration**: Routes tasks to optimal AI models
- **Grok → Claude Pipeline**: Specialized for coding tasks
- **Error Handling**: Automatic retries and fallback mechanisms
- **Configurable Rules**: JSON-based task routing
- **VS Code Integration**: Native interface with progress tracking`
    },
    pythonMain: {
      title: 'main.py',
      icon: Code,
      content: `See: backend/main.py

Main orchestrator class that coordinates multiple AI models based on task analysis.

Key methods:
- process_prompt(): Main entry point for processing user prompts
- _process_task(): Routes individual tasks to appropriate AI models
- _combine_responses(): Combines multiple task responses into final output

The orchestrator follows a three-step process:
1. Analyze and break down the prompt into tasks
2. Process each task with the appropriate model(s)
3. Combine responses into cohesive final output`
    },
    pythonAnalyzer: {
      title: 'task_analyzer.py',
      icon: Code,
      content: `See: backend/task_analyzer.py

Analyzes user prompts and categorizes them into task types:
- coding
- summarization
- data_analysis
- creative_writing
- general

The analyzer uses keyword matching and can split multi-part prompts
automatically based on patterns like "then", "also", numbered lists, etc.`
    },
    pythonClients: {
      title: 'api_clients.py',
      icon: Code,
      content: `See: backend/api_clients.py

API client wrappers for:
- GrokClient: xAI Grok API with prompt refinement capabilities
- ClaudeClient: Anthropic Claude API
- ChatGPTClient: OpenAI ChatGPT API

All clients include:
- Automatic retry logic with exponential backoff
- Error handling
- Configurable max tokens and temperature`
    },
    pythonConfig: {
      title: 'config.py & task_rules.json',
      icon: Settings,
      content: `See: backend/config.py and backend/task_rules.json

Configuration management system that handles:
- Task routing rules (which AI for which task type)
- System settings (retries, timeouts, logging)
- Dynamic rule updates

Default routing:
- coding → grok_refine_then_claude (Grok refines, Claude executes)
- summarization → chatgpt
- data_analysis → chatgpt
- creative_writing → grok
- general → grok`
    },
    extensionTS: {
      title: 'extension.ts',
      icon: Code,
      content: `See: vscode-extension/src/extension.ts

VS Code extension that provides:
- Command palette integration
- Input prompt dialog
- Webview results panel with task breakdown
- Python backend communication
- Progress tracking and error handling

Commands:
- AI3: Process Prompt (Ctrl+Shift+A / Cmd+Shift+A)
- AI3: Open Configuration`
    }
  };

  const TabButton = ({ id, title, icon: Icon }: { id: string; title: string; icon: any }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
        activeTab === id
          ? 'bg-blue-500 text-white'
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
      }`}
    >
      <Icon size={18} />
      <span>{title}</span>
    </button>
  );

  const currentFile = files[activeTab as keyof typeof files];
  const Icon = currentFile.icon;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AI3 Orchestrator System
          </h1>
          <p className="text-gray-600 text-lg">
            "One Source to Rule Them All" - Multi-AI Model Coordination
          </p>
        </header>

        <div className="flex flex-wrap gap-2 mb-6">
          <TabButton id="overview" title="Overview" icon={Book} />
          <TabButton id="pythonMain" title="main.py" icon={Code} />
          <TabButton id="pythonAnalyzer" title="task_analyzer.py" icon={Code} />
          <TabButton id="pythonClients" title="api_clients.py" icon={Code} />
          <TabButton id="pythonConfig" title="config.py" icon={Settings} />
          <TabButton id="extensionTS" title="extension.ts" icon={Code} />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center gap-3 mb-4 border-b pb-3">
            <Icon size={24} className="text-blue-500" />
            <h2 className="text-2xl font-semibold text-gray-800">
              {currentFile.title}
            </h2>
          </div>
          <div className="prose max-w-none">
            <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto whitespace-pre-wrap">
              {currentFile.content}
            </pre>
          </div>
        </div>

        <footer className="mt-8 text-center text-gray-500 text-sm">
          <p>AI3 Orchestrator v1.0.0 - Intelligent Multi-Model Task Distribution</p>
        </footer>
      </div>
    </div>
  );
};

export default AIOrchestratorDocs;
