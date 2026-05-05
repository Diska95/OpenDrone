import client from './client'

export const adminApi = {
  // dashboard
  getStats: () => client.get('/dashboard/admin/'),
  // projects
  getAllProjects: (statusFilter) => client.get('/projects/admin/all/', { params: statusFilter ? { status: statusFilter } : {} }),
  getPendingProjects: () => client.get('/projects/admin/pending/'),
  approveProject: (slug) => client.post(`/projects/${slug}/approve/`),
  rejectProject: (slug, reason = '') => client.post(`/projects/${slug}/reject/`, { reason }),
  archiveProject: (slug) => client.post(`/projects/${slug}/archive/`),
  unarchiveProject: (slug) => client.post(`/projects/${slug}/unarchive/`),
  hardDeleteProject: (slug) => client.delete(`/projects/${slug}/`),
  getArchivedProjects: () => client.get('/projects/admin/archived/'),
  // users
  getUsers: (params = {}) => client.get('/auth/admin/users/', { params }),
  updateUser: (id, data) => client.patch(`/auth/admin/users/${id}/`, data),
}
