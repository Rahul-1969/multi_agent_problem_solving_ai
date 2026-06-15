# Frontend Components Documentation

## New Components Overview

All new components are located in `/frontend/src/components/`

### 1. MarkdownRenderer.jsx

Renders markdown content with full formatting support.

**Props:**
```javascript
<MarkdownRenderer 
  content={markdownString}  // String containing markdown content
/>
```

**Supported Markdown:**
- Headings (# through ######)
- Bold (**text**)
- Italic (*text*)
- Inline code (`code`)
- Code blocks with syntax highlighting
- Lists (ordered and unordered)
- Tables (GitHub Flavored Markdown)
- Blockquotes
- Links
- Horizontal rules

**Example:**
```javascript
import MarkdownRenderer from './components/MarkdownRenderer';

function MyComponent() {
  const markdown = `# Title
## Subtitle
This is **bold** and *italic*.
\`\`\`python
def hello():
    print("Hello")
\`\`\`
- List item 1
- List item 2`;

  return <MarkdownRenderer content={markdown} />;
}
```

---

### 2. CodingResponse.jsx

Renders structured coding problem solutions.

**Props:**
```javascript
<CodingResponse 
  data={{
    title: string,              // Problem title
    explanation: string,        // Markdown explanation
    code: string,               // Code content
    language: string,           // Programming language
    output: string,             // Expected output (markdown)
    time_complexity: string,    // e.g., "O(n log n)"
    space_complexity: string,   // e.g., "O(1)"
    key_points: string[]        // Array of key insights
  }}
/>
```

**Example:**
```javascript
<CodingResponse 
  data={{
    title: "Binary Search Algorithm",
    explanation: "Binary search divides the array in half each iteration...",
    code: "def binsearch(arr, x):\n    l, r = 0, len(arr)-1\n    while l<=r:\n        m = (l+r)//2\n        if arr[m]==x: return m\n        elif arr[m]<x: l=m+1\n        else: r=m-1\n    return -1",
    language: "python",
    output: "binsearch([1,3,5,7,9], 5) # Returns 2",
    time_complexity: "O(log n)",
    space_complexity: "O(1)",
    key_points: [
      "Only works on sorted arrays",
      "Much faster than linear search"
    ]
  }}
/>
```

**Display:**
- Title with purple icon
- Explanation section with markdown
- Code section with syntax highlighting and copy button
- Complexity grid showing time and space complexity
- Output section
- Key points as bulleted list

---

### 3. MedicalResponse.jsx

Renders medical assessment information.

**Props:**
```javascript
<MedicalResponse 
  data={{
    symptoms: string,          // Markdown description
    possible_causes: string[], // Array of possible conditions
    recommendations: string,   // Markdown recommendations
    when_to_consult: string,   // Markdown warning/emergency info
    disclaimer: string         // Default: standard medical disclaimer
  }}
/>
```

**Example:**
```javascript
<MedicalResponse 
  data={{
    symptoms: "## Identified Symptoms\n- Sore throat\n- Fever",
    possible_causes: [
      "Common Cold",
      "Influenza",
      "Strep Throat"
    ],
    recommendations: "## Care Tips\n1. Rest\n2. Stay hydrated\n3. Take over-the-counter pain relievers",
    when_to_consult: "## Emergency: Seek immediate care if...\n- High fever (>104°F)\n- Difficulty breathing"
  }}
/>
```

**Display:**
- Red icon title
- Symptoms section
- Possible causes as alert list
- Recommendations with green accent
- When to consult with red alert styling
- Medical disclaimer at bottom

---

### 4. AcademicResponse.jsx

Renders educational content.

**Props:**
```javascript
<AcademicResponse 
  data={{
    title: string,        // Topic title
    definition: string,   // Markdown definition
    explanation: string,  // Detailed explanation
    example: string,      // Markdown example
    diagram: string,      // ASCII or markdown diagram
    key_formulas: string[],  // Array of formula strings
    tips: string[],       // Study tips
    summary: string       // Summary conclusion
  }}
