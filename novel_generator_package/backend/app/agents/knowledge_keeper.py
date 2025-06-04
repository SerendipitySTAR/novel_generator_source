"""
知识库管理员智能体，负责维护和更新小说知识库
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class KnowledgeKeeperAgent(BaseAgent):
    """知识库管理员智能体"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行知识库管理员智能体
        
        Args:
            input_data: 输入数据，包含：
                - operation: 操作类型，可以是"extract"(提取)、"update"(更新)、"query"(查询)
                - content: 需要处理的内容
                - query: 查询内容（当operation为"query"时）
                - kb_snapshot: 当前知识库快照（当operation为"update"时）
            
        Returns:
            Dict[str, Any]: 输出数据，包含：
                - entities: 提取的实体（当operation为"extract"时）
                - relationships: 提取的关系（当operation为"extract"时）
                - events: 提取的事件（当operation为"extract"时）
                - kb_snapshot: 更新后的知识库快照（当operation为"update"时）
                - query_results: 查询结果（当operation为"query"时）
        """
        operation = input_data.get("operation", "")
        
        if operation == "extract":
            return await self._extract_knowledge(input_data)
        elif operation == "update":
            return await self._update_knowledge_base(input_data)
        elif operation == "query":
            return await self._query_knowledge_base(input_data)
        else:
            raise ValueError(f"不支持的操作类型: {operation}")
    
    async def _extract_knowledge(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从内容中提取知识
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        content = input_data.get("content", "")
        
        # 构建提示词
        prompt_template = """你是一位精确的知识提取专家。请从以下内容中提取结构化知识，包括实体、关系和事件。

内容:
{content}

请提取以下内容：
1. 实体：人物、地点、组织、物品等，包括其属性和描述
2. 关系：实体之间的关系，如亲属关系、从属关系、敌对关系等
3. 事件：发生的重要事件，包括参与者、时间、地点、结果等

请按照以下JSON格式输出：

{{
  "entities": [
    {{
      "id": "entity_1",
      "name": "实体名称",
      "type": "人物/地点/组织/物品",
      "attributes": {{
        "属性1": "值1",
        "属性2": "值2",
        ...
      }},
      "description": "实体描述"
    }},
    ...
  ],
  "relationships": [
    {{
      "source_id": "entity_1",
      "target_id": "entity_2",
      "type": "关系类型",
      "description": "关系描述"
    }},
    ...
  ],
  "events": [
    {{
      "id": "event_1",
      "type": "事件类型",
      "participants": ["entity_1", "entity_2", ...],
      "time": "事件时间",
      "location": "事件地点",
      "description": "事件描述",
      "result": "事件结果"
    }},
    ...
  ]
}}
"""
        
        prompt = await self._generate_prompt(prompt_template, {
            "content": content
        })
        
        # 调用LLM提取知识
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=settings.AGENT_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )
        
        # 解析结果
        import json
        import re
        
        try:
            # 使用正则表达式提取JSON部分
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 解析JSON
                result = json.loads(json_str)
                return result
            else:
                # 如果无法提取JSON，返回默认结果
                return {
                    "entities": [],
                    "relationships": [],
                    "events": []
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "entities": [],
                "relationships": [],
                "events": [],
                "error": f"解析提取结果时出错: {str(e)}"
            }
    
    async def _update_knowledge_base(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新知识库
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        content = input_data.get("content", "")
        kb_snapshot = input_data.get("kb_snapshot", {})
        
        # 构建提示词
        prompt_template = """你是一位精确的知识库管理员。请根据以下新内容，更新现有的知识库快照。

新内容:
{content}

现有知识库快照:
{kb_snapshot_text}

请执行以下操作：
1. 添加新实体：如果新内容中出现了知识库中不存在的实体，添加它们
2. 更新现有实体：如果新内容中包含了知识库中已有实体的新信息，更新它们
3. 添加新关系：如果新内容中描述了实体之间的新关系，添加它们
4. 更新现有关系：如果新内容中包含了知识库中已有关系的新信息，更新它们
5. 添加新事件：如果新内容中描述了新的事件，添加它们
6. 解决冲突：如果新内容与知识库中的信息冲突，以新内容为准

请按照以下JSON格式输出更新后的知识库快照：

