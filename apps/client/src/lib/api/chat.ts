// Chat API functions
import axios from '@/lib/axios';

export interface Chat {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  messageCount?: number;
  lastMessage?: string;
}

export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'ai';
  createdAt: string;
  groundingScore?: number;
  retrievedChunks?: Array<{
    content: string;
    similarity: number;
    document_title: string;
    chunk_index: number;
  }>;
}

export interface ChatResponse {
  answer: string;
  sources: Array<{
    content: string;
    similarity: number;
    document_title: string;
    chunk_index: number;
  }>;
  messageId: string;
  groundingScore: number;
  chatId: string;
  responseTime: number;
  language: string;
  chunksRetrieved: number;
  createdNewChat: boolean;
}

// Chat Management
export async function getUserChats(limit = 20, offset = 0): Promise<{ 
  chats: Chat[]; 
  pagination: PaginationMeta;
}> {
  const response = await axios.get('/chat/', {
    params: { limit, offset }
  });
  return response.data;
}

export async function getChatDetails(chatId: string, limit = 50, offset = 0): Promise<{
  chat: Chat;
  messages: Message[];
  pagination: PaginationMeta;
}> {
  // Get chat messages from the backend
  const response = await axios.get(`/chat/${chatId}/messages`, {
    params: { limit, offset }
  });
  const messages = response.data.messages;

  // Create a mock chat object since the backend doesn't return chat details directly
  const chat: Chat = {
    id: chatId,
    name: messages.length > 0 ? `Chat ${new Date(messages[0].createdAt).toLocaleDateString()}` : 'New Chat',
    created_at: messages.length > 0 ? messages[0].createdAt : new Date().toISOString(),
    updated_at: messages.length > 0 ? messages[messages.length - 1].createdAt : new Date().toISOString(),
    messageCount: messages.length,
    lastMessage: messages.length > 0 ? messages[messages.length - 1].content : undefined,
  };

  return {
    chat,
    messages,
    pagination: response.data.pagination || {
      total: messages.length,
      limit,
      offset,
      hasMore: false
    }
  };
}

export async function deleteChat(chatId: string): Promise<void> {
  await axios.delete(`/chat/${chatId}`);
}

// RAG Chat
export async function sendMessage(
  content: string,
  chatId?: string,
  files?: File[]
): Promise<ChatResponse> {
  // Create FormData since the backend expects form data
  const formData = new FormData();
  formData.append('content', content);

  if (chatId) {
    formData.append('chat_id', chatId);
  }

  if (files && files.length > 0) {
    files.forEach((file) => {
      formData.append('files', file);
    });
  }

  const response = await axios.post('/chat/message', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  // Transform the backend response to match our interface
  const backendResponse = response.data;

  return {
    answer: backendResponse.message.content,
    sources: backendResponse.rag_metadata?.sources || [],
    messageId: backendResponse.message.id || `msg-${Date.now()}`,
    groundingScore: backendResponse.rag_metadata?.confidence || 0,
    chatId: backendResponse.chat_id,
    responseTime: backendResponse.rag_metadata?.response_time || 0,
    language: backendResponse.rag_metadata?.language || 'en',
    chunksRetrieved: backendResponse.rag_metadata?.chunks_retrieved || 0,
    createdNewChat: backendResponse.created_new_chat || false,
  };
}

// Chat History
export async function getChatHistory(chatId: string, limit = 50, offset = 0): Promise<{
  messages: Message[];
  pagination: PaginationMeta;
}> {
  const response = await axios.get(`/chat/${chatId}/messages`, {
    params: { limit, offset }
  });
  return {
    messages: response.data.messages,
    pagination: response.data.pagination || {
      total: response.data.messages.length,
      limit,
      offset,
      hasMore: false
    }
  };
}

// Feedback
export async function submitFeedback(
  messageId: string,
  feedback: 'helpful' | 'not_helpful' | 'partial'
): Promise<void> {
  await axios.post('/rag/feedback', {
    message_id: messageId,
    feedback,
  });
}

export default {
  getUserChats,
  getChatDetails,
  deleteChat,
  sendMessage,
  getChatHistory,
  submitFeedback,
};
