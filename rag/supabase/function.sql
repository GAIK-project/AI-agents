CREATE OR REPLACE FUNCTION find_similar_documents(
  query_embedding VECTOR(1536),
  similarity_threshold FLOAT DEFAULT 0.7,
  max_results INT DEFAULT 5
) 
RETURNS TABLE (
  id INT,
  title TEXT,
  content TEXT,
  metadata JSONB,
  similarity FLOAT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
) 
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.title,
    d.content,
    d.metadata,
    1 - (d.embedding <=> query_embedding) as similarity,
    d.created_at,
    d.updated_at
  FROM
    documents d
  WHERE
    1 - (d.embedding <=> query_embedding) > similarity_threshold
  ORDER BY
    d.embedding <=> query_embedding
  LIMIT max_results;
END;
$$;