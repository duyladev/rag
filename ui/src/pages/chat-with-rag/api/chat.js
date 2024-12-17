import { api } from '../../../services/api';

export const chatWithRagApi = (payload) => {
  return api.post(
    'http://localhost:6007/query-with-rag?query_str=' + payload,
    payload,
  );
};
