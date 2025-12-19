package org.muchen.aigen.config;

import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.pgvector.PgVectorEmbeddingStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RagConfiguration {

    // ... 你的 @Value 属性保持不变 ...
    @Value("${aigen.rag.pgvector.host:localhost}")
    private String host;
    @Value("${aigen.rag.pgvector.port:5432}")
    private Integer port;
    @Value("${aigen.rag.pgvector.database:aigen}")
    private String database;
    @Value("${aigen.rag.pgvector.user:postgres}")
    private String user;
    @Value("${aigen.rag.pgvector.password:password}")
    private String password;
    @Value("${aigen.rag.pgvector.table:embeddings}")
    private String table;
    @Value("${aigen.rag.pgvector.schema:aigen_rag}")
    private String schema;

    @Bean
    @ConditionalOnProperty(prefix = "aigen.rag", name = "enabled", havingValue = "true")
    public EmbeddingStore<TextSegment> embeddingStore() {
        return PgVectorEmbeddingStore.builder()
                .host(host)
                .port(port)
                .database(database)
                .user(user)
                .password(password)
                .table(table)
                //.schema(schema)
                .dimension(1536)
                .useIndex(true)
                .build();
    }
}