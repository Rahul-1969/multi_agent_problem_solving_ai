import { useState, useEffect, useMemo, useCallback } from 'react'
import chatService from '../services/chatService'
import { useAuth } from '../context/AuthContext'

export default function useChat() {
  const { logout } = useAuth()
  const [chats, setChats] = useState([])
  const [activeChatId, setActiveChatId] = useState(null)
  const [activeChat, setActiveChat] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const loadChat = useCallback(async (chatId) => {
    try {
      const data = await chatService.fetchChat(chatId)
      if (data?.success) {
        setActiveChat({
          id: data.chat_id,
          title: data.title || 'New chat',
          messages: data.messages || [],
        })
      }
    } catch (err) {
      if (err?.status === 401) logout()
      throw err
    }
  }, [logout])

  const createNewChat = useCallback(async () => {
    try {
      const data = await chatService.createChat()
      if (data?.success) {
        const chat = {
          id: data.chat_id,
          title: data.title || 'New chat',
          messages: data.messages || [],
        }
        setChats((prev) => [chat, ...prev])
        setActiveChatId(chat.id)
        setActiveChat(chat)
      }
    } catch (err) {
      if (err?.status === 401) logout()
      throw err
    }
  }, [logout])

  const loadChats = useCallback(async () => {
    try {
      const data = await chatService.fetchChats()
      if (data?.success) {
        const list = data.chats || []
        setChats(list)
        if (list.length > 0) {
          setActiveChatId(list[0].id)
          await loadChat(list[0].id)
        } else {
          await createNewChat()
        }
      }
    } catch (err) {
      if (err?.status === 401) logout()
      throw err
    }
  }, [logout, loadChat, createNewChat])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadChats()
  }, [loadChats])

  useEffect(() => {
    if (activeChatId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      void loadChat(activeChatId)
    }
  }, [activeChatId, loadChat])

  async function deleteChat(id) {
    await chatService.deleteChat(id)
    setChats((prev) => prev.filter((c) => c.id !== id))
    if (activeChatId === id) {
      const next = chats.find((c) => c.id !== id)
      if (next) {
        setActiveChatId(next.id)
      } else {
        setActiveChatId(null)
        setActiveChat(null)
      }
    }
  }

  async function submitMessage(text, pdfStatus) {
    const trimmed = text.trim()
    if (!trimmed) return

    if (!activeChatId) await createNewChat()
    const currentChatId = activeChatId
    setIsLoading(true)

    try {
      if (pdfStatus?.loaded) {
        await chatService.postMessage(currentChatId, {
          sender: 'user',
          content: trimmed,
          domain: 'user',
        })
        const pdfResponse = await chatService.sendMessage(trimmed)
        const botResp = pdfResponse.response || 'Unable to answer.'
        await chatService.postMessage(currentChatId, {
          sender: 'bot',
          content: botResp,
          domain: 'pdf',
          data: { answer: botResp },
        })
        await loadChat(currentChatId)
        setChats((prev) =>
          prev.map((chat) =>
            chat.id === currentChatId
              ? { ...chat, title: chat.title || trimmed.slice(0, 40), updated_at: new Date().toISOString() }
              : chat,
          ),
        )
      } else {
        const result = await chatService.sendMessage(trimmed, currentChatId)
        if (result?.success) {
          setActiveChat((prev) => ({
            ...prev,
            messages: result.messages || prev?.messages || [],
          }))
          setChats((prev) =>
            prev.map((chat) =>
              chat.id === currentChatId ? { ...chat, updated_at: new Date().toISOString() } : chat,
            ),
          )
        }
      }
    } catch (err) {
      setActiveChat((prev) => ({
        ...prev,
        messages: [
          ...(prev?.messages || []),
          { sender: 'bot', text: 'Something went wrong. Please try again.', domain: 'general' },
        ],
      }))
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const filteredChats = useMemo(() => chats, [chats])

  return {
    chats,
    activeChatId,
    setActiveChatId,
    activeChat,
    isLoading,
    loadChats,
    loadChat,
    createNewChat,
    deleteChat,
    submitMessage,
    filteredChats,
    setChats,
  }
}
