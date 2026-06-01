import os
import sys
import argparse
from config import MAX_ITERS
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from functions.call_functions import available_functions, call_function
from enum import Enum, auto


class GenerateResult(Enum):
    DONE = auto()
    CONTINUE = auto()


def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == "" or api_key is None:
        raise RuntimeError("Couldn't find the Gemini API key")

    client = genai.Client(api_key=api_key)

    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    for _ in range(MAX_ITERS):
        try:
            final_response = generate_content(client, messages, args.verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                return
        except Exception as e:
            print(f"Error during content generation: {e}")

    print(f"Reached maximum iterations ({MAX_ITERS}) without a final response.")
    sys.exit(1)


def generate_content(
    client: genai.Client, messages: list[types.Content], verbose: bool
) -> str | None:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    if response.usage_metadata is None:
        raise RuntimeError("Failed to request Gemini's API")

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.candidates is not None and len(response.candidates) > 0:
        for candidate in response.candidates:
            if candidate.content is not None:
                messages.append(candidate.content)

    if not response.function_calls:
        return response.text

    function_results: list[types.Part] = []
    for function_call in response.function_calls:
        print(f"Calling function: {function_call.name}({function_call.args})")
        function_call_result = call_function(function_call, verbose)

        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response
            or not function_call_result.parts[0].function_response.response
        ):
            raise RuntimeError(f"Empty function response for {function_call.name}")
        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")

        function_results.append(function_call_result.parts[0])

    messages.append(types.Content(role="user", parts=function_results))


if __name__ == "__main__":
    main()
