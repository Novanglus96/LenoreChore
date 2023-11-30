import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: false,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
})

export default {
    createAreaGroup(newAreaGroup) {
        return apiClient.post('/areagroups/', newAreaGroup)
    },
    updateAreaGroup(updatedAreaGroup) {
        return apiClient.put('/areagroups/' + updatedAreaGroup.id, updatedAreaGroup)
    },
    deleteAreaGroup(deletedAreaGroup) {
        return apiClient.delete('/areagroups/' + deletedAreaGroup.id)
    },
    getAreaGroups() {
        return apiClient.get('/areagroups/')
    }
}