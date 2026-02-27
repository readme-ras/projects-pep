"""
Agent loop.

Flow:
  1. User sends a message.
  2. LLM responds — either plain text (done) or a tool_call block.
  3. If tool_call: execute the tool, append result, loop back to LLM.
  4. Repeat until plain-text response or max_steps reached.
"""

import json
from agent.llm import call_llm, parse_tool_call
from tools import TOOL_REGISTRY, ALL_SCHEMAS


MAX_STEPS = 5   # guard against infinite loops


class Agent:
    def __init__(self):
        self.tools    = ALL_SCHEMAS
        self.registry = TOOL_REGISTRY

    def run(self, user_message: str, history: list[dict] | None = None) -> dict:
        """
        Run the agent for one user turn.

        Args:
            user_message: The user's input.
            history:      Previous messages for multi-turn context.

        Returns:
            {
              "response":    str,           # final assistant reply
              "tool_calls":  list[dict],    # all tool calls made
              "steps":       int,
              "messages":    list[dict],    # full message log
            }
        """
        messages   = list(history or [])
        messages.append({"role": "user", "content": user_message})

        tool_calls = []
        steps      = 0

        while steps < MAX_STEPS:
            steps += 1
            raw = call_llm(messages, self.tools)

            # Check if the model wants to call a tool
            tool_call = parse_tool_call(raw)

            if tool_call:
                tool_name = tool_call.get("tool")
                arguments = tool_call.get("arguments", {})

                # Record the assistant's tool-call message
                messages.append({"role": "assistant", "content": raw})

                # Execute tool
                result = self._execute_tool(tool_name, arguments)
                tool_calls.append({
                    "tool":      tool_name,
                    "arguments": arguments,
                    "result":    result,
                })

                # Feed result back
                result_text = json.dumps(result) if isinstance(result, dict) else str(result)
                messages.append({"role": "tool", "content": result_text})

            else:
                # Plain response — we're done
                messages.append({"role": "assistant", "content": raw})
                return {
                    "response":   raw,
                    "tool_calls": tool_calls,
                    "steps":      steps,
                    "messages":   messages,
                }

        # Fallback if max steps reached
        fallback = "I reached the maximum reasoning steps. Please try rephrasing your question."
        messages.append({"role": "assistant", "content": fallback})
        return {
            "response":   fallback,
            "tool_calls": tool_calls,
            "steps":      steps,
            "messages":   messages,
        }

    def _execute_tool(self, name: str, arguments: dict):
        if name not in self.registry:
            return {"error": f"Unknown tool: '{name}'"}
        fn, _ = self.registry[name]
        try:
            return fn(**arguments)
        except Exception as e:
            return {"error": str(e)}
