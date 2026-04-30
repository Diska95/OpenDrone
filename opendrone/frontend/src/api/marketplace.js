import client from './client'

export const marketplaceApi = {
  getProjects: (params = {}) => client.get('/projects/', { params }),
  getProject: (slug) => client.get(`/projects/${slug}/`),
  createProject: (data) => client.post('/projects/', data),
  updateProject: (slug, data) => client.patch(`/projects/${slug}/`, data),
  publishProject: (slug) => client.post(`/projects/${slug}/publish/`),
  approveProject: (slug) => client.post(`/projects/${slug}/approve/`),
  rejectProject: (slug, reason = '') => client.post(`/projects/${slug}/reject/`, { reason }),
  getPendingProjects: () => client.get('/projects/admin/pending/'),
  forkProject: (slug) => client.post(`/projects/${slug}/fork/`),
  getMyProjects: () => client.get('/projects/my/'),
  getCategories: () => client.get('/projects/categories/'),
  getBrands: (category) => client.get('/projects/brands/', { params: category ? { category } : {} }),
  uploadFile: (slug, formData) => client.post(`/projects/${slug}/files/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getBOM: (slug) => client.get(`/projects/${slug}/bom/`),
  addBOMItem: (slug, data) => client.post(`/projects/${slug}/bom/`, data),
  getReviews: (slug) => client.get(`/projects/${slug}/reviews/`),
  addReview: (slug, data) => client.post(`/projects/${slug}/reviews/`, data),
}
