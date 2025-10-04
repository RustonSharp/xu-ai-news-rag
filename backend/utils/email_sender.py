import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 修改: 使用相对导入代替绝对导入
from .logging_config import app_logger


class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """
        初始化邮件发送器
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP服务器端口
            username: 邮箱用户名
            password: 邮箱密码或授权码
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_emails: 收件人邮箱列表
            subject: 邮件主题
            body: 邮件正文
            is_html: 是否为HTML格式邮件，默认为False
            cc_emails: 抄送邮箱列表，可选
            bcc_emails: 密送邮箱列表，可选
            attachments: 附件路径列表，可选
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件对象
            message = MIMEMultipart()
            message["From"] = self.username
            message["To"] = ", ".join(to_emails)
            message["Subject"] = subject
            
            # 添加抄送
            if cc_emails:
                message["Cc"] = ", ".join(cc_emails)
                to_emails.extend(cc_emails)
            
            # 添加正文
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as file:
                            part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                        message.attach(part)
                    else:
                        app_logger.warning(f"Attachment file not found: {file_path}")
            
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.username, self.password)
                
                # 收件人列表包括密送
                all_recipients = to_emails.copy()
                if bcc_emails:
                    all_recipients.extend(bcc_emails)
                
                server.sendmail(self.username, all_recipients, message.as_string())
            
            app_logger.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            app_logger.error(f"Failed to send email: {str(e)}")
            return False


def get_email_sender() -> EmailSender:
    """
    从环境变量获取邮件发送器实例
    
    Returns:
        EmailSender: 邮件发送器实例
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    
    if not username or not password:
        raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD must be set in environment variables. 注意：EMAIL_PASSWORD 应该是邮箱的SMTP授权码，而不是登录密码")
    
    return EmailSender(smtp_server, smtp_port, username, password)


def send_notification_email(
    to_emails: List[str],
    subject: str,
    message: str,
    is_html: bool = False
) -> bool:
    """
    发送通知邮件的便捷函数
    
    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        message: 邮件内容
        is_html: 是否为HTML格式邮件，默认为False
        
    Returns:
        bool: 发送是否成功
    """
    try:
        email_sender = get_email_sender()
        return email_sender.send_email(
            to_emails=to_emails,
            subject=subject,
            body=message,
            is_html=is_html
        )
    except Exception as e:
        app_logger.error(f"Failed to send notification email: {str(e)}")
        return False


def send_report_email(
    to_emails: List[str],
    subject: str,
    message: str,
    report_file_path: str,
    is_html: bool = False
) -> bool:
    """
    发送带报告附件的邮件的便捷函数
    
    Args:
        to_emails: 收件人邮箱列表
        subject: 邮件主题
        message: 邮件内容
        report_file_path: 报告文件路径
        is_html: 是否为HTML格式邮件，默认为False
        
    Returns:
        bool: 发送是否成功
    """
    try:
        email_sender = get_email_sender()
        return email_sender.send_email(
            to_emails=to_emails,
            subject=subject,
            body=message,
            is_html=is_html,
            attachments=[report_file_path]
        )
    except Exception as e:
        app_logger.error(f"Failed to send report email: {str(e)}")
        return False
    
if __name__ == "__main__":
    # 测试邮件发送功能
    to_emails = ["qyq799660872@163.com"]
    subject = "Test Email"
    message = "This is a test email sent from Python."
    
    sent = send_notification_email(to_emails, subject, message)
    print(f"Email sent: {sent}")