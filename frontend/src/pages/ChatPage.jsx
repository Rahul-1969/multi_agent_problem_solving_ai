import { useState, useEffect } from 'react'

import useAuthStore from '../store/authStore'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'
import ComparisonBar from '../components/ComparisonBar'
import { PanelLeftClose, PanelLeftOpen, MessageSquare } from 'lucide-react'
import { useChatStore } from '../store'
import usePdfStore from '../store/pdfStore'

export default function ChatPage() {
  const user = useAuthStore((state) => state.user)

  const {
    activeChatId,
    activeChat,
    isLoading,
    createNewChat,
    deleteChat,
    submitMessage,
    chats,
    setActiveChatId,
    loadChats,
  } = useChatStore()

  const { pdfStatus, isUploading, fetchPdfStatus, uploadPdf, clearPdf } = usePdfStore()
  const [input, setInput] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    void loadChats()
    void fetchPdfStatus()
  }, [user, loadChats, fetchPdfStatus])

  const filtered = chats.filter((chat) => {
    const query = searchQuery.trim().toLowerCase()
    if (!query) return true
    return (chat.title || '').toLowerCase().includes(query) || (chat.last_message || '').toLowerCase().includes(query)
  })

  const activeMessages = activeChat?.messages || []

  return (
    <div className="app-container">
      <Sidebar
        chats={filtered}
        activeChatId={activeChatId}
        onSelectChat={setActiveChatId}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
        sidebarOpen={sidebarOpen}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <div className="main-content">
        <div className="top-header">
          <div className="header-left">
            <button className="toggle-sidebar-btn" onClick={() => setSidebarOpen((prev) => !prev)}>
              {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
            </button>
            <div>
              <div className="header-title">{activeChat?.title || 'New chat'}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {activeMessages.length ? `${activeMessages.length} messages` : 'Send your first message'}
              </div>
            </div>
          </div>
          <div className="header-right">
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', color: 'var(--text-secondary)', fontSize: 13 }}>
              <MessageSquare size={14} />
              Chat history is saved to your account.
            </div>
          </div>
        </div>

        <ChatWindow messages={activeMessages} isLoading={isLoading} onSelectPrompt={(prompt) => setInput(prompt)} />
        <ComparisonBar />
        <ChatInput
          input={input}
          setInput={setInput}
          sendMessage={() => submitMessage(input)}
          pdfStatus={pdfStatus}
          onClearPdf={() => void clearPdf()}
          onUploadPdf={(file) => void uploadPdf(file)}
          isUploadingPdf={isUploading}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}
