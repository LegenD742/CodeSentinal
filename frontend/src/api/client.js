import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

export const listRepositories = () => api.get("/repos").then((r) => r.data);
export const listPullRequests = (repoId) => api.get(`/repos/${repoId}/prs`).then((r) => r.data);
export const getPullRequest = (prId) => api.get(`/prs/${prId}`).then((r) => r.data);
export const listReviewRuns = (prId) => api.get(`/prs/${prId}/runs`).then((r) => r.data);
export const getReviewRun = (runId) => api.get(`/runs/${runId}`).then((r) => r.data);
export const getRunStatus = (runId) => api.get(`/runs/${runId}/status`).then((r) => r.data);
export const rerunReview = (prId) => api.post(`/runs/${prId}/rerun`).then((r) => r.data);
