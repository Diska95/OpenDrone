import client from './client'

export const authApi = {
  register: (data) => client.post('/auth/register/', data),
  login: (email, password) => client.post('/auth/login/', { email, password }),
  logout: (refresh) => client.post('/auth/logout/', { refresh }),
  getMe: () => client.get('/auth/me/'),
  updateMe: (data) => client.patch('/auth/me/', data),
  changePassword: (data) => client.post('/auth/me/password/', data),
}
