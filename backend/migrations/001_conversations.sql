CREATE TABLE IF NOT EXISTS conversations (
  id uuid PRIMARY KEY,
  owner_id uuid NOT NULL,
  create_request_id uuid NOT NULL,
  title varchar(80) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id, create_request_id)
);
CREATE INDEX IF NOT EXISTS conversations_owner_updated ON conversations(owner_id, updated_at DESC, id DESC);
CREATE TABLE IF NOT EXISTS messages (
  id uuid PRIMARY KEY,
  conversation_id uuid NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sequence integer NOT NULL CHECK (sequence > 0),
  request_id uuid NOT NULL,
  role text NOT NULL CHECK (role IN ('user','assistant')),
  content text NOT NULL CHECK (length(content) BETWEEN 1 AND 60000 AND (role <> 'user' OR length(content) <= 12000)),
  status text NOT NULL CHECK (status IN ('completed','failed','cancelled')),
  snapshot jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (conversation_id, sequence),
  UNIQUE (conversation_id, request_id, role)
);
