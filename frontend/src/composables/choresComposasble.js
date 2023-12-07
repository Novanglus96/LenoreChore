import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v2',
  withCredentials: false,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
})