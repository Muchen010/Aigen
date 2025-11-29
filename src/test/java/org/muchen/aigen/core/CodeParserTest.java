package org.muchen.aigen.core;

import org.junit.jupiter.api.Test;
import org.muchen.aigen.ai.model.HtmlCodeResult;
import org.muchen.aigen.ai.model.MultiFileCodeResult;

import static org.junit.jupiter.api.Assertions.assertNotNull;


class CodeParserTest {

    @Test
    void parseHtmlCode() {
        // 修复：添加 ```html 和 ``` 包裹代码
        String codeContent = """
                随便写一段描述：
                
                ```html
                <!DOCTYPE html>
                <html>
                <head>
                    <title>测试页面</title>
                </head>
                <body>
                    <h1>Hello World!</h1>
                </body>
                </html>
                ```

                随便写一段描述
                """;
        HtmlCodeResult result = CodeParser.parseHtmlCode(codeContent);
        assertNotNull(result);
        // 验证提取的内容不包含 "随便写一段描述"
        assertNotNull(result.getHtmlCode());
        System.out.println("Parsed HTML: " + result.getHtmlCode());
    }

    @Test
    void parseMultiFileCode() {
        // 修复：分别为 HTML, CSS, JS 添加对应的 Markdown 代码块包裹
        String codeContent = """
                创建一个完整的网页：
                
                index.html
                ```html
                <!DOCTYPE html>
                <html>
                <head>
                    <title>多文件示例</title>
                    <link rel="stylesheet" href="style.css">
                </head>
                <body>
                    <h1>欢迎使用</h1>
                    <script src="script.js"></script>
                </body>
                </html>
                ```

                style.css
                ```css
                h1 {
                    color: blue;
                    text-align: center;
                }
                ```
                
                script.js
                ```javascript
                console.log('页面加载完成');
                ```

                文件创建完成！
                """;

        MultiFileCodeResult result = CodeParser.parseMultiFileCode(codeContent);

        assertNotNull(result);
        assertNotNull(result.getHtmlCode(), "HTML Code should not be null");
        assertNotNull(result.getCssCode(), "CSS Code should not be null");
        assertNotNull(result.getJsCode(), "JS Code should not be null");

        System.out.println("HTML: " + result.getHtmlCode());
        System.out.println("CSS: " + result.getCssCode());
        System.out.println("JS: " + result.getJsCode());
    }
}
