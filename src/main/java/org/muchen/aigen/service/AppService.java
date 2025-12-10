package org.muchen.aigen.service;

import com.mybatisflex.core.query.QueryWrapper;
import com.mybatisflex.core.service.IService;
import org.muchen.aigen.model.dto.app.AppAddRequest;
import org.muchen.aigen.model.dto.app.AppDeployRequest;
import org.muchen.aigen.model.dto.app.AppQueryRequest;
import org.muchen.aigen.model.dto.app.AppVO;
import org.muchen.aigen.model.entity.App;
import org.muchen.aigen.model.entity.User;
import reactor.core.publisher.Flux;

import java.util.List;

/**
 * 应用 服务层。
 *
 * @author Muchen
 */
public interface AppService extends IService<App> {

    Long createApp(AppAddRequest appAddRequest, User loginUser);

    AppVO getAppVO(App app);

    QueryWrapper getQueryWrapper(AppQueryRequest appQueryRequest);

    List<AppVO> getAppVOList(List<App> appList);

    /**
     * 通过对话生成应用代码
     *
     * @param appId 应用id
     * @param message 提示词
     * @param loginUser 登录用户
     * @return 流式返回
     */
    Flux<String> chatToGenCode(Long appId, String message , User loginUser);


    String deployApp(Long appId, User loginUser);

    void generateAppScreenshotAsync(Long appId, String appUrl);
}
