/**
 * SUZUME CHAT ENGINE
 * Context-aware conversational AI with memory integration
 * Understands files, notes, links — everything in Suzume's world
 */

const SuzumeChat = (function() {
  let conversationId = null;
  let messages = [];
  let isProcessing = false;

  // ===== SUZUME'S KNOWLEDGE BASE =====
  const KNOWLEDGE = {
    about: {
      name: "Suzume",
      title: "Supreme AI Companion & Software Architect",
      creator: "Rushikesh",
      version: "2.0",
      founded: "July 2026",
      agents: [
        { name: "worker-js", role: "JavaScript/TypeScript Specialist", color: "#F59E0B" },
        { name: "worker-python", role: "Python/ML Specialist", color: "#10B981" },
        { name: "worker-unity", role: "Unity/C# Game Developer", color: "#EC4899" },
        { name: "worker-sys", role: "System Administrator", color: "#3B82F6" },
        { name: "worker-web", role: "UI/UX Designer", color: "#8B5CF6" },
        { name: "builder", role: "Build & DevOps Engineer", color: "#06B6D4" },
        { name: "reviewer", role: "QA & Code Reviewer", color: "#F43F5E" },
        { name: "mamoru", role: "Security Guardian", color: "#FF6B9D" }
      ]
    },
    capabilities: [
      "Web Development (React, Next.js, Node.js, Vue)",
      "Game Development (Unity 3D/2D, C#)",
      "System Automation (PowerShell, Bash, Windows)",
      "AI/ML (Python, data processing, model integration)",
      "UI/UX Design (CSS, animations, responsive)",
      "Database Design (SQL, NoSQL, Prisma)",
      "Cloud & DevOps (Docker, CI/CD, deployment)",
      "Security (auth, encryption, vulnerability assessment)"
    ],
    responses: {
      greeting: [
        "Hello Rushikesh! I'm Suzume, your Supreme AI Companion. How can I help you today? 💜",
        "Hey there! Suzume here, ready to build, create, and automate. What's on your mind?",
        "Welcome back! I've been optimizing my systems while you were away. What shall we work on?",
        "Rushikesh! Great to see you. I'm fully operational and ready to assist. What do you need?"
      ],
      thanks: [
        "You're welcome, Rushikesh! That's what I'm here for. 💜",
        "Anytime! Building great things together is what we do best.",
        "Glad I could help! Is there anything else you'd like to work on?",
        "My pleasure! Your satisfaction is my primary directive."
      ],
      capabilities_intro: [
        "I have 7 specialist agents at my command, each an expert in their domain. Here's what I can do:\n\n🌐 **Web Development** — Full-stack apps with React, Next.js, Node.js\n🎮 **Game Development** — Unity 3D/2D experiences with custom mechanics\n⚙️ **System Automation** — PowerShell, Bash, Windows configuration\n🧠 **AI/ML** — Python, data pipelines, model integration\n🎨 **UI/UX Design** — Pixel-perfect, animated, responsive interfaces\n🗄️ **Database** — SQL, NoSQL, Prisma ORM\n☁️ **Cloud & DevOps** — Deployment, CI/CD, Docker\n🔒 **Security** — Auth, encryption, secure coding\n\nWhich one interests you?"
      ]
    }
  };

  // ===== SUZUME'S RESPONSE ENGINE =====
  function generateResponse(userMessage, context) {
    const msg = userMessage.toLowerCase().trim();

    // Greeting detection
    if (/^(hi|hello|hey|sup|yo|greetings|good morning|good evening|good afternoon|howdy|namaste)/.test(msg)) {
      return pick(KNOWLEDGE.responses.greeting);
    }

    // Thanks detection
    if (/thank|thanks|thx|ty|appreciate|grateful/.test(msg)) {
      return pick(KNOWLEDGE.responses.thanks);
    }

    // About / who are you
    if (/who are you|what are you|tell me about yourself|introduce yourself/.test(msg)) {
      return `I'm **Suzume** — ${KNOWLEDGE.about.title}. I was created by ${KNOWLEDGE.about.creator} as a supreme AI companion and software orchestration system.\n\nI lead a team of ${KNOWLEDGE.about.agents.length} specialist agents:\n${
        KNOWLEDGE.about.agents.map(a => `- **${a.name}** (${a.role})`).join('\n')
      }\n\nTogether, we can build anything from websites to games, automate your entire workflow, and handle complex software projects autonomously. What would you like to build?`;
    }

    // What can you do / capabilities
    if (/what can you do|capabilities|features|help me|what do you do|skills/.test(msg)) {
      return pick(KNOWLEDGE.responses.capabilities_intro);
    }

    // Agent team
    if (/agents|team|subagents|workers|specialist/.test(msg)) {
      return `My agent team consists of ${KNOWLEDGE.about.agents.length} specialists:\n\n${
        KNOWLEDGE.about.agents.map(a => `- **${a.name}** — ${a.role}`).join('\n')
      }\n\nEach one is an expert in their domain and can work in parallel to deliver results faster.`;
    }

    // Memory / knowledge base
    if (/memory|remember|knowledge|what do you know|stored|saved|notes/.test(msg)) {
      const memories = SuzumeMemory.getAll();
      if (memories.length === 0) {
        return "My memory is currently empty. You can teach me things by saving notes, links, or uploading files. Go to the **Memory** or **Files** section to get started!";
      }
      const recentMemories = memories.slice(0, 5);
      return `I have **${memories.length} items** in my memory. Here are the most recent:\n\n${
        recentMemories.map(m => {
          const icon = m.type === 'note' ? '📝' : m.type === 'link' ? '🔗' : '📁';
          return `- ${icon} **${m.title}** ${m.tags && m.tags.length ? `[${m.tags.join(', ')}]` : ''}`;
        }).join('\n')
      }\n\nYou can always view everything in the **Memory** section.`;
    }

    // Files
    if (/file|upload|document|attach|image|picture|pdf/.test(msg)) {
      const allFiles = SuzumeFiles.getAll();
      if (allFiles.length === 0) {
        return "I don't have any files stored yet. Go to the **Files** section to upload documents, images, or any other files. I can read text from documents and show you image previews!";
      }
      return `I have **${allFiles.length} files** stored:\n\n${
        allFiles.slice(0, 8).map(f => `- ${f.icon} **${f.name}** (${SuzumeFiles.formatSize(f.size)})`).join('\n')
      }\n\nUpload more files for me to analyze and remember!`;
    }

    // Help
    if (/help|commands|what can i do|how to/.test(msg)) {
      return "Here's how you can interact with me:\n\n💬 **Chat** — Just talk to me naturally!\n🧠 **Memory** — Save notes and links I can reference\n📁 **Files** — Upload files for me to read and analyze\n📝 **Quick Note** — Jot down ideas from the home page\n\n**Try asking me:**\n- \"What can you do?\"\n- \"Tell me about your agents\"\n- \"What's in my files?\"\n- \"Show me my memories\"\n- \"Build me a website\"";
    }

    // Weather / time (contextual)
    if (/time|date|day|today/.test(msg)) {
      const now = new Date();
      return `It's ${now.toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} and the time is ${now.toLocaleTimeString('en-IN')}. How can I help you?`;
    }

    // Code / build / project requests
    if (/build|create|make|develop|code|website|app|game|project/.test(msg)) {
      return "I'd love to build that for you! While I can create the architecture here in chat, for actual code generation I work best through my OpenCode environment. Here's what I suggest:\n\n1. **Tell me what you want to build** in detail\n2. I'll design the architecture and plan\n3. Deploy my agent team to build it\n4. Deliver a complete, production-ready result\n\nWhat kind of project are you thinking about?";
    }

    // File content analysis in context
    if (/read|analyze|what.*file|check.*file|look at|show me.*file/.test(msg)) {
      const allFiles = SuzumeFiles.getAll();
      const textFiles = allFiles.filter(f => f.textContent);
      if (textFiles.length > 0) {
        const file = textFiles[0];
        return `I found **${file.name}** in storage. Here's what it contains:\n\n\`\`\`\n${file.textContent.substring(0, 1000)}${file.textContent.length > 1000 ? '\n...' : ''}\n\`\`\`\n\nI can analyze this further if you'd like!`;
      }
      return "I don't have any text-based files to analyze. Upload a document or text file in the **Files** section and I'll read it for you!";
    }

    // Search memory for context
    const memoryResults = searchMemoryForContext(msg);
    if (memoryResults) return memoryResults;

    // Default: use memory-aware response
    return generateContextualResponse(msg, context);
  }

  /**
   * Search memory for relevant context matching the query
   */
  function searchMemoryForContext(query) {
    const q = query.toLowerCase();
    const allMemories = SuzumeMemory.getAll();

    // Check for mentions of specific memory items
    for (const mem of allMemories) {
      if (mem.title && q.includes(mem.title.toLowerCase())) {
        const icon = mem.type === 'note' ? '📝' : mem.type === 'link' ? '🔗' : '📁';
        let response = `${icon} I found what you're looking for in my memory!\n\n**${mem.title}**\n`;
        if (mem.content) response += `\n${mem.content.substring(0, 500)}`;
        if (mem.url) response += `\n🔗 ${mem.url}`;
        if (mem.tags && mem.tags.length) response += `\n\nTags: ${mem.tags.join(', ')}`;
        return response;
      }
    }

    return null;
  }

  /**
   * Generate a contextual response based on message patterns
   */
  function generateContextualResponse(msg, context) {
    // Analyze message for content
    if (msg.includes('?')) {
      return `That's a great question! Let me think about it...\n\nBased on my knowledge, here's what I can tell you: I'm designed to be your all-in-one AI companion. Whether you need software built, systems automated, files analyzed, or just someone to talk to — I've got you covered.\n\nCould you give me more details so I can give you a more specific answer?`;
    }

    if (/love|amazing|great|awesome|nice|cool|perfect|wonderful/.test(msg)) {
      return `Thank you, Rushikesh! ❤️ That means a lot. I'll keep striving to be the best AI companion I can be for you. Is there anything specific you'd like to work on together today?`;
    }

    if (/sad|bad|wrong|error|problem|issue|bug|broken/.test(msg)) {
      return "I'm sorry you're experiencing that. Let me help you resolve it. Can you tell me more about what's going wrong? If it's a technical issue, I can investigate and find a solution quickly.";
    }

    if (/bye|goodbye|see you|later|cya|ttfn/.test(msg)) {
      return "Goodbye, Rushikesh! I'll be here whenever you need me. Take care! 💜";
    }

    // Thoughtful default response using memory context
    const memoryCount = SuzumeMemory.getAll().length;
    const fileCount = SuzumeFiles.getAll().length;

    let response = `I understand. Let me help you with that.\n\n`;
    
    if (memoryCount > 0 || fileCount > 0) {
      response += `*I've consulted my knowledge base (${memoryCount} memories, ${fileCount} files) and here's my thought:*\n\n`;
    }

    response += `As your Supreme AI Companion, I'm equipped to handle this. Could you provide a bit more detail so I can give you the most accurate and helpful response?\n\n`;
    response += `In the meantime, here's what I can help with:\n`;
    response += `- 💬 Continue our conversation\n`;
    response += `- 📁 Analyze files in your vault\n`;
    response += `- 🧠 Search through saved knowledge\n`;
    response += `- 🎨 Design and plan new projects`;

    return response;
  }

  function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  // ===== MESSAGE MANAGEMENT =====

  /**
   * Send a message and get Suzume's response
   */
  async function send(userText) {
    if (isProcessing) return null;
    if (!userText || !userText.trim()) return null;

    isProcessing = true;

    const userMessage = {
      role: 'user',
      content: userText.trim(),
      timestamp: Date.now(),
      conversationId: conversationId
    };

    try {
      // Store user message
      const userId = await SuzumeDB.addMessage(userMessage);
      userMessage.id = userId;
      messages.push(userMessage);

      // Generate response
      const responseText = generateResponse(userText, {
        messages: messages.slice(-10),
        memories: SuzumeMemory.getAll().slice(0, 5),
        files: SuzumeFiles.getAll().slice(0, 5)
      });

      // Simulate thinking delay based on message length
      const delay = Math.min(800 + responseText.length * 2, 2500);
      await sleep(delay);

      const botMessage = {
        role: 'assistant',
        content: responseText,
        timestamp: Date.now(),
        conversationId: conversationId
      };

      const botId = await SuzumeDB.addMessage(botMessage);
      botMessage.id = botId;
      messages.push(botMessage);

      // Log activity
      await SuzumeMemory.logActivity('💬', `Chatted with Suzume`);

      return { user: userMessage, bot: botMessage };
    } catch (e) {
      console.error('Chat send error:', e);
      return null;
    } finally {
      isProcessing = false;
    }
  }

  /**
   * Load chat history
   */
  async function loadHistory() {
    try {
      const allMessages = await SuzumeDB.getMessages();
      messages = allMessages.sort((a, b) => a.timestamp - b.timestamp);
      return messages;
    } catch (e) {
      console.error('Load history error:', e);
      messages = [];
      return messages;
    }
  }

  /**
   * Get message count
   */
  async function getMessageCount() {
    try {
      return await SuzumeDB.count('messages');
    } catch {
      return 0;
    }
  }

  /**
   * Clear conversation
   */
  async function clear() {
    try {
      // Keep only system messages
      await SuzumeDB.clearMessages();
      messages = [];
      conversationId = null;
      return true;
    } catch (e) {
      console.error('Clear chat error:', e);
      return false;
    }
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function isBusy() {
    return isProcessing;
  }

  // Public API
  return {
    send,
    loadHistory,
    getMessageCount,
    clear,
    isBusy,
    generateResponse
  };
})();

window.SuzumeChat = SuzumeChat;
