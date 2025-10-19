# AI3 Orchestrator - Intelligent Routing Guide
## Based on Comprehensive AI Model Comparison Analysis

---

## 🎯 Overview

The AI3 Orchestrator now uses an evidence-based routing system that directs tasks to the optimal AI model based on documented strengths and benchmark performance. This guide is derived from a comprehensive analysis of Claude, ChatGPT, and Grok comparing their own capabilities.

---

## 📊 AI Model Selection Matrix

### **When to Use CLAUDE**

```
✅ PRIMARY USE CASES:
├─ Production-quality coding
├─ Software engineering tasks
├─ Long-form writing and narratives
├─ Professional/technical documentation
├─ Document processing (up to 200K tokens)
├─ Desktop automation and UI control
└─ Autonomous long-term tasks

📈 BENCHMARKS:
├─ SWE-bench: Industry leader
├─ Code consistency: 1 bad line per 999 good
├─ Context window: 200K tokens
└─ Autonomous task duration: 30+ hours

⚙️ ROUTING KEYWORDS:
code, function, algorithm, refactor, debug, github, pull request,
story, narrative, creative writing, long-form, document, pdf,
technical writing, api docs, specification, automation, gui,
desktop, process automation, workflow
```

**BEST FOR:**
- Building production-ready code with minimal errors
- Writing engaging, human-like narratives
- Processing lengthy documents or codebases
- Creating comprehensive technical documentation
- Automating desktop workflows and UI interactions

**AVOID FOR:**
- Mathematical proofs and STEM reasoning (use Grok)
- Image generation (use ChatGPT)
- Real-time social media analysis (use Grok)

---

### **When to Use CHATGPT**

```
✅ PRIMARY USE CASES:
├─ Multimodal tasks (image/voice/video)
├─ Data analysis and visualization
├─ Summarization and information extraction
├─ API integration and webhooks
├─ General versatile tasks
└─ Real-time streaming responses

📈 BENCHMARKS:
├─ SWE-bench: 54.6-74.9%
├─ Multimodal: Only native voice/video API
├─ Integration: 5000+ apps via Zapier
└─ Context window: 1M tokens (GPT-4.1+)

⚙️ ROUTING KEYWORDS:
summarize, tldr, overview, data, analyze, chart, visualization,
image, picture, generate image, dalle, voice, audio, video,
integrate, api integration, zapier, webhook, connector,
general, versatile, swiss army knife
```

**BEST FOR:**
- Creating images with DALL-E
- Analyzing data and creating visualizations
- Summarizing long articles or documents
- Building integrations with third-party services
- Real-time voice/video applications
- General-purpose versatile tasks

**AVOID FOR:**
- Creative writing (use Claude)
- Advanced mathematics (use Grok)
- Production code quality (use Claude)

---

### **When to Use GROK**

```
✅ PRIMARY USE CASES:
├─ Mathematical and STEM reasoning
├─ Real-time X/Twitter intelligence
├─ Creative insights and brainstorming
├─ Breaking news and current events
├─ Market sentiment analysis
└─ Cost-efficient high-volume tasks

📈 BENCHMARKS:
├─ AIME 2025: 93.3% (vs 33-36% for others)
├─ GPQA (STEM): 84.6-87.5%
├─ Real-time data: Native X integration
└─ Creativity: Unique perspectives and humor

⚙️ ROUTING KEYWORDS:
math, calculate, equation, solve, proof, theorem, calculus,
algebra, stem, physics, chemistry, twitter, social media,
trending, sentiment, real-time, breaking news, brainstorm,
creative solution, unique perspective, innovative
```

**BEST FOR:**
- Solving complex mathematical problems
- Analyzing social media trends and sentiment
- Generating creative, out-of-the-box ideas
- Tracking breaking news and real-time events
- STEM research and scientific reasoning
- Cost-sensitive high-volume operations

**AVOID FOR:**
- Image generation (poor quality)
- Professional business writing (use Claude)
- Multimodal tasks (use ChatGPT)

---

## 🗺️ Complete Routing Table

