#!/usr/bin/env python
"""Benchmark script to measure and compare LLM model providers.

1. Queries and lists the accessible models for each configured provider.
2. Benchmarks a curated list of free-tier friendly models directly in our codebase
   and via direct OpenAI-compatible endpoints to evaluate TTFT, latency, and throughput.
"""

import asyncio
import os
import sys
import time
from typing import Any

import httpx
from dotenv import load_dotenv

from api.dependencies import _create_provider_for_type
from api.models.anthropic import Message, MessagesRequest
from config.settings import get_settings

# Load dotenv directly to read all keys including those not in Pydantic Settings
load_dotenv()


async def list_models(
    client: httpx.AsyncClient, provider: str, api_key: str
) -> list[str]:
    """List available models for a given provider using their API."""
    if not api_key or not api_key.strip():
        return []

    try:
        if provider == "nvidia_nim":
            headers = {"Authorization": f"Bearer {api_key}"}
            r = await client.get(
                "https://integrate.api.nvidia.com/v1/models",
                headers=headers,
                timeout=10.0,
            )
            if r.status_code == 200:
                data = r.json()
                return sorted([m["id"] for m in data.get("data", [])])
            return [f"Error HTTP {r.status_code}: {r.text}"]

        elif provider == "google_ai_studio":
            params = {"key": api_key}
            r = await client.get(
                "https://generativelanguage.googleapis.com/v1beta/models",
                params=params,
                timeout=10.0,
            )
            if r.status_code == 200:
                data = r.json()
                # Gemini models returned usually start with 'models/'
                return sorted(
                    [m["name"].replace("models/", "") for m in data.get("models", [])]
                )
            return [f"Error HTTP {r.status_code}: {r.text}"]

        elif provider == "open_router":
            headers = {"Authorization": f"Bearer {api_key}"}
            r = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=10.0,
            )
            if r.status_code == 200:
                data = r.json()
                return sorted([m["id"] for m in data.get("data", [])])
            return [f"Error HTTP {r.status_code}: {r.text}"]

        elif provider == "cerebras":
            headers = {"Authorization": f"Bearer {api_key}"}
            r = await client.get(
                "https://api.cerebras.ai/v1/models",
                headers=headers,
                timeout=10.0,
            )
            if r.status_code == 200:
                data = r.json()
                return sorted([m["id"] for m in data.get("data", [])])
            return [f"Error HTTP {r.status_code}: {r.text}"]

        elif provider == "grok":
            headers = {"Authorization": f"Bearer {api_key}"}
            r = await client.get(
                "https://api.x.ai/v1/models",
                headers=headers,
                timeout=10.0,
            )
            if r.status_code == 200:
                data = r.json()
                return sorted([m["id"] for m in data.get("data", [])])
            return [f"Error HTTP {r.status_code}: {r.text}"]

        elif provider == "cohere":
            headers = {"Authorization": f"Bearer {api_key}"}
            r = await client.get(
                "https://api.cohere.ai/compatibility/v1/models",
                headers=headers,
                timeout=10.0,
            )
            if r.status_code == 200:
                data = r.json()
                return sorted([m["id"] for m in data.get("data", [])])
            return [f"Error HTTP {r.status_code}: {r.text}"]

    except Exception as e:
        return [f"Exception listing models: {e}"]

    return []


async def benchmark_model(provider_type: str, model_name: str, settings: Any) -> dict:
    """Benchmark a single model/provider combination using proxy providers."""
    try:
        provider = _create_provider_for_type(provider_type, settings)
    except Exception as e:
        return {
            "model": f"{provider_type}/{model_name}",
            "status": "Init Error",
            "ttft_ms": None,
            "total_time_ms": None,
            "tokens": 0,
            "tokens_per_sec": 0.0,
            "error": str(e),
        }

    req = MessagesRequest(
        model=model_name,
        messages=[Message(role="user", content="hola")],
        max_tokens=25,
        stream=True,
    )

    start_time = time.perf_counter()
    ttft = None
    total_tokens = 0
    status = "Success"
    error_msg = ""

    try:
        async for chunk in provider.stream_response(
            req, input_tokens=10, request_id="benchmark_test"
        ):
            if "content_block_delta" in chunk:
                if ttft is None:
                    ttft = time.perf_counter() - start_time
                total_tokens += 1
    except Exception as e:
        status = "Failed"
        error_msg = str(e)
    finally:
        await provider.cleanup()

    total_time = time.perf_counter() - start_time

    return {
        "model": f"{provider_type}/{model_name}",
        "status": status,
        "ttft_ms": int(ttft * 1000) if ttft is not None else None,
        "total_time_ms": int(total_time * 1000),
        "tokens": total_tokens,
        "tokens_per_sec": (
            round(total_tokens / total_time, 2)
            if total_time > 0 and total_tokens > 0
            else 0.0
        ),
        "error": error_msg,
    }


