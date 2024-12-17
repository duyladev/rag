import { api } from '../../../services/api';

export const chatApi = (payload) => {
  return api.post('http://localhost:6007/query?query_str=' + payload, payload);
};
