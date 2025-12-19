package org.muchen.aigen.langgraph4j.node;

import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;
import dev.langchain4j.store.embedding.EmbeddingStore;
import lombok.extern.slf4j.Slf4j;
import org.bsc.langgraph4j.action.AsyncNodeAction;
import org.bsc.langgraph4j.prebuilt.MessagesState;
import org.muchen.aigen.langgraph4j.state.WorkflowContext;
import org.muchen.aigen.langgraph4j.utils.SpringContextUtil;

import java.util.List;
import java.util.stream.Collectors;

import static org.bsc.langgraph4j.action.AsyncNodeAction.node_async;

@Slf4j
public class KnowledgeRetrievalNode {

    private static final int MAX_RESULTS = 3;
    private static final double MIN_SCORE = 0.7;

    public static AsyncNodeAction<MessagesState<String>> create() {
        return node_async(state -> {
            WorkflowContext context = WorkflowContext.getContext(state);
            log.info("🚀 执行节点: 知识检索 (RAG)");

            // 1. 安全获取 Bean
            EmbeddingStore<TextSegment> embeddingStore;
            EmbeddingModel embeddingModel;

            try {
                // 尝试获取，如果 Config 里没开启(@ConditionalOnProperty不成立)，这里会抛异常
                embeddingStore = SpringContextUtil.getBean(EmbeddingStore.class);
                embeddingModel = SpringContextUtil.getBean(EmbeddingModel.class);
            } catch (Exception e) {
                log.warn("⚠️ RAG 组件未启用或未配置，跳过知识检索步骤。提示: 如需启用请在 yml 设置 aigen.rag.enabled=true");
                context.setCurrentStep("知识检索(跳过)");
                return WorkflowContext.saveContext(context);
            }

            // 2. 执行检索
            try {
                String queryText = context.getOriginalPrompt();

                // A. Embedding
                Embedding queryEmbedding = embeddingModel.embed(queryText).content();

                // B. Search
                EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                        .queryEmbedding(queryEmbedding)
                        .maxResults(MAX_RESULTS)
                        .minScore(MIN_SCORE)
                        .build();

                EmbeddingSearchResult<TextSegment> result = embeddingStore.search(request);
                List<EmbeddingMatch<TextSegment>> matches = result.matches();

                if (matches.isEmpty()) {
                    log.info("📭 未检索到相关知识库内容");
                    context.setRetrievedKnowledge("");
                } else {
                    // C. 格式化
                    String knowledgeBlock = matches.stream()
                            .map(match -> match.embedded().text())
                            .collect(Collectors.joining("\n\n"));

                    log.info("✅ 成功检索到 {} 条相关知识", matches.size());
                    context.setRetrievedKnowledge(knowledgeBlock);
                }

            } catch (Exception e) {
                // 兜底：数据库连接失败、超时等，不中断流程
                log.error("❌ 知识检索运行异常 (已降级为普通生成): {}", e.getMessage());
                context.setRetrievedKnowledge("");
            }

            context.setCurrentStep("知识检索");
            return WorkflowContext.saveContext(context);
        });
    }
}