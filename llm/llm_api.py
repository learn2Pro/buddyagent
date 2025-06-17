from abc import abstractmethod
from openai import OpenAI

class LLM:
    def __init__(self, model_name, api_base, api_key, temperature, max_tokens):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def chat_completion(self, messages, stream=False):
        pass


class OpenAIClient(LLM):
    def __init__(self, model_name, api_base, api_key, temperature, max_tokens):
        super().__init__(model_name, api_base, api_key, temperature, max_tokens)
        self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)

    def chat_completion(self, messages, stream=False):
        return self.client.chat.completions.create(
            model=self.model_name, messages=messages, stream=stream
        )


class ClaudeClient(LLM):
    def __init__(self, model_name, api_base, api_key, temperature, max_tokens):
        super().__init__(model_name, api_base, api_key, temperature, max_tokens)
        self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)
        

    def chat_completion(self, messages):
        pass


if __name__ == "__main__":
    from conf.config_loader import config_data

    model_name = "claude-sonnet-4-20250514"
    llm_config = config_data["llm"][model_name]
    llm = OpenAIClient(
        model_name,
        api_base=llm_config['api_base'],
        api_key=llm_config['api_key'],
        temperature=llm_config['temperature'],
        max_tokens=llm_config['max_tokens'],
    )
    completion = llm.chat_completion(messages=[{"role": "user", "content": "Hello, world!"}])
    print(completion)
