package org.muchen.aigen.core;

import cn.hutool.core.io.FileUtil;
import cn.hutool.core.util.IdUtil;
import cn.hutool.core.util.StrUtil;
import org.muchen.aigen.ai.model.HtmlCodeResult;
import org.muchen.aigen.ai.model.MultiFileCodeResult;
import org.muchen.aigen.model.enums.CodeGenTypeEnum;

import java.io.File;
import java.nio.charset.StandardCharsets;

/**
 * 文件保存器
 *
 */
@Deprecated
public class CodeFileSaver {

    //文件保存根目录
    private static final String FILE_SAVE_ROOT_DIR = System.getProperty("user.dir") + File.separator + "tmp" + File.separator + "code_outPut";

    /**
     * 保存HTML文件
     *
     * HtmlCodeResult
     * @param htmlCodeResult HtmlCodeResult结果
     * @return 文件
     */
    public  static File saveHtmlCodeResult(HtmlCodeResult htmlCodeResult) {
        String baseDirPath = buildUniqueDir(CodeGenTypeEnum.HTML.getValue());
        writeToFile(baseDirPath,"index.html",htmlCodeResult.getHtmlCode());
        return new File(baseDirPath);
    }

    /**
     * 保存多文件代码
     *
     * @param result MultiFileCodeResult结果
     * @return 文件
     */
    public static File saveMultiFileCodeResult(MultiFileCodeResult result) {
        String baseDirPath = buildUniqueDir(CodeGenTypeEnum.MULTI_FILE.getValue());
        writeToFile(baseDirPath, "index.html", result.getHtmlCode());
        writeToFile(baseDirPath, "style.css", result.getCssCode());
        writeToFile(baseDirPath, "script.js", result.getJsCode());
        return new File(baseDirPath);
    }

    /**
     * 构建完文件唯一路径
     *
     * @param bizType 代码生成类型
     * @return 文件唯一路径名
     */
    private static String buildUniqueDir(String bizType) {
        String uniqueDirName = StrUtil.format("{}_{}", bizType, IdUtil.getSnowflakeNextIdStr());
        String dirPath = FILE_SAVE_ROOT_DIR + File.separator + uniqueDirName;
        FileUtil.mkdir(dirPath);
        return dirPath;
    }

    /**
     * 保存单个文件
     *
     * @param dirPath 文件位置
     * @param fileName 文件名称
     * @param content 文件内容
     */
    public static void writeToFile(String dirPath, String fileName,String content ) {
        String filePath = dirPath + File.separator+fileName;
        FileUtil.writeString(content,filePath, StandardCharsets.UTF_8);
    }

}

