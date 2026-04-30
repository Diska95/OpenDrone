import client from './client'

export const ordersApi = {
  createOrder: (data) => client.post('/orders/create/', data),
  getOrders: () => client.get('/orders/'),
  getOrder: (id) => client.get(`/orders/${id}/`),
  updateStatus: (id, data) => client.patch(`/orders/${id}/status/`, data),
  openDispute: (id, data) => client.post(`/orders/${id}/dispute/`, data),
}
