import { api } from '../../../services/api';

export const chatWithRagApi = (payload) => {
  return api.post(
    'http://localhost:6007/chat-with-rag?message=' + payload,
    payload,
  );
};
