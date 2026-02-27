from tools.weather import get_weather, TOOL_SCHEMA as WEATHER_SCHEMA

# Registry: maps tool name → (callable, schema)
TOOL_REGISTRY = {
    "get_weather": (get_weather, WEATHER_SCHEMA),
}

ALL_SCHEMAS = [schema for _, schema in TOOL_REGISTRY.values()]
