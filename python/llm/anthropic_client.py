from llm.llm_client import LLMClient
import anthropic
import os


MODEL_HAIKU = "claude-3-5-haiku-latest"
MODEL_SONNET = "claude-3-7-sonnet-latest"


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str = None):
        """
        Initializes the Anthropic client.
        API key can be provided directly or will be fetched from ANTHROPIC_API_KEY environment variable.
        """
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable or pass it directly.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_text(self, prompt: str, model: str = MODEL_SONNET, max_tokens: int = 1024) -> str:
        """
        Generates text using the specified Anthropic model.

        Args:
            prompt (str): The prompt to send to the model.
            model (str): The model to use (e.g., 'claude-3-5-haiku-latest', 'claude-3-7-sonnet-latest').
            max_tokens (int): The maximum number of tokens to generate.

        Returns:
            str: The generated text.
        """
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return ""

if __name__ == '__main__':
    # Example usage (requires ANTHROPIC_API_KEY to be set in the environment)
    try:
        client = AnthropicClient()
        example_prompt = "Hello, Claude. Tell me a short story."
        print(f"Sending prompt: {example_prompt}")
        generated_text = client.generate_text(example_prompt)
        print(f"Generated text: {generated_text}")
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
