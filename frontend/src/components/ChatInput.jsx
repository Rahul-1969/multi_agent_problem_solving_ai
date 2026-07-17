import { useRef } from "react";
import { Send, Paperclip, X, FileText, Loader2 } from "lucide-react";

export default function ChatInput({
  input,
  setInput,
  sendMessage,
  pdfStatus,
  onClearPdf,
  onUploadPdf,
  isUploadingPdf,
  isLoading,
  useRag,
  setUseRag,
}) {
  const fileInputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      onUploadPdf(file);
    } else if (file) {
      alert("Only PDF files are supported.");
    }
    // reset file input value so same file can be selected again if cleared
    e.target.value = "";
  };

  const triggerFileSelect = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="chat-input-sticky">
      <div className="chat-input-container">
        
        {/* PDF Status indicator above the chat input box */}
        {isUploadingPdf && (
          <div className="pdf-attachment-badge">
            <Loader2 size={13} className="animate-spin" />
            <span>Uploading PDF...</span>
          </div>
        )}

        {!isUploadingPdf && pdfStatus && pdfStatus.loaded && (
          <div className="pdf-attachment-badge">
            <FileText size={13} />
            <span>Grounded to: <strong>{pdfStatus.filename}</strong> {pdfStatus.pages ? `(${pdfStatus.pages} pages)` : ""}</span>
            <button className="pdf-attachment-close" onClick={onClearPdf} title="Unload PDF document">
              <X size={12} />
            </button>
          </div>
        )}

        <div className="chat-input-box">
          <div className="chat-actions-left">
            <button 
              className="attach-btn" 
              onClick={triggerFileSelect} 
              title="Attach PDF for document Q&A"
              disabled={isLoading || isUploadingPdf}
            >
              <Paperclip size={18} />
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: "none" }} 
              accept=".pdf"
              onChange={handleFileChange}
            />
          </div>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={pdfStatus && pdfStatus.loaded ? "Ask a question about this document..." : "Message NeuralChat..."}
            className="chat-textarea"
            rows={1}
            disabled={isLoading}
            style={{ height: input ? "auto" : "36px" }}
          />

          <button
            onClick={sendMessage}
            className="send-btn"
            disabled={!input.trim() || isLoading || isUploadingPdf}
            title="Send message"
          >
            <Send size={15} />
          </button>
        </div>
        
        <div className="chat-input-toolbar">
          <label className="rag-toggle-label" htmlFor="rag-toggle">
            <input
              id="rag-toggle"
              type="checkbox"
              className="rag-toggle-checkbox"
              checked={!!useRag}
              onChange={(e) => setUseRag(e.target.checked)}
              disabled={isLoading}
            />
            <span className="rag-toggle-text">Use my notes</span>
          </label>
        </div>

        <p className="disclaimer-text">
          NeuralChat can make mistakes. Verify important info.
        </p>
      </div>
    </div>
  );
}