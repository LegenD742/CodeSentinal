-- CodeSentinel database schema
-- Run automatically by the postgres container on first init (docker-entrypoint-initdb.d).

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS installations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    github_installation_id BIGINT UNIQUE NOT NULL,
    account_login VARCHAR(255) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    github_repo_id BIGINT UNIQUE NOT NULL,
    full_name VARCHAR(255) UNIQUE NOT NULL,
    default_branch VARCHAR(100) NOT NULL DEFAULT 'main',
    installation_id BIGINT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_repositories_full_name ON repositories (full_name);

CREATE TABLE IF NOT EXISTS pull_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    github_pr_number INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    author_login VARCHAR(255) NOT NULL,
    base_branch VARCHAR(255) NOT NULL,
    head_branch VARCHAR(255) NOT NULL,
    head_sha VARCHAR(64) NOT NULL,
    state VARCHAR(20) NOT NULL DEFAULT 'open',
    additions INTEGER NOT NULL DEFAULT 0,
    deletions INTEGER NOT NULL DEFAULT 0,
    changed_files INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repository_id, github_pr_number)
);
CREATE INDEX IF NOT EXISTS idx_pr_repo ON pull_requests (repository_id);

CREATE TABLE IF NOT EXISTS review_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pull_request_id UUID NOT NULL REFERENCES pull_requests(id) ON DELETE CASCADE,
    trigger_sha VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'queued',
    risk_score FLOAT,
    risk_level VARCHAR(20),
    verdict_action VARCHAR(20),
    summary TEXT,
    agent_trace JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER
);
CREATE INDEX IF NOT EXISTS idx_runs_pr ON review_runs (pull_request_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON review_runs (status);

CREATE TABLE IF NOT EXISTS findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_run_id UUID NOT NULL REFERENCES review_runs(id) ON DELETE CASCADE,
    source_agent VARCHAR(30) NOT NULL,
    category VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    confidence INTEGER NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    title VARCHAR(300) NOT NULL,
    explanation TEXT NOT NULL,
    evidence TEXT NOT NULL,
    suggested_fix TEXT,
    suggested_patch TEXT,
    tool_origin VARCHAR(50),
    rule_id VARCHAR(200),
    critic_verdict VARCHAR(20),
    critic_reasoning TEXT,
    is_posted_to_github BOOLEAN NOT NULL DEFAULT FALSE,
    github_comment_id INTEGER,
    metadata_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_findings_run ON findings (review_run_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings (severity);

CREATE TABLE IF NOT EXISTS code_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_path VARCHAR(1000) NOT NULL,
    commit_sha VARCHAR(64) NOT NULL,
    chunk_index INTEGER NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    symbol_name VARCHAR(300),
    content TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_embeddings_repo ON code_embeddings (repository_id);
-- Approximate nearest-neighbour index (IVFFlat) for cosine similarity search.
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON code_embeddings
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
