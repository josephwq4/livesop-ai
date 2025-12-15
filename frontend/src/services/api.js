import axios from 'axios';
import { supabase } from '../lib/supabase';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Authorization Header to every request
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();

  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }

  return config;
});

// Workflows API
export const fetchWorkflows = async (teamId, workflowId = null) => {
  let url = `/workflows/${teamId}/workflows`;
  if (workflowId) url += `?workflow_id=${workflowId}`;

  const response = await api.get(url);
  return response.data;
};

export const fetchWorkflowHistory = async (teamId) => {
  const response = await api.get(`/workflows/${teamId}/history`);
  return response.data;
};

export const searchKnowledge = async (teamId, query) => {
  const response = await api.get(`/workflows/${teamId}/search?q=${encodeURIComponent(query)}`);
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

export const updateNode = async (teamId, nodeId, payload) => {
  const response = await api.patch(`/workflows/${teamId}/nodes/${nodeId}`, payload);
  return response.data;
};

// Automations API
export const runAutomation = async (teamId, payload) => {
  const response = await api.post(`/automations/${teamId}/execute`, payload);
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

export const getTeamUsage = async () => {
  const response = await api.get('/usage/');
  return response.data;
};

export const getLiveFeed = async (teamId) => {
  const response = await api.get(`/automations/${teamId}/live_feed`);
  return response.data;
};

export default api;