| Task Category | Routed To | Reasoning |
|---------------|-----------|-----------|
| **coding** | Claude | SWE-bench leader, highest code quality consistency |
| **creative_writing** | Claude | Best narrative flow, human-like prose, 200K context |
| **professional_writing** | Claude | Technical docs, specifications, business writing |
| **document_processing** | Claude | 200K context window, comprehensive analysis |
| **automation** | Claude | Desktop/UI automation, workflow control |
| **summarization** | ChatGPT | Efficient information extraction, balanced approach |
| **data_analysis** | ChatGPT | Visualization, statistics, business intelligence |
| **multimodal** | ChatGPT | Only native voice/video/image generation |
| **integration** | ChatGPT | Zapier ecosystem, API integrations, webhooks |
| **mathematical_reasoning** | Grok | 93.3% AIME (2.5x better than competitors) |
| **realtime_social** | Grok | Native X/Twitter access, sentiment analysis |
| **creative_insight** | Grok | Unique perspectives, brainstorming, innovation |
| **general** | ChatGPT | Most versatile "Swiss Army knife" |

---

## 🔬 Evidence-Based Decisions

### **Accuracy of AI Self-Assessments**

When the three AI models evaluated each other's capabilities:

```
ChatGPT Response: 8.5-9.5/10 accuracy
├─ Most evidence-based with extensive citations
├─ Distinguished verified benchmarks from claims
└─ Appropriate skepticism of unverified data

Claude Response: 7-8/10 accuracy
├─ Comprehensive and well-structured
├─ Some unverified claims (e.g., 30-hour autonomy)
└─ Self-promotional bias (rated itself 9.5/10)

Grok Response: 6-6.7/10 accuracy
├─ Honest about limitations (30% disappointment rate)
├─ Anecdotal sources and blog-based claims
└─ Self-deprecating bias but still competitive
```

**Takeaway:** All three models showed self-serving bias. The routing rules prioritize *independent benchmarks* over self-assessments.

---

## 💡 New Use Cases Covered

### **CLAUDE - Unconventional Applications**
- **Desktop Process Automation**: GUI navigation for compliance checks
- **One-Prompt Micro-Apps**: Dashboards, interactive tools
- **Long-Horizon Agentic Tasks**: Multi-day code reviews
- **Full-Book Academic Summaries**: Research synthesis

### **CHATGPT - Unconventional Applications**
- **SIP Phone Agents**: Customer service hotlines
- **Field Technician Support**: Hands-free camera/mic streaming
- **Talent Identification**: Introspection and blind-spot analysis
- **Financial Forecasting**: Automated SWOT in spreadsheets

### **GROK - Unconventional Applications**
- **Government/DoD Integration**: Verified $200M contract (July 2025)
- **Live E-commerce Sentiment**: Real-time brand monitoring
- **Humor-Infused Education**: Quantum physics with personality
- **Political Campaign Analysis**: Social listening at scale

---

## 🎮 Keyword Examples

### Example 1: Multi-Task Prompt
**Prompt:** "Analyze Twitter sentiment about our product launch, then write a technical blog post about the features, and create a dashboard visualization."

**Routing:**
1. "Analyze Twitter sentiment" → **Grok** (realtime_social)
2. "Write a technical blog post" → **Claude** (professional_writing)
3. "Create a dashboard visualization" → **ChatGPT** (data_analysis + multimodal)

---

### Example 2: Coding Task
**Prompt:** "Implement a Python function to solve the traveling salesman problem using dynamic programming."

**Routing:**
- Contains: "implement", "function", "python", "algorithm"
- Category: **coding**
- Model: **Claude** (production-quality code, SWE-bench leader)

---

### Example 3: Mathematical Reasoning
**Prompt:** "Prove that the square root of 2 is irrational using a proof by contradiction."

**Routing:**
- Contains: "prove", "square root", "irrational", "proof"
- Category: **mathematical_reasoning**
- Model: **Grok** (93.3% AIME, strongest math performance)

---

### Example 4: Image Generation
**Prompt:** "Create an illustration of a futuristic city with flying cars and neon lights."