/>
```

**Example:**
```javascript
<AcademicResponse 
  data={{
    title: "Newton's Second Law",
    definition: "**F = ma** - Force equals mass times acceleration",
    explanation: "This fundamental law states...",
    example: "Example: A 2kg ball pushed with 10N force\nAcceleration = 10/2 = 5 m/s²",
    key_formulas: [
      "**F = m × a**",
      "**a = F / m**"
    ],
    tips: [
      "Force and acceleration are in same direction",
      "Consider net force (sum of all forces)"
    ],
    summary: "F=ma is the foundation of classical mechanics"
  }}
/>
```

**Display:**
- Blue icon title
- Definition in highlighted box
- Detailed explanation
- Formula grid
- Example section with amber accent
- Study tips with checkmark icons
- Summary section with brain icon

---

### 5. CopyResponseButton.jsx

Reusable copy button component.

**Props:**
```javascript
<CopyResponseButton 
  text={stringToCopy}      // Text to copy to clipboard
  label="Copy"             // Optional: button label (default: "Copy Response")
/>
```

**Example:**
```javascript
<CopyResponseButton 
  text={complexResponse}
  label="Copy Full Response"
/>
```

**Features:**
- Clicking copies text to clipboard
- Shows "Copied!" feedback for 2 seconds
- Hover effects
- Smooth transitions

---

### 6. MessageBubble.jsx (Updated)

Enhanced message bubble with intelligent routing.

**Props:**
```javascript
<MessageBubble 
  sender="user" | "bot"        // Message sender
  text={messageText}           // Raw text or markdown
  domain="coding" | "medical" | "education" | "college" | "general" | "pdf"
  data={structuredData}        // Domain-specific data object
/>
```

**Automatic Routing:**
- `domain: "coding"` → Renders `CodingResponse`
- `domain: "medical"` → Renders `MedicalResponse`
- `domain: "education"` → Renders `AcademicResponse`
- `domain: "college"` → Custom college layout
- `domain: "general"` or other → Renders `MarkdownRenderer`

---

## Integration Example

```javascript
import MessageBubble from './components/MessageBubble';

function ChatWindow({ messages }) {
  return (
    <div className="chat-window">
      {messages.map((msg, idx) => (
        <MessageBubble
          key={idx}
          sender={msg.sender}
          text={msg.text}
          domain={msg.domain}
          data={msg.data}
        />
      ))}
    </div>
  );
}
```

---

## Styling & Customization

### CSS Classes

All new components use CSS classes defined in `index.css`:

- `.markdown-content` - Wrapper for markdown
- `.structured-response` - Wrapper for structured responses
- `.response-title` - Title section
- `.response-section` - Each section
- `.code-block-wrapper` - Code block container
- `.complexity-item` - Complexity cards
- `.definition-section` - Academic definition
- `.alert-box` - Medical alerts
- `.disclaimer` - Disclaimer styling

### Color Variables

Defined in `:root` of `index.css`:

```css
--accent-color: #10a37f;        /* ChatGPT Green */
--accent-blue: #3b82f6;         /* Academic */
--accent-purple: #a855f7;       /* Coding */
--accent-red: #ef4444;          /* Medical */
--accent-amber: #f59e0b;        /* Examples */
```

### Animations

- `fadeUp` - Messages fade in and slide up
- `fadeIn` - General fade in effect
- `slideIn` - Slide in from top
- `typingBounce` - Typing indicator dots

---

## Best Practices

1. **Always provide domain** - Ensures correct rendering
2. **Use markdown in text fields** - Rich formatting
3. **Keep data structure consistent** - With domain spec
4. **Test with real data** - Check formatting
5. **Use copy buttons** - For code snippets
6. **Responsive sizing** - Components adapt to screen

---

## Troubleshooting

**Code block not rendering?**
- Ensure language is specified: `language: "python"`
- Check markdown formatting: \`\`\`python\ncode\n\`\`\`

**Markdown not working?**
- Verify markdown syntax
- Check for proper escaping
- Use GFM table syntax for tables

**Component not displaying?**
- Check props structure
- Verify domain matches component
- Check console for errors

---

## Performance Notes

- Syntax highlighting is client-side (fast)
- Markdown rendering is optimized with React Markdown
- Code splitting recommended for production
- Components use memo optimization where applicable

---

## Future Enhancements

Potential additions:
- LaTeX/KaTeX for mathematical equations
- Diagram rendering libraries
- Theme customization
- Response sharing
- User ratings/feedback
