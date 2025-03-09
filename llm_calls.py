import litellm
import json
from litellm import completion, token_counter, completion_cost, get_max_tokens
from assets import USER_MESSAGE, MODELS_USED
from api_management import get_api_key
import os

def call_llm_model(data, response_format, model, system_message, extra_user_instruction="", max_tokens=None, use_model_max_tokens_if_none=False):
    """
    Calls an LLM via LiteLLM and returns:
      - parsed_response (str or dict),
      - token_counts ({"input_tokens": int, "output_tokens": int}),
      - cost (float).
    It respects the maximum token limits and uses an improved prompt to force JSON output for structured data.

    Parameters:
        data (str): Additional data (e.g., raw webpage text).
        response_format: Expected response format (e.g., a Pydantic model).
        model (str): Model identifier.
        system_message (str): System prompt.
        extra_user_instruction (str): Additional instructions.
        max_tokens (int, optional): Maximum tokens for completion.
        use_model_max_tokens_if_none (bool, optional): Use model's max tokens if max_tokens is None.

    Returns:
        tuple: (parsed_response, token_counts, cost)
    """
    env_var_name = list(MODELS_USED[model])[0]  # e.g., "GEMINI_API_KEY"
    env_value = get_api_key(model)
    print("env variable is:" + env_value)
    if env_value:
        os.environ[env_var_name] = env_value

    model_max_tokens = get_max_tokens(model)
    if max_tokens is not None:
        max_tokens = min(max_tokens, model_max_tokens) - 100
    elif use_model_max_tokens_if_none:
        max_tokens = model_max_tokens - 100

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{USER_MESSAGE} {extra_user_instruction} {data}"}
    ]

    params = {
        "model": model,
        "messages": messages,
        "response_format": response_format,
    }
    if max_tokens is not None:
        params["max_tokens"] = max_tokens

    response = completion(**params)
    parsed_response = response.choices[0].message.content

    input_tokens = token_counter(model=model, messages=messages)
    output_text = parsed_response if isinstance(parsed_response, str) else json.dumps(parsed_response)
    output_tokens = token_counter(model=model, text=output_text)

    token_counts = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    cost = completion_cost(completion_response=response)

    return parsed_response, token_counts, cost
