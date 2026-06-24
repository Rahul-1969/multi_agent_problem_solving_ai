import create from 'zustand'
import chatService from '../services/chatService'
import pdfService from '../services/pdfService'
import usePdfStore from './pdfStore'

const useChatStore = create((set, get) => ({
  chats: [],
  activeChatId: null,
  activeChat: null,
  isLoading: false,
  currentDomain: 'general',

  setChats(chats) {
    set({ chats })
  },

  setActiveChatId(chatId) {
    set({ activeChatId: chatId })
    if (chatId) {
      void get().loadChat(chatId)
    }
  },

  setActiveChat(activeChat) {
    set({ activeChat })
  },

  setIsLoading(isLoading) {
    set({ isLoading })
  },

  setCurrentDomain(domain) {
    set({ currentDomain: domain || 'general' })
  },

  async loadChats() {
    try {
      const data = await chatService.fetchChats()
      if (data?.success) {
        const list = data.chats || []
        set({ chats: list })
        if (list.length > 0) {
          set({ activeChatId: list[0].id })
          await get().loadChat(list[0].id)
        }
      }
    } catch (err) {
      console.error('Failed to load chats:', err)
      throw err
    }
  },

  async loadChat(chatId) {
    try {
      const data = await chatService.fetchChat(chatId)
      if (data?.success) {
        set({
          activeChat: {
            id: data.chat_id,
            title: data.title || 'New chat',
            messages: data.messages || [],
          },
        })
      }
    } catch (err) {
      console.error('Failed to load chat:', err)
      throw err
    }
  },

  async createNewChat() {
    try {
      const data = await chatService.createChat()
      if (data?.success) {
        const chat = {
          id: data.chat_id,
          title: data.title || 'New chat',
          messages: data.messages || [],
        }
        set((state) => ({
          chats: [chat, ...(state.chats || [])],
          activeChatId: chat.id,
          activeChat: chat,
        }))
      }
    } catch (err) {
      console.error('Failed to create new chat:', err)
      throw err
    }
  },

  async deleteChat(chatId) {
    try {
      await chatService.deleteChat(chatId)
      set((state) => ({
        chats: state.chats.filter((c) => c.id !== chatId),
        activeChatId: state.activeChatId === chatId ? null : state.activeChatId,
        activeChat: state.activeChat?.id === chatId ? null : state.activeChat,
      }))
    } catch (err) {
      console.error('Failed to delete chat:', err)
      throw err
    }
  },

  async submitMessage(text) {
    const trimmed = text?.trim()
    if (!trimmed) return

    const pdfStatus = usePdfStore.getState().pdfStatus
    let currentChatId = get().activeChatId

    if (!currentChatId) {
      await get().createNewChat()
      currentChatId = get().activeChatId
    }

    const loadingId = `loading-${Date.now()}`

    // Optimistically add user message + loading placeholder
    set((state) => ({
      activeChat: {
        ...state.activeChat,
        messages: [
          ...(state.activeChat?.messages || []),
          { sender: 'user', content: trimmed, domain: 'user' },
          { sender: 'bot', content: '', domain: 'loading', id: loadingId },
        ],
      },
    }))

    set({ isLoading: true, currentDomain: 'general' })

    try {
      if (pdfStatus?.loaded) {
        await chatService.postMessage(currentChatId, {
          sender: 'user',
          content: trimmed,
          domain: 'user',
        })

        const pdfResponse = await pdfService.askPdf(trimmed, pdfStatus.session_id)
        const botResp = pdfResponse.response || 'Unable to answer.'

        await chatService.postMessage(currentChatId, {
          sender: 'bot',
          content: botResp,
          domain: 'pdf',
          data: { answer: botResp },
        })

        await get().loadChat(currentChatId)
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.id === currentChatId
              ? { ...chat, title: chat.title || trimmed.slice(0, 40), updated_at: new Date().toISOString() }
              : chat,
          ),
        }))
      } else {
        const result = await chatService.sendMessage(trimmed, currentChatId)

        // Derive domain from the response for pipeline visibility
        const domain = result?.domain || 'general'
        set({ currentDomain: domain })

        if (result?.success) {
          const botMessage = {
            sender: 'bot',
            content: result.response || '',
            domain: domain,
            data: result.data || null,
            text: result.response || '',
          }

          // Replace the loading placeholder with the real bot message
          // or append fallback if no backend messages available
          set((state) => {
            const prevMessages = state.activeChat?.messages || []
            const filtered = prevMessages.filter((m) => m.id !== loadingId)

            // Prefer the backend-provided message list if it contains
            // both the user message and the bot answer.
            const backendMessages = result.messages
            const hasBackendMessages = Array.isArray(backendMessages) && backendMessages.length > 0

            const nextMessages = hasBackendMessages
              ? backendMessages
              : [...filtered, botMessage]

            return {
              activeChat: {
                ...state.activeChat,
                messages: nextMessages,
              },
              chats: state.chats.map((chat) =>
                chat.id === currentChatId
                  ? { ...chat, updated_at: new Date().toISOString() }
                  : chat,
              ),
            }
          })
        } else {
          // Replace loading with error message
          set((state) => ({
            activeChat: {
              ...state.activeChat,
              messages: (state.activeChat?.messages || []).filter((m) => m.id !== loadingId).concat({
                sender: 'bot',
                content: result?.error || 'Something went wrong. Please try again.',
                domain: 'general',
              }),
            },
          }))
        }
      }
    } catch (err) {
      set((state) => ({
        activeChat: {
          ...state.activeChat,
          messages: (state.activeChat?.messages || [])
            .filter((m) => m.id !== loadingId)
            .concat({
              sender: 'bot',
              content: 'Something went wrong. Please try again.',
              domain: 'general',
            }),
        },
      }))
      throw err
    } finally {
      set({ isLoading: false })
    }
  },
}))

export default useChatStore
