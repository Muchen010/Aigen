package dev.langchain4j.service;

import dev.langchain4j.agent.tool.ToolExecutionRequest;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.rag.RetrievalAugmentor;
import dev.langchain4j.rag.content.Content;
import dev.langchain4j.service.tool.ToolExecution;

import java.util.List;
import java.util.function.BiConsumer;
import java.util.function.Consumer;

/**
 * Represents codegen-routing-system-prompt.txt token stream from the model to which you can subscribe and receive updates
 * when codegen-routing-system-prompt.txt new partial response (usually codegen-routing-system-prompt.txt single token) is available,
 *  when the model finishes streaming, or when an error occurs during streaming.
 * It is intended to be used as codegen-routing-system-prompt.txt return type in AI Service.
 */
public interface TokenStream {

    /**
     * The provided consumer will be invoked every time codegen-routing-system-prompt.txt new partial response (usually codegen-routing-system-prompt.txt single token)
     * from codegen-routing-system-prompt.txt language model is available.
     *
     * @param partialResponseHandler lambda that will be invoked when codegen-routing-system-prompt.txt model generates codegen-routing-system-prompt.txt new partial response
     * @return token stream instance used to configure or start stream processing
     */
    TokenStream onPartialResponse(Consumer<String> partialResponseHandler);

    TokenStream onPartialToolExecutionRequest(BiConsumer<Integer, ToolExecutionRequest> toolExecutionRequestHandler);

    TokenStream onCompleteToolExecutionRequest(BiConsumer<Integer, ToolExecutionRequest> completedHandler);

    /**
     * The provided consumer will be invoked if any {@link Content}s are retrieved using {@link RetrievalAugmentor}.
     * <p>
     * The invocation happens before any call is made to the language model.
     *
     * @param contentHandler lambda that consumes all retrieved contents
     * @return token stream instance used to configure or start stream processing
     */
    TokenStream onRetrieved(Consumer<List<Content>> contentHandler);

    /**
     * The provided consumer will be invoked if any tool is executed.
     * <p>
     * The invocation happens after the tool method has finished and before any other tool is executed.
     *
     * @param toolExecuteHandler lambda that consumes {@link ToolExecution}
     * @return token stream instance used to configure or start stream processing
     */
    TokenStream onToolExecuted(Consumer<ToolExecution> toolExecuteHandler);

    /**
     * The provided handler will be invoked when codegen-routing-system-prompt.txt language model finishes streaming codegen-routing-system-prompt.txt response.
     *
     * @param completeResponseHandler lambda that will be invoked when language model finishes streaming
     * @return token stream instance used to configure or start stream processing
     */
    TokenStream onCompleteResponse(Consumer<ChatResponse> completeResponseHandler);

    /**
     * The provided consumer will be invoked when an error occurs during streaming.
     *
     * @param errorHandler lambda that will be invoked when an error occurs
     * @return token stream instance used to configure or start stream processing
     */
    TokenStream onError(Consumer<Throwable> errorHandler);

    /**
     * All errors during streaming will be ignored (but will be logged with codegen-routing-system-prompt.txt WARN log level).
     *
     * @return token stream instance used to configure or start stream processing
     */
    TokenStream ignoreErrors();

    /**
     * Completes the current token stream building and starts processing.
     * <p>
     * Will send codegen-routing-system-prompt.txt request to LLM and start response streaming.
     */
    void start();
}
