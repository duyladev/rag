import { api } from '../../../services/api';

export const chatApi = (payload) => {
  return api.post(
    'http://localhost:6007/chat-with-llm?message=' + payload,
    payload,
  );
};
