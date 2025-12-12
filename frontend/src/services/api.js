import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Workflows API
export const fetchWorkflows = async (teamId) => {
  const response = await api.get(`/workflows/${teamId}/workflows`);
  return response.data;
};

export const runInference = async (teamId) => {
  const response = await api.post(`/workflows/${teamId}/infer`);
  return response.data;
};

export const fetchSOP = async (teamId, workflowId = null) => {
  const url = workflowId 
    ? `/workflows/${teamId}/sop?workflow_id=${workflowId}`
    : `/workflows/${teamId}/sop`;
  const response = await api.get(url);
  return response.data;
};

export const searchWorkflows = async (teamId, query, limit = 10) => {
  const response = await api.get(`/workflows/${teamId}/search`, {
    params: { query, limit }
  });
  return response.data;
};

// Automations API
export const runAutomation = async (teamId, workflowId, parameters = null) => {
  const response = await api.post(`/automations/${teamId}/run/${workflowId}`, parameters);
  return response.data;
};

export const getAutomationHistory = async (teamId, limit = 50) => {
  const response = await api.get(`/automations/${teamId}/history`, {
    params: { limit }
  });
  return response.data;
};

export const scheduleAutomation = async (teamId, workflowId, schedule, parameters = null) => {
  const response = await api.post(`/automations/${teamId}/schedule/${workflowId}`, parameters, {
    params: { schedule }
  });
  return response.data;
};

// Integrations API
export const fetchSlackEvents = async (token, channels) => {
  const response = await api.get('/integrations/slack', {
    params: { token, channels }
  });
  return response.data;
};

export const fetchJiraIssues = async (apiKey, project) => {
  const response = await api.get('/integrations/jira', {
    params: { api_key: apiKey, project }
  });
  return response.data;
};

export const fetchGmailThreads = async (credentials, label = 'INBOX') => {
  const response = await api.get('/integrations/gmail', {
    params: { credentials, label }
  });
  return response.data;
};

export const uploadCSV = async (teamId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/integrations/csv/upload`, formData, {
    params: { team_id: teamId },
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export default api;
