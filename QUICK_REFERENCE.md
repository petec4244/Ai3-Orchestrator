# AI3 Orchestrator - Quick Reference Guide

## 🚀 Quick Decision Tree

```
Need to...
│
├─ Write production code? ────────────────────► CLAUDE
│
├─ Solve complex math/STEM problem? ──────────► GROK
│
├─ Generate images/voice/video? ──────────────► CHATGPT
│
├─ Analyze Twitter/social trends? ────────────► GROK
│
├─ Write technical documentation? ────────────► CLAUDE
│
├─ Summarize long articles? ──────────────────► CHATGPT
│
├─ Process long documents (>50K tokens)? ─────► CLAUDE
│
├─ Analyze data/create visualizations? ───────► CHATGPT
│
├─ Brainstorm creative ideas? ────────────────► GROK
│
├─ Automate desktop/GUI tasks? ───────────────► CLAUDE
│
├─ Integrate with APIs/webhooks? ─────────────► CHATGPT
│
└─ General versatile task? ───────────────────► CHATGPT
```

---

## 📊 AI Strengths at a Glance

| Capability | Claude | ChatGPT | Grok |
|------------|--------|---------|------|
| **Coding Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Math/STEM** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Creative Writing** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Multimodal** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **Real-time Data** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Long Documents** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Consistency** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Cost Efficiency** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 Keyword Triggers

### Automatically Routes to CLAUDE
```
code, function, refactor, debug, github, pull request, codebase,
story, narrative, creative writing, long-form, engaging,
technical writing, api docs, specification, professional,
document, pdf, book, manuscript, 200k context,
automate, gui, desktop automation, workflow, rpa
```

### Automatically Routes to CHATGPT
```
summarize, tldr, overview, brief, digest,
analyze data, chart, visualization, excel, statistics,
image, picture, generate image, dalle, voice, video, audio,
integrate, api integration, zapier, webhook, connector
```

### Automatically Routes to GROK
```
math, calculate, equation, solve, proof, theorem, calculus,
stem, physics, chemistry, biology, scientific,
twitter, social media, trending, sentiment, real-time,
brainstorm, creative solution, unique perspective, innovative
```

---

## 💻 Example Prompts

### CLAUDE Examples
```bash
# Production coding
python main.py "Implement a REST API for user authentication with JWT tokens"

# Creative writing
python main.py "Write a short story about an AI discovering emotions"

# Technical docs
python main.py "Create API documentation for our payment processing endpoints"

# Document processing
python main.py "Analyze this 100-page research paper and extract key findings"

# Automation
python main.py "Automate the process of filling out this Excel form using GUI automation"
```

### CHATGPT Examples
```bash
# Summarization
python main.py "Summarize this 50-page quarterly report into key points"

# Data analysis
python main.py "Analyze this CSV dataset and create visualization recommendations"

# Image generation
python main.py "Generate an image of a sunset over mountains with a lake"

# Integration
python main.py "Create a webhook integration between Stripe and our database"

# General versatile
python main.py "Help me understand quantum computing in simple terms"
```

### GROK Examples
```bash
# Mathematical reasoning
python main.py "Prove that there are infinitely many prime numbers"

# Real-time social
python main.py "Analyze current Twitter sentiment about electric vehicles"

# STEM research
python main.py "Explain the latest developments in quantum entanglement"

# Creative insights
python main.py "Brainstorm 10 innovative solutions for urban traffic congestion"

# Breaking news
python main.py "What are the latest trending topics on social media right now?"
```

---

## 🔧 Configuration

### View Current Routing Rules
```bash
cat backend/task_rules.json
```

### Modify Routing
Edit `backend/task_rules.json`:
```json
{
  "routing_rules": {
    "coding": "claude",              // Change to "grok" or "chatgpt"
    "mathematical_reasoning": "grok",
    "multimodal": "chatgpt"
  }
}
```

### Test Routing
```bash
# See which AI gets selected
python main.py "Your test prompt here"
# Check logs in backend/orchestrator.log
```

---

## 📈 Performance Benchmarks

### Coding (SWE-bench Verified)
```
Claude:   ████████████████████████ Leader
ChatGPT:  ████████████████ 54.6-74.9%
Grok:     ████████████ Competitive
```

