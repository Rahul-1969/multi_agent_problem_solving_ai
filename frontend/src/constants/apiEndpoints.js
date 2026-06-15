export const CHAT = '/chat'
export const CHATS = '/chats'
export const LOGIN = '/auth/login'
export const REFRESH = '/auth/refresh'
export const REGISTER = '/auth/register'
export const PDF_LOAD = '/pdf/load'
export const PDF_UPLOAD = '/pdf/upload'
export const PDF_ASK = '/pdf/ask'
export const PDF_STATUS = '/pdf/status'
export const PDF_CLEAR = '/pdf/clear'
export const CHAT_MESSAGES = (chatId) => `/chats/${chatId}/messages`
export const CHAT_DETAIL = (chatId) => `/chats/${chatId}`
