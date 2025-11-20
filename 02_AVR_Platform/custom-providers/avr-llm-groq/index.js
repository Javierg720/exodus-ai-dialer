const express = require('express');
const { OpenAI } = require('openai');
const fs = require('fs');
const path = require('path');
const app = express();
app.use(express.json());

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const MODEL = process.env.GROQ_MODEL || 'llama3-8b-8192';
const TEMPERATURE = parseFloat(process.env.TEMPERATURE || '0.7');

// Load Clover sales script
let CLOVER_PROMPT = 'You are a helpful assistant.';
try {
  const promptPath = path.join(__dirname, 'clover-prompt.txt');
  if (fs.existsSync(promptPath)) {
    CLOVER_PROMPT = fs.readFileSync(promptPath, 'utf8');
    console.log('[Groq] Loaded Clover sales script');
  }
} catch (err) {
  console.error('[Groq] Failed to load clover-prompt.txt:', err.message);
}

const DEFAULT_SYSTEM_PROMPT = process.env.SYSTEM_PROMPT || CLOVER_PROMPT;

const openai = new OpenAI({
  apiKey: GROQ_API_KEY,
  baseURL: 'https://api.groq.com/openai/v1',  // Groq's OpenAI-compatible endpoint
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', provider: 'groq', model: MODEL });
});

// AVR /prompt-stream endpoint (SSE format with type: "text")
app.post('/prompt-stream', async (req, res) => {
  try {
    const { messages = [], systemPrompt } = req.body;
    const finalSystemPrompt = systemPrompt || DEFAULT_SYSTEM_PROMPT;
    const formattedMessages = [
      { role: 'system', content: finalSystemPrompt },
      ...messages
    ];

    console.log(`[Groq] /prompt-stream with ${messages.length} messages`);

    const completion = await openai.chat.completions.create({
      model: MODEL,
      messages: formattedMessages,
      temperature: TEMPERATURE,
      stream: false  // Buffered full response
    });

    const responseText = completion.choices[0]?.message?.content || '';
    console.log(`[Groq] Response: ${responseText.substring(0, 50)}...`);

    // AVR expects plain JSON with "type": "text" and "content": responseText (not wrapped in SSE)
    res.json({ type: 'text', content: responseText });
  } catch (error) {
    console.error('[Groq] Error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

app.listen(6002, () => {
  console.log('[Groq LLM Provider] Running on port 6002');
});
