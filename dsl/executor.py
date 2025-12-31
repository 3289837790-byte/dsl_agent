from dsl.parser import parse_dsl_file


class DSLExecutor:
    def __init__(self, script_path, llm_client):
        """
        :param script_path: RSL 脚本文件的路径
        :param llm_client: 统一的大模型客户端 (可能是 Real 也可能是 Stub)
        """
        self.llm = llm_client

        # 1. 解析脚本
        try:
            self.script = parse_dsl_file(script_path)
            # 2. 初始化指针
            self.current_state_name = self.script.start_state
            self.is_finished = False
        except Exception as e:
            print(f"❌ 脚本解析失败: {e}")
            self.script = None
            self.is_finished = True

    def get_current_state(self):
        """获取当前状态对象"""
        if not self.script: return None
        return self.script.states.get(self.current_state_name)

    def run(self):
        """启动会话，返回开场白"""
        if not self.script: return "系统错误：脚本未加载"

        self.current_state_name = self.script.start_state
        self.is_finished = False

        start_node = self.get_current_state()
        return start_node.response if start_node else "Error: Start state not found."

    def step(self, user_input):
        """
        执行一步状态流转
        """
        if self.is_finished:
            return "（会话已结束）"

        current_node = self.get_current_state()
        if not current_node: return "系统错误：状态丢失"

        # 1. 检查是否是结束状态
        if current_node.is_end or not current_node.transitions:
            self.is_finished = True
            return "（流程结束）"

        # 2. 准备候选项
        transitions = current_node.transitions
        # 构造映射表: { "中文描述": Transition对象 }
        # 这样做是为了让 LLM 理解选项含义
        options_map = {t.description: t for t in transitions}
        options_text = list(options_map.keys())

        # 3. 意图识别 (委托给 LLMClient，支持 Stub/Real 切换)
        # print(f"   [Debug] 正在识别意图，候选: {options_text}")
        detected_intent = self.llm.recognize_intent(user_input, options_text)

        # 4. 状态跳转
        if detected_intent in options_map:
            # 找到对应的 Transition 对象
            trans = options_map[detected_intent]

            # 更新状态指针
            self.current_state_name = trans.target_state

            # 获取新状态
            new_state = self.get_current_state()

            # 检查新状态是否结束
            if new_state.is_end:
                self.is_finished = True

            return new_state.response
        else:
            # 兜底回复
            return f"抱歉，我没听懂。请参考以下内容回复：{' / '.join(options_text)}"