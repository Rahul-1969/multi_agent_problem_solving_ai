import apiService from './apiService'
import { CHAT, CHATS, CHAT_MESSAGES, CHAT_DETAIL } from '../constants/apiEndpoints'
import { mapChatResponse } from '../utils/responseMapper'

const chatService = {
  async fetchChats() {
    const response = await apiService.get(CHATS)
    const payload = response.data
    if (Array.isArray(payload)) {
      return { success: true, chats: payload }
    }
    return {
      success: payload.success === true,
      chats: payload.chats || [],
      ...payload,
    }
  },

  async fetchChat(chatId) {
    const response = await apiService.get(CHAT_DETAIL(chatId))
    return response.data
  },

  async createChat(title = 'New chat') {
    const response = await apiService.post(CHATS, { title })
    return response.data
  },

  async deleteChat(chatId) {
    const response = await apiService.delete(CHAT_DETAIL(chatId))
    return response.data
  },

  async postMessage(chatId, message) {
    const response = await apiService.post(CHAT_MESSAGES(chatId), message)
    return response.data
  },

  async sendMessage(message, chatId = null, useRag = false) {
    const payload = { message, use_rag: useRag }
    if (chatId) {
      payload.chat_id = chatId
    }
    const response = await apiService.post(CHAT, payload)
    const mapped = mapChatResponse(response)
    return {
      ...mapped,
      messages: response.data?.messages ?? null,
      chat_title: response.data?.chat_title ?? null,
      raw: response.data,
    }
  },

  async askCoding(message) {
    return this.sendMessage(message)
  },

  async askEducation(message) {
    return this.sendMessage(message)
  },

  async askMedical(message) {
    return this.sendMessage(message)
  },

  async predictCollege(message) {
    return this.sendMessage(message)
  },
}

export default chatService