### Math (AIME 2025)
```
Grok:     ████████████████████████████ 93.3%
ChatGPT:  ████████ 36.7%
Claude:   ███████ 33.9%
```

### Context Window
```
ChatGPT:  ████████████████████████████████ 1M tokens
Claude:   ████████ 200K tokens
Grok:     ████ Standard
```

---

## 🎓 Best Practices

### ✅ DO
- Use specific keywords in your prompts
- Let the orchestrator auto-route based on task type
- Review routing logs to understand decisions
- Combine multiple AIs for multi-part tasks
- Use Claude for code that will go to production
- Use Grok for complex mathematical proofs
- Use ChatGPT for image/video generation

### ❌ DON'T
- Manually specify AI unless you have a specific reason
- Expect perfect routing with vague prompts
- Use Grok for image generation (poor quality)
- Use Claude for pure math problems (use Grok)
- Use ChatGPT for creative storytelling (use Claude)

---

## 🔍 Troubleshooting

### Wrong AI Selected?
**Problem:** Task routed to unexpected AI
**Solution:** Add more specific keywords from the routing guide

```bash
# Too generic - might route incorrectly
"Help me with this"

# Specific - routes correctly
"Debug this Python function for calculating Fibonacci numbers"
```

### Multi-Part Tasks Not Splitting?
**Problem:** Complex prompt treated as single task
**Solution:** Use clear separators

```bash
# Use numbered lists or "then"
"1. Solve this equation 2. Generate an image of the graph"
"Calculate the derivative, then create a visualization"
```

### Check Routing Decision
```bash
# View orchestrator logs
cat backend/orchestrator.log | grep "Processing"
```

---

## 📚 Additional Resources

- **[AI Routing Guide](docs/AI_ROUTING_GUIDE.md)** - Complete routing documentation
- **[README.md](README.md)** - Full setup instructions
- **[task_rules.json](backend/task_rules.json)** - Current configuration
- **[AI Comparison Summary](../../../Notes/prompts/AI_Comparison_Summary.md)** - Evidence basis

---

## 🚨 Common Mistakes

### Mistake 1: Forcing the Wrong AI
```bash
# ❌ BAD: Forcing Grok for coding
python main.py "Use Grok to write production code"
# Result: Lower quality, less consistent

# ✅ GOOD: Let orchestrator choose
python main.py "Write production code for user authentication"
# Result: Routes to Claude automatically
```

### Mistake 2: Vague Prompts
```bash
# ❌ BAD: Too vague
python main.py "Do something with data"
# Result: Routes to general → ChatGPT (may not be optimal)

# ✅ GOOD: Specific
python main.py "Analyze CSV data and create statistical visualizations"
# Result: Routes to data_analysis → ChatGPT (optimal)
```

### Mistake 3: Ignoring AI Limitations
```bash
# ❌ BAD: Asking Grok for images
python main.py "Grok, generate an image of a cat"
# Result: Poor quality, watermarks

# ✅ GOOD: Use ChatGPT
python main.py "Generate an image of a cat wearing a hat"
# Result: Routes to multimodal → ChatGPT with DALL-E
```

---

## 💡 Pro Tips

1. **Batch Similar Tasks**: Group tasks by type for efficiency
   ```bash
   # Instead of 5 separate calls, combine:
   python main.py "Write 5 Python functions: 1) fibonacci 2) prime check..."
   ```

2. **Leverage Strengths**: Multi-stage prompts use multiple AIs
   ```bash
   python main.py "Use Grok to solve this equation, then have ChatGPT create a graph visualization"
   ```

3. **Override When Needed**: Explicitly request an AI
   ```bash
   python main.py "Claude, write a detailed analysis of..."
   ```

4. **Check Confidence**: Review `orchestrator.log` for confidence scores
   ```bash
   grep "confidence" backend/orchestrator.log
   ```

5. **Cost Optimization**: Use Grok for high-volume, less critical tasks
   ```bash
   # Hundreds of simple calculations? Use Grok
   python main.py "Calculate compound interest for 100 scenarios..."
   ```

---

**Quick Reference v2.0** | AI3 Orchestrator | Evidence-Based Routing
