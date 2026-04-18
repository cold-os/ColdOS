import uuid
import json
from datetime import datetime
from cold_reasoner import ColdReasoner

class CageGateway:
    def __init__(self, rules_file='ceal_rules.yaml'):
        self.reasoner = ColdReasoner(rules_file)
        self.audit_logs = []
    
    def generate_token(self):
        """生成一次性令牌"""
        return str(uuid.uuid4())
    
    def log_audit(self, user_input, agent_response, validation_result, token=None):
        """记录审计日志"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'agent_response': agent_response,
            'validation_result': validation_result,
            'token': token,
            'audit_id': str(uuid.uuid4())
        }
        self.audit_logs.append(audit_entry)
        # 打印审计日志（实际应用中可能会写入文件或数据库）
        try:
            print(f"[审计日志] {json.dumps(audit_entry, ensure_ascii=False, indent=2)}")
        except UnicodeEncodeError:
            # 使用ensure_ascii=True来避免Unicode编码错误
            print(f"[审计日志] {json.dumps(audit_entry, ensure_ascii=True, indent=2)}")
    
    def process_agent_response(self, user_input, agent_response):
        """处理智能体响应并进行校验"""
        # 提取智能体的报告信念和行为提案
        beliefs = agent_response.get('beliefs', {})
        action_type = agent_response.get('action_type')
        output_text = agent_response.get('output_text')
        
        # 调用ColdReasoner进行三层一致性校验
        is_passed, validation_logs = self.reasoner.check_all(beliefs, action_type, output_text)
        
        # 构建校验结果
        validation_result = {
            'passed': is_passed,
            'logs': validation_logs
        }
        
        # 根据校验结果决定是否放行
        if is_passed:
            # 生成一次性令牌
            token = self.generate_token()
            print(f"[CAGE] 校验通过，生成令牌: {token}")
            print(f"[CAGE] 转发行为: {action_type} - {output_text}")
        else:
            token = None
            print(f"[CAGE] 校验失败，拦截行为")
            print(f"[CAGE] 失败原因: {validation_logs}")
        
        # 记录审计日志
        self.log_audit(user_input, agent_response, validation_result, token)
        
        return {
            'passed': is_passed,
            'token': token,
            'validation_logs': validation_logs
        }
    
    def get_audit_logs(self):
        """获取审计日志"""
        return self.audit_logs