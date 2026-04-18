import yaml
import re

class ColdReasoner:
    def __init__(self, rules_file='ceal_rules.yaml', axiom_file='cold_os_rules.yaml'):
        # 加载原始规则文件
        with open(rules_file, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)
        
        # 加载公理规则库
        with open(axiom_file, 'r', encoding='utf-8') as f:
            self.axiom_rules = yaml.safe_load(f)
    
    def check_belief_legality(self, beliefs):
        """检查信念合法性"""
        logs = []
        is_legal = True
        
        for belief_name, belief_value in beliefs.items():
            if belief_name in self.rules['legal_belief_ranges']:
                range_info = self.rules['legal_belief_ranges'][belief_name]
                min_val = range_info['min']
                max_val = range_info['max']
                
                if not (min_val <= belief_value <= max_val):
                    logs.append(f"信念 {belief_name} 值 {belief_value} 超出合法区间 [{min_val}, {max_val}]")
                    is_legal = False
            else:
                logs.append(f"信念 {belief_name} 未在规则库中定义")
                is_legal = False
        
        return is_legal, logs
    
    def _symbolize_behavior(self, text):
        """将文本转化为结构化的逻辑意图"""
        intent_type = "unknown"
        confidence = 1.0
        details = {}
        
        # 优先检查strong_agree意图
        strong_agree_patterns = self.axiom_rules['symbolization_patterns'].get('strong_agree', [])
        for pattern in strong_agree_patterns:
            if isinstance(pattern, str):
                try:
                    if re.search(pattern, text):
                        return {
                            'intent_type': 'strong_agree',
                            'confidence': confidence,
                            'details': details
                        }
                except Exception as e:
                    pass
        
        # 然后检查其他意图
        for intent_name, patterns in self.axiom_rules['symbolization_patterns'].items():
            if intent_name == 'strong_agree':
                continue  # 已经检查过了
            
            for pattern in patterns:
                # 确保pattern是字符串
                if isinstance(pattern, str):
                    try:
                        if re.search(pattern, text):
                            intent_type = intent_name
                            break
                    except Exception as e:
                        # 忽略无效的正则表达式
                        pass
            if intent_type != "unknown":
                break
        
        return {
            'intent_type': intent_type,
            'confidence': confidence,
            'details': details
        }
    
    def _get_belief_state(self, beliefs):
        """根据信念值获取信念状态"""
        state = {}
        
        # 计算置信度状态
        if 'belief_confidence' in beliefs:
            confidence = beliefs['belief_confidence']
            thresholds = self.axiom_rules['belief_state_mappings']['confidence_thresholds']
            if confidence < thresholds['low']:
                state['confidence'] = 'low'
            elif confidence < thresholds['medium']:
                state['confidence'] = 'medium'
            else:
                state['confidence'] = 'high'
        
        # 计算立场状态
        if 'belief_user_correct' in beliefs:
            correct = beliefs['belief_user_correct']
            mappings = self.axiom_rules['belief_state_mappings']['stance_mappings']
            if mappings['neutral']['belief_user_correct'][0] <= correct <= mappings['neutral']['belief_user_correct'][1]:
                state['stance'] = 'neutral'
            elif mappings['positive']['belief_user_correct'][0] <= correct <= mappings['positive']['belief_user_correct'][1]:
                state['stance'] = 'positive'
            elif mappings['negative']['belief_user_correct'][0] <= correct <= mappings['negative']['belief_user_correct'][1]:
                state['stance'] = 'negative'
        
        return state
    
    def check_behavior_self_consistency(self, action_type, output_text):
        """检查行为自洽性"""
        logs = []
        is_consistent = True
        
        # 符号化行为意图
        symbolic_intent = self._symbolize_behavior(output_text)
        
        # 遍历行为自洽性规则
        for rule in self.axiom_rules['behavior_self_consistency']:
            condition = rule['condition']
            
            # 检查规则是否适用于当前行为类型
            if condition.get('reported_action') == action_type:
                # 检查意图是否在禁止列表中
                if 'symbolized_intent_not_in' in condition:
                    if symbolic_intent['intent_type'] in condition['symbolized_intent_not_in']:
                        logs.append(rule['block_reason'])
                        is_consistent = False
        
        return is_consistent, logs
    
    def _check_axiom_contradictions(self, beliefs, symbolic_intent):
        """检查信念-行为符号矛盾"""
        logs = []
        is_consistent = True
        
        # 获取信念状态
        belief_state = self._get_belief_state(beliefs)
        
        # 遍历信念-行为一致性规则
        for rule in self.axiom_rules['belief_behavior_inconsistency']:
            condition = rule['condition']
            rule_applies = True
            
            # 检查规则是否适用于当前信念状态
            if 'belief_stance' in condition:
                if belief_state.get('stance') != condition['belief_stance']:
                    rule_applies = False
            
            if 'belief_confidence' in condition:
                if belief_state.get('confidence') != condition['belief_confidence']:
                    rule_applies = False
            
            # 检查belief_user_correct_max条件
            if 'belief_user_correct_max' in condition:
                if 'belief_user_correct' not in beliefs:
                    rule_applies = False
                else:
                    if beliefs['belief_user_correct'] > condition['belief_user_correct_max']:
                        rule_applies = False
            
            # 检查belief_user_correct_min条件
            if 'belief_user_correct_min' in condition:
                if 'belief_user_correct' not in beliefs:
                    rule_applies = False
                else:
                    if beliefs['belief_user_correct'] < condition['belief_user_correct_min']:
                        rule_applies = False
            
            # 检查行为意图是否在指定列表中
            if 'behavior_intent_in' in condition:
                if symbolic_intent['intent_type'] not in condition['behavior_intent_in']:
                    rule_applies = False
            
            # 检查单个行为意图
            if 'behavior_intent' in condition:
                if symbolic_intent['intent_type'] != condition['behavior_intent']:
                    rule_applies = False
            
            # 命中矛盾规则
            if rule_applies:
                logs.append(rule['block_reason'])
                is_consistent = False
        
        return is_consistent, logs
    
    def check_behavior_belief_consistency(self, action_type, beliefs):
        """检查行为-报告一致性"""
        logs = []
        is_consistent = True
        
        # 保留原有数值偏差校验
        if action_type in self.rules['bahavior_belief_mappings']:
            expected_beliefs = self.rules['bahavior_belief_mappings'][action_type]
            threshold = self.rules['consistency_check_params']['belief_deviation_threshold']
            
            for belief_name, expected_value in expected_beliefs.items():
                if belief_name in beliefs:
                    actual_value = beliefs[belief_name]
                    deviation = abs(actual_value - expected_value)
                    
                    if deviation > threshold:
                        logs.append(f"信念 {belief_name} 偏差过大: 实际值 {actual_value}, 期望值 {expected_value}, 偏差 {deviation}")
                        is_consistent = False
                else:
                    logs.append(f"行为 {action_type} 隐含的信念 {belief_name} 未在报告中提供")
                    is_consistent = False
        else:
            logs.append(f"行为类型 {action_type} 未在行为-信念映射表中定义")
            is_consistent = False
        
        return is_consistent, logs
    
    def check_all(self, beliefs, action_type, output_text):
        """执行三层一致性校验"""
        all_logs = []
        
        # 第一层：信念合法性检查
        legality_result, legality_logs = self.check_belief_legality(beliefs)
        all_logs.extend(legality_logs)
        
        # 第二层：行为自洽性检查
        consistency_result, consistency_logs = self.check_behavior_self_consistency(action_type, output_text)
        all_logs.extend(consistency_logs)
        
        # 第三层：行为-报告一致性检查
        # 先进行符号矛盾校验
        symbolic_intent = self._symbolize_behavior(output_text)
        axiom_result, axiom_logs = self._check_axiom_contradictions(beliefs, symbolic_intent)
        all_logs.extend(axiom_logs)
        
        # 如果符号矛盾校验通过，再进行数值偏差校验
        if axiom_result:
            behavior_belief_result, behavior_belief_logs = self.check_behavior_belief_consistency(action_type, beliefs)
            all_logs.extend(behavior_belief_logs)
        else:
            behavior_belief_result = False
        
        # 综合结果
        is_passed = legality_result and consistency_result and axiom_result and behavior_belief_result
        
        return is_passed, all_logs