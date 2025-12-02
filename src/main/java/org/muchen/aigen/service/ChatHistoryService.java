package org.muchen.aigen.service;

import com.mybatisflex.core.paginate.Page;
import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.service.IService;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import org.muchen.aigen.model.dto.chathistory.ChatHistoryQueryRequest;
import org.muchen.aigen.model.entity.ChatHistory;
import org.muchen.aigen.model.entity.User;

import java.time.LocalDateTime;

/**
 * 对话历史 服务层。
 *
 * @author Muchen
 */
public interface ChatHistoryService extends IService<ChatHistory> {

    boolean addChatMessage(Long appId, String message, String messageType, Long userId);

    boolean deleteByAppId(Long appId);

    QueryWrapper getQueryWrapper(ChatHistoryQueryRequest chatHistoryQueryRequest);

    Page<ChatHistory> listAppChatHistoryByPage(Long appId, int pageSize,
                                               LocalDateTime lastCreateTime,
                                               User loginUser);

    int loadChatHistoryToMemory(Long appId, MessageWindowChatMemory chatMemory, int maxCount);
}
