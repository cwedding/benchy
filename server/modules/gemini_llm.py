import google.generativeai as genai
import os
import json
from modules.tools import gemini_tools_list
from modules.data_types import SimpleToolCall, ModelAlias, ToolsAndPrompts
from utils import (
    parse_markdown_backticks,
    timeit,
    MAP_MODEL_ALIAS_TO_COST_PER_MILLION_TOKENS,
)
from modules.data_types import ToolCallResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_gemini_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the cost for Gemini API usage.

    Args:
        model: The model name/alias used
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        float: Total cost in dollars
    """

    cost_map = MAP_MODEL_ALIAS_TO_COST_PER_MILLION_TOKENS.get(model)
    if not cost_map:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * cost_map["input"]
    output_cost = (output_tokens / 1_000_000) * cost_map["output"]

    return round(input_cost + output_cost, 6)


def tool_prompt(prompt: str, model: str, force_tools: list[str]) -> ToolCallResponse:
    """
    Run a chat model with tool calls using Gemini's API.
    Now supports JSON structured output variants by parsing the response.
    """
    with timeit() as t:
        if "-json" in model:
            # Initialize model for JSON output
            base_model = model.replace("-json", "")
            if model == "gemini-exp-1114-json":
                base_model = "gemini-exp-1114"  # Map to actual model name

            gemini_model = genai.GenerativeModel(
                model_name=base_model,
            )

            # Send message and get JSON response
            chat = gemini_model.start_chat()
            response = chat.send_message(prompt)

            try:
                # Parse raw response text into ToolsAndPrompts model
                parsed_response = ToolsAndPrompts.model_validate_json(
                    parse_markdown_backticks(response.text)
                )
                tool_calls = [
                    SimpleToolCall(
                        tool_name=tap.tool_name, params={"prompt": tap.prompt}
                    )
                    for tap in parsed_response.tools_and_prompts
                ]
            except Exception as e:
                print(f"Failed to parse JSON response: {e}")
                tool_calls = []

        else:
            # Original implementation using function calling
            gemini_model = genai.GenerativeModel(
                model_name=model, tools=gemini_tools_list
            )
            chat = gemini_model.start_chat(enable_automatic_function_calling=True)
            response = chat.send_message(prompt)

            tool_calls = []
            for part in response.parts:
                if hasattr(part, "function_call"):
                    fc = part.function_call
                    tool_calls.append(SimpleToolCall(tool_name=fc.name, params=fc.args))

        # Extract token counts and calculate cost
        usage_metadata = response._result.usage_metadata
        input_tokens = usage_metadata.prompt_token_count
        output_tokens = usage_metadata.candidates_token_count
        cost = get_gemini_cost(model, input_tokens, output_tokens)

    return ToolCallResponse(
        tool_calls=tool_calls, runTimeMs=t(), inputAndOutputCost=cost
    )
