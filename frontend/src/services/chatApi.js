import API from './api'

export async function getChats() {
  return API.get('/chats')
}

export async function getChat(chatId) {
  return API.get(`/chats/${chatId}`)
}

export async function createChat(title = 'New chat') {
  return API.post('/chats', { title })
}

export async function deleteChat(chatId) {
  return API.delete(`/chats/${chatId}`)
}

export async function postMessage(chatId, message) {
  return API.post(`/chats/${chatId}/messages`, message)
}

export async function sendChatQuery(payload) {
  return API.post('/chat', payload)
}