**Routing:**
- Contains: "create", "illustration", "visual"
- Category: **multimodal**
- Model: **ChatGPT** (DALL-E integration, only native image generation)

---

## ⚙️ Configuration

### Editing Routing Rules

Edit `backend/task_rules.json` to customize routing:

```json
{
  "routing_rules": {
    "coding": "claude",
    "mathematical_reasoning": "grok",
    "multimodal": "chatgpt"
  }
}
```

### Available Routing Options

- `"claude"` - Route directly to Claude
- `"chatgpt"` - Route directly to ChatGPT
- `"grok"` - Route directly to Grok
- `"grok_refine_then_claude"` - Legacy: Grok refines, Claude executes

---

## 📈 Performance Comparison

### **Coding Quality**
```
Claude:   ████████████████████████████████████████ (SWE-bench leader)
ChatGPT:  ███████████████████████████████ (54.6-74.9%)
Grok:     ███████████████████████ (competitive)
```

### **Mathematical Reasoning (AIME)**
```
Grok:     ████████████████████████████████████████████████ 93.3%
ChatGPT:  ███████████████ 36.7%
Claude:   ██████████████ 33.9%
```

### **Multimodal Capabilities**
```
ChatGPT:  ████████████████████████████████████████ (native)
Claude:   ████████████ (analysis only)
Grok:     ██ (poor quality)
```

### **Real-time Social Data**
```
Grok:     ████████████████████████████████████████ (native X access)
ChatGPT:  ███████████████████ (web search)
Claude:   ███████████████████ (web search)
```

---

## 🚨 Important Caveats

### **Self-Serving Bias**
All three AI models exhibited bias when evaluating themselves:
- Claude rated itself 9.5/10
- ChatGPT framed itself most favorably despite objectivity attempts
- Grok overcorrected with self-criticism but remained competitive

### **Unverified Claims**
Some claims in the source analysis lack independent verification:
- Claude's "30-hour autonomy" claim
- Grok's specific HumanEval scores
- Some performance metrics from vendor sources only

### **Routing is Probabilistic**
The keyword-based routing is a heuristic. Complex prompts may trigger multiple categories. The system selects the category with the highest keyword match count.

---

## 🎓 Best Practices

1. **Task Specificity**: More specific keywords lead to better routing
   - ❌ "Help me with this" → routes to general
   - ✅ "Debug this Python function" → routes to Claude

2. **Multi-Task Decomposition**: The analyzer splits complex prompts
   - "First solve this equation, then generate an image of the solution"
   - Routes: Part 1 → Grok, Part 2 → ChatGPT

3. **Override Routing**: You can manually specify in your prompt
   - "Using Claude, implement..."
   - "Have Grok solve this math problem..."

4. **Cost Optimization**: For high-volume tasks, consider Grok for efficiency
   - Grok 4 Fast: Most cost-efficient option
   - Claude: Premium pricing, 45 msg/5 hour limits
   - ChatGPT: Mid-tier, $200/month Pro plan

5. **Quality vs Speed Trade-offs**:
   - **Highest Quality Code**: Claude
   - **Fastest Multimodal**: ChatGPT
   - **Best Math Reasoning**: Grok
   - **Most Consistent**: Claude (Constitutional AI)

---

## 📚 Further Reading

- [AI Comparison Summary](../Notes/prompts/AI_Comparison_Summary.md) - Complete analysis
- [README.md](../README.md) - Project setup and usage
- [task_rules.json](../backend/task_rules.json) - Current routing configuration

---

## 🔄 Version History

- **v2.0.0** (2025-01-16): Evidence-based routing with 12 task categories
  - Expanded from 5 to 12 task categories
  - Added 150+ new keywords across all categories
  - Direct routing to Claude (previously only grok_refine_then_claude)
  - Routing based on independent benchmark analysis
  - Documented unconventional use cases for each AI

- **v1.0.0** (2025-01-16): Initial release
  - Basic 5-category routing
  - Grok → Claude pipeline for coding

---

**AI3 Orchestrator v2.0** - Intelligent Multi-Model Task Distribution
**Powered by Evidence-Based AI Selection**
