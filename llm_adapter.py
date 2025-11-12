import os, json, requests

def call_llm(provider, api_key, messages, max_tokens=400, temperature=0.6):
    provider = (provider or "openai").lower()
    if provider == "openai":
        return _call_openai(api_key, messages, max_tokens, temperature)
    if provider == "anthropic":
        return _call_anthropic(api_key, messages, max_tokens, temperature)
    # fallback simple: try OpenAI if unknown
    return _call_openai(api_key, messages, max_tokens, temperature)

def _call_openai(api_key, messages, max_tokens, temperature):
    import openai
    openai.api_key = api_key
    resp = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_DEFAULT_MODEL","gpt-4o-mini"),
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    text = resp.choices[0].message['content']
    usage = resp.get('usage', {})
    return {"text": text, "usage": usage}
    
def _call_anthropic(api_key, messages, max_tokens, temperature):
    # simple mapping for Claude-like API (adapt if you use Anthropic)
    prompt = \"\\n\".join(m['content'] for m in messages)
    url = "https://api.anthropic.com/v1/complete"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    payload = {"prompt": prompt, "model": "claude-2.1", "max_tokens_to_sample": max_tokens}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    j = r.json()
    return {"text": j.get("completion",""), "usage": j.get("token_usage",{})}
