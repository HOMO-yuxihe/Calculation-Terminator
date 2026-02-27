# src/calcterm/__main__.py
import sys
import traceback
sys.path.append('src')
from PyQt5.QtWidgets import QApplication,QMessageBox
from calcterm.app.main_window import MainWindow

def setup_exception_hook():
    # 保存原始的异常钩子
    original_excepthook = sys.excepthook

    def custom_excepthook(exc_type, exc_value, exc_traceback):
        # 排除键盘中断（Ctrl+C）
        if issubclass(exc_type, KeyboardInterrupt):
            original_excepthook(exc_type, exc_value, exc_traceback)
            return
        
        # 拼接详细的异常信息（含堆栈）
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        # 弹出错误提示框
        QMessageBox.critical(None, '程序异常', f'发生错误：\n{error_msg}')
        # 调用原始钩子（可选，保留控制台输出）
        original_excepthook(exc_type, exc_value, exc_traceback)

    # 设置自定义钩子
    sys.excepthook = custom_excepthook

def main():
    # 先设置自定义异常钩子
    setup_exception_hook()
    
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        # 捕获初始化阶段的异常（比如创建窗口时的错误）
        error_msg = f"程序初始化失败：\n{str(type(e))}: {str(e)}"
        QMessageBox.critical(None, '发生错误', error_msg)

if __name__ == "__main__":
    main()