{{
  "entities": {{
    "entity_1": {{
      "name": "实体名称",
      "type": "人物/地点/组织/物品",
      "attributes": {{
        "属性1": "值1",
        "属性2": "值2",
        ...
      }},
      "description": "实体描述"
    }},
    ...
  }},
  "relationships": [
    {{
      "source_id": "entity_1",
      "target_id": "entity_2",
      "type": "关系类型",
      "description": "关系描述"
    }},
    ...
  ],
  "events": [
    {{
      "id": "event_1",
      "type": "事件类型",
      "participants": ["entity_1", "entity_2", ...],
      "time": "事件时间",
      "location": "事件地点",
      "description": "事件描述",
      "result": "事件结果"
    }},
    ...
  ]
}}
"""
        
        # 将知识库快照转换为文本
        kb_snapshot_text = self._kb_snapshot_to_text(kb_snapshot)
        
        prompt = await self._generate_prompt(prompt_template, {
            "content": content,
            "kb_snapshot_text": kb_snapshot_text
        })
        
        # 调用LLM更新知识库
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=settings.AGENT_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )
        
        # 解析结果
        import json
        import re
        
        try:
            # 使用正则表达式提取JSON部分
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 解析JSON
                result = json.loads(json_str)
                return {"kb_snapshot": result}
            else:
                # 如果无法提取JSON，返回原始知识库快照
                return {"kb_snapshot": kb_snapshot}
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "kb_snapshot": kb_snapshot,
                "error": f"解析更新结果时出错: {str(e)}"
            }
    
    async def _query_knowledge_base(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        查询知识库
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        query = input_data.get("query", "")
        kb_snapshot = input_data.get("kb_snapshot", {})
        
        # 构建提示词
        prompt_template = """你是一位精确的知识库查询专家。请根据以下查询，从知识库中检索相关信息。

查询:
{query}

知识库快照:
{kb_snapshot_text}

请按照以下JSON格式输出查询结果：

{{
  "query_results": [
    {{
      "type": "实体/关系/事件",
      "content": {{
        // 相关内容
      }},
      "relevance": "高/中/低",
      "explanation": "解释为什么这个结果与查询相关"
    }},
    ...
  ],
  "summary": "查询结果的简要总结"
}}
"""
        
        # 将知识库快照转换为文本
        kb_snapshot_text = self._kb_snapshot_to_text(kb_snapshot)
        
        prompt = await self._generate_prompt(prompt_template, {
            "query": query,
            "kb_snapshot_text": kb_snapshot_text
        })
        
        # 调用LLM查询知识库
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=settings.AGENT_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )
        
        # 解析结果
        import json
        import re
        
        try:
            # 使用正则表达式提取JSON部分
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 解析JSON
                result = json.loads(json_str)
                return result
            else:
                # 如果无法提取JSON，返回默认结果
                return {
                    "query_results": [],
                    "summary": "无法解析查询结果"
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "query_results": [],
                "summary": f"解析查询结果时出错: {str(e)}"
            }
    
    def _kb_snapshot_to_text(self, kb_snapshot: Dict[str, Any]) -> str:
        """
        将知识库快照转换为文本
        
        Args:
            kb_snapshot: 知识库快照
            
        Returns:
            str: 文本形式的知识库快照
        """
        text = ""
        
        # 实体信息
        if "entities" in kb_snapshot:
            text += "【实体信息】\n"
            for entity_id, entity in kb_snapshot["entities"].items():
                text += f"- ID: {entity_id}\n"
                text += f"  名称: {entity.get('name', '')}\n"
                text += f"  类型: {entity.get('type', '')}\n"
                
                if "attributes" in entity:
                    text += "  属性:\n"
                    for attr_name, attr_value in entity["attributes"].items():
                        text += f"    {attr_name}: {attr_value}\n"
                
                text += f"  描述: {entity.get('description', '')}\n"
            text += "\n"
        
        # 关系信息
        if "relationships" in kb_snapshot:
            text += "【关系信息】\n"
            for relationship in kb_snapshot["relationships"]:
                source_id = relationship.get("source_id", "")
                target_id = relationship.get("target_id", "")
                rel_type = relationship.get("type", "")
                description = relationship.get("description", "")
                
                text += f"- {source_id} {rel_type} {target_id}: {description}\n"
            text += "\n"
        
        # 事件信息
        if "events" in kb_snapshot:
            text += "【事件信息】\n"
            for event in kb_snapshot["events"]:
                event_id = event.get("id", "")
                event_type = event.get("type", "")
                participants = event.get("participants", [])
                time = event.get("time", "")
                location = event.get("location", "")
                description = event.get("description", "")
                result = event.get("result", "")
                
                text += f"- ID: {event_id}\n"
                text += f"  类型: {event_type}\n"
                text += f"  参与者: {', '.join(participants)}\n"
                text += f"  时间: {time}\n"
                text += f"  地点: {location}\n"
                text += f"  描述: {description}\n"
                text += f"  结果: {result}\n"
            text += "\n"
        
        return text
