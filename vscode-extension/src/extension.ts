// VS Code Extension Entry Point
import * as vscode from 'vscode';
import * as path from 'path';
import { spawn } from 'child_process';

let outputChannel: vscode.OutputChannel;
let currentPanel: vscode.WebviewPanel | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('AI Orchestrator extension activated');

    outputChannel = vscode.window.createOutputChannel('AI Orchestrator');

    // Register main command
    let disposable = vscode.commands.registerCommand(
        'ai-orchestrator.processPrompt',
        async () => {
            await processPrompt(context);
        }
    );

    // Register configuration command
    let configDisposable = vscode.commands.registerCommand(
        'ai-orchestrator.openConfig',
        () => {
            openConfigFile();
        }
    );

    context.subscriptions.push(disposable, configDisposable);

    outputChannel.appendLine('AI Orchestrator ready!');
}

async function processPrompt(context: vscode.ExtensionContext) {
    // Get user input
    const prompt = await vscode.window.showInputBox({
        prompt: 'Enter your prompt for AI Orchestrator',
        placeHolder: 'e.g., Write a Python function to parse CSV files, then summarize the data',
        ignoreFocusOut: true
    });

    if (!prompt) {
        return;
    }

    // Create or show webview panel
    if (currentPanel) {
        currentPanel.reveal(vscode.ViewColumn.One);
    } else {
        currentPanel = vscode.window.createWebviewPanel(
            'aiOrchestratorResults',
            'AI Orchestrator Results',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        currentPanel.onDidDispose(() => {
            currentPanel = undefined;
        });
    }

    // Show loading state
    currentPanel.webview.html = getLoadingHtml();

    // Execute Python backend
    try {
        const result = await executePythonBackend(prompt);
        currentPanel.webview.html = getResultsHtml(result);
    } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        currentPanel.webview.html = getErrorHtml(errorMsg);
        vscode.window.showErrorMessage(`AI Orchestrator Error: ${errorMsg}`);
    }
}

function executePythonBackend(prompt: string): Promise<any> {
    return new Promise((resolve, reject) => {
        outputChannel.appendLine(`Processing prompt: ${prompt}`);

        // Find Python executable
        const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';

        // Path to backend (assumes backend is in workspace or extension folder)
        const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
        const backendPath = workspacePath
            ? path.join(workspacePath, 'backend', 'main.py')
            : path.join(__dirname, '..', '..', 'backend', 'main.py');

        outputChannel.appendLine(`Using backend at: ${backendPath}`);

        // Spawn Python process
        const pythonProcess = spawn(pythonCommand, [backendPath, prompt]);

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString();
            stdout += output;
            outputChannel.append(output);
        });

        pythonProcess.stderr.on('data', (data) => {
            const output = data.toString();
            stderr += output;
            outputChannel.append(output);
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    // Try to parse JSON output
                    const jsonMatch = stdout.match(/\{[\s\S]*\}/);
                    if (jsonMatch) {
                        resolve(JSON.parse(jsonMatch[0]));
                    } else {
                        resolve({ success: true, final_output: stdout });
                    }
                } catch (e) {
                    resolve({ success: true, final_output: stdout });
                }
            } else {
                reject(new Error(`Python process exited with code ${code}\n${stderr}`));
            }
        });

        pythonProcess.on('error', (error) => {
            reject(new Error(`Failed to start Python process: ${error.message}`));
        });

        // Set timeout
        setTimeout(() => {
            pythonProcess.kill();
            reject(new Error('Request timed out after 120 seconds'));
        }, 120000);
    });
}

function openConfigFile() {
    const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspacePath) {
        vscode.window.showErrorMessage('Please open a workspace first');
        return;
    }

    const configPath = path.join(workspacePath, 'backend', 'task_rules.json');
    vscode.workspace.openTextDocument(configPath).then(doc => {
        vscode.window.showTextDocument(doc);
    }, error => {
        vscode.window.showErrorMessage(`Could not open config file: ${error.message}`);
    });
}

function getLoadingHtml(): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                }
                .loader {
                    border: 4px solid var(--vscode-editor-background);
                    border-top: 4px solid var(--vscode-button-background);
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .status { text-align: center; margin-top: 20px; }
            </style>
        </head>
        <body>
            <h1>AI Orchestrator</h1>
            <div class="loader"></div>
            <div class="status">Processing your prompt across multiple AI models...</div>
        </body>
        </html>
    `;
}

function getResultsHtml(result: any): string {
    const tasks = result.tasks || [];
    const finalOutput = result.final_output || 'No output generated';

    const tasksHtml = tasks.map((task: any, i: number) => `
        <div class="task">
            <h3>Task ${i + 1}: ${task.type.replace('_', ' ')}</h3>
            <p><strong>Content:</strong> ${escapeHtml(task.content)}</p>
            <p><strong>Confidence:</strong> ${task.confidence}</p>
        </div>
    `).join('');

    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                    line-height: 1.6;
                }
                h1 { color: var(--vscode-textLink-foreground); }
                .section {
                    margin: 20px 0;
                    padding: 15px;
                    background: var(--vscode-editor-background);
                    border-left: 3px solid var(--vscode-button-background);
                }
                .task {
                    margin: 10px 0;
                    padding: 10px;
                    background: var(--vscode-input-background);
                    border-radius: 4px;
                }
                pre {
                    background: var(--vscode-textCodeBlock-background);
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                }
                code {
                    font-family: var(--vscode-editor-font-family);
                }
            </style>
        </head>
        <body>
            <h1>AI Orchestrator Results</h1>

            <div class="section">
                <h2>Task Breakdown</h2>
                ${tasksHtml}
            </div>

            <div class="section">
                <h2>Final Output</h2>
                <pre><code>${escapeHtml(finalOutput)}</code></pre>
            </div>
        </body>
        </html>
    `;
}

function getErrorHtml(error: string): string {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                }
                .error {
                    background: var(--vscode-inputValidation-errorBackground);
                    border: 1px solid var(--vscode-inputValidation-errorBorder);
                    padding: 15px;
                    border-radius: 4px;
                    margin: 20px 0;
                }
                h1 { color: var(--vscode-errorForeground); }
            </style>
        </head>
        <body>
            <h1>Error</h1>
            <div class="error">
                <p><strong>An error occurred:</strong></p>
                <pre>${escapeHtml(error)}</pre>
            </div>
        </body>
        </html>
    `;
}

function escapeHtml(text: string): string {
    const map: { [key: string]: string } = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

export function deactivate() {}