async def benchmark_direct_openai(
    provider_name: str, base_url: str, api_key: str, model_name: str
) -> dict:
    """Benchmark a model directly via OpenAI client."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    start_time = time.perf_counter()
    ttft = None
    total_tokens = 0
    status = "Success"
    error_msg = ""

    try:
        stream = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "hola"}],
            max_tokens=25,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                if ttft is None:
                    ttft = time.perf_counter() - start_time
                total_tokens += 1
    except Exception as e:
        status = "Failed"
        error_msg = str(e)
    finally:
        await client.close()

    total_time = time.perf_counter() - start_time

    return {
        "model": f"{provider_name}/{model_name}",
        "status": status,
        "ttft_ms": int(ttft * 1000) if ttft is not None else None,
        "total_time_ms": int(total_time * 1000),
        "tokens": total_tokens,
        "tokens_per_sec": (
            round(total_tokens / total_time, 2)
            if total_time > 0 and total_tokens > 0
            else 0.0
        ),
        "error": error_msg,
    }


async def main():
    settings = get_settings()

    print("=========================================================")
    print("PHASE 1: LISTING ACCESSIBLE MODELS FOR EACH PROVIDER")
    print("=========================================================")

    providers = {
        "nvidia_nim": settings.nvidia_nim_api_key,
        "google_ai_studio": settings.google_ai_studio_api_key,
        "open_router": settings.open_router_api_key,
        "cerebras": os.getenv("CEREBRAS_API_KEY", ""),
        "grok": os.getenv("GROK_API_KEY", ""),
        "cohere": os.getenv("COHERE_API_KEY", ""),
    }

    async with httpx.AsyncClient() as client:
        for provider_name, api_key in providers.items():
            if api_key and api_key.strip():
                print(f"\n--- Provider: {provider_name} ---")
                models = await list_models(client, provider_name, api_key)
                if not models:
                    print("No models found or empty response.")
                else:
                    # Filter out error strings or print them differently
                    errors = [
                        m
                        for m in models
                        if m.startswith("Error") or m.startswith("Exception")
                    ]
                    valid_models = [
                        m
                        for m in models
                        if not (m.startswith("Error") or m.startswith("Exception"))
                    ]

                    if errors:
                        for err in errors:
                            print(f"  [ERROR] {err}")
                    if valid_models:
                        print(f"  Accessible Models ({len(valid_models)}):")
                        # Print models grouped or in chunks for readability
                        for i in range(0, len(valid_models), 3):
                            chunk = valid_models[i : i + 3]
                            print("    " + ", ".join(f"`{m}`" for m in chunk))
            else:
                print(
                    f"\n--- Provider: {provider_name} (NOT CONFIGURED - Key missing) ---"
                )

    print("\n=========================================================")
    print("PHASE 2: RUNNING BENCHMARK FOR SELECTED MODELS")
    print("=========================================================")

    results = []

    # 1. Native Proxy Providers
    if settings.nvidia_nim_api_key.strip():
        nim_models = [
            "mistralai/mistral-small-4-119b-2603",
            "mistralai/mistral-large-3-675b-instruct-2512",
            "z-ai/glm-5.1",
            "meta/llama-3.3-70b-instruct",
        ]
        for model in nim_models:
            print(f"Testing nvidia_nim/{model} via proxy provider...")
            res = await benchmark_model("nvidia_nim", model, settings)
            results.append(res)

    if settings.google_ai_studio_api_key.strip():
        gemini_models = ["gemini-2.5-flash", "gemini-2.5-pro"]
        for model in gemini_models:
            print(f"Testing google_ai_studio/{model} via proxy provider...")
            res = await benchmark_model("google_ai_studio", model, settings)
            results.append(res)

    if settings.open_router_api_key.strip():
        openrouter_models = [
            "meta-llama/llama-3.2-3b-instruct:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-4-31b-it:free",
            "qwen/qwen3-coder:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
        ]
        for model in openrouter_models:
            print(f"Testing open_router/{model} via proxy provider...")
            res = await benchmark_model("open_router", model, settings)
            results.append(res)

    # 2. Direct OpenAI-compatible Providers (Cerebras, Grok, Cohere)
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    if cerebras_key and cerebras_key.strip():
        for model in ["gpt-oss-120b", "zai-glm-4.7"]:
            print(f"Testing cerebras/{model} directly...")
            res = await benchmark_direct_openai(
                "cerebras", "https://api.cerebras.ai/v1", cerebras_key, model
            )
            results.append(res)

    grok_key = os.getenv("GROK_API_KEY")
    if grok_key and grok_key.strip():
        print("Testing grok/grok-2-latest directly...")
        res = await benchmark_direct_openai(
            "grok", "https://api.x.ai/v1", grok_key, "grok-2-latest"
        )
        results.append(res)

    cohere_key = os.getenv("COHERE_API_KEY")
    if cohere_key and cohere_key.strip():
        for model in ["command-r-08-2024", "command-r-plus-08-2024"]:
            print(f"Testing cohere/{model} directly...")
            res = await benchmark_direct_openai(
                "cohere", "https://api.cohere.ai/compatibility/v1", cohere_key, model
            )
            results.append(res)

    if not results:
        print("Error: No providers are configured with API keys in your .env file.")
        sys.exit(1)

    print("\nBenchmark Complete!\n")

    # Generate Markdown Table
    print(
        "| Model / Provider | Status | TTFT (ms) | Speed (t/s) | Total Time (ms) | Info / Error |"
    )
    print("| --- | --- | --- | --- | --- | --- |")
    for res in results:
        ttft = res["ttft_ms"] if res["ttft_ms"] is not None else "-"
        speed = res["tokens_per_sec"] if res["status"] == "Success" else "-"
        total = res["total_time_ms"] if res["total_time_ms"] is not None else "-"
        err = res["error"] if res["error"] else "-"
        if len(err) > 60:
            err = err[:57] + "..."
        print(
            f"| `{res['model']}` | {res['status']} | {ttft} | {speed} | {total} | {err} |"
        )


if __name__ == "__main__":
    asyncio.run(main())
