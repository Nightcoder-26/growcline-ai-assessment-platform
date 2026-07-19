import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/expenses';

export const expenseService = {
  getAll: async () => {
    const response = await axios.get(API_URL);
    return response.data;
  },
  
  create: async (description, amount) => {
    const response = await axios.post(API_URL, {
      description,
      amount: parseFloat(amount),
      category: 'General'
    });
    return response.data;
  },

  delete: async (id) => {
    await axios.delete(`${API_URL}/${id}`);
  },

  update: async (id, description, amount) => {
    const response = await axios.put(`${API_URL}/${id}`, {
      description,
      amount: parseFloat(amount),
      category: 'General'
    });
    return response.data;
  }
};
