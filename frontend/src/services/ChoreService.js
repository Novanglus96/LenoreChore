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
    },
    createArea(newArea) {
        return apiClient.post('/areas/', newArea)
    },
    updateArea(updatedArea) {
        return apiClient.put('/areas/' + updatedArea.id, updatedArea)
    },
    deleteArea(deletedArea) {
        return apiClient.delete('/areas/' + deletedArea.id)
    },
    getAreas() {
        return apiClient.get('/options/')
    },
    createOption(newOption) {
        return apiClient.post('/options/', newOption)
    },
    updateOption(updatedOption) {
        return apiClient.put('/options/' + updatedOption.id, updatedOption)
    },
    deleteOption(deletedOption) {
        return apiClient.delete('/options/' + deletedOption.id)
    },
    getOptions() {
        console.log('I ran!')
        return apiClient.get('/options/1/')
    }
}