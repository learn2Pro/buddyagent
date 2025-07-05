from abc import abstractmethod
from openai import OpenAI
from src.conf.config_loader import config_data
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek, chat_models

class LLM:
    def __init__(self, model_name):
        self.model_name = model_name
        llm_config = config_data["llm"][model_name]
        self.api_base = llm_config["api_base"]
        self.api_key = llm_config["api_key"]

    @abstractmethod
    def chat_completion(self, messages, temperature=0.0, stream=False):
        pass

    @abstractmethod
    def get_llm(self):
        pass


class OpenAIClient(LLM):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.client = ChatOpenAI(model=model_name, base_url=self.api_base, api_key=self.api_key, temperature=0.0)

    def chat_completion(self, messages, temperature=0.0, stream=False):
        return self.client.invoke(messages, temperature=temperature)

    def get_llm(self):
        return self.client
    
class UnifiedLLMClient(LLM):
    def __init__(self, model_name):
        super().__init__(model_name)
        if 'claude' in model_name:
            self.client = ChatOpenAI(model=model_name, base_url=self.api_base, api_key=self.api_key, temperature=0.0)
        elif 'gemini' in model_name:
            self.client = ChatOpenAI(model=model_name, base_url=self.api_base, api_key=self.api_key, temperature=0.0)
        elif 'deepseek' in model_name:
            self.client = ChatOpenAI(model_name=model_name, base_url=self.api_base, api_key=self.api_key, temperature=0.0)
        else:
            self.client = ChatOpenAI(model=model_name, base_url=self.api_base, api_key=self.api_key, temperature=0.0)

    def chat_completion(self, messages, temperature=0.0, stream=False):
        return self.client.chat.completions.create(model=self.model_name, messages=messages, temperature=temperature, stream=stream)
    
    def get_llm(self):
        return self.client


# class ClaudeClient(LLM):
#     def __init__(self, model_name, api_base, api_key, temperature, max_tokens):
#         super().__init__(model_name, api_base, api_key, temperature, max_tokens)
#         self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)

#     def chat_completion(self, messages):
#         pass


if __name__ == "__main__":
    from conf.config_loader import config_data

    llm = OpenAIClient("ep-20250619111741-nx8jc")
    completion = llm.chat_completion(
        messages=[{"role": "user", "content": "Hello, world!"}]
    )
    # for chunk in completion:
    #     print(chunk)
    print(completion.content)
