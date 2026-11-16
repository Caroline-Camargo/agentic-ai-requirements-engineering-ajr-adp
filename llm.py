"""Wrapper da API DeepSeek (usando biblioteca openai) com rate limit, retry e modo MOCK para testes."""
import os, time, random, json

import config

class DailyQuotaExceeded(Exception):
    pass

_client = None

def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise SystemExit("Defina a variável de ambiente DEEPSEEK_API_KEY com a sua chave da DeepSeek (ex: export DEEPSEEK_API_KEY='sk-...').")
        base_url = getattr(config, "DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        _client = OpenAI(api_key=key, base_url=base_url)
    return _client

def _mock(prompt, json_mode):
    random.seed(hash(prompt) % 10**6)
    if json_mode:
        out = {}
        boost = 0.8 if "[ADP]" in prompt else 0.0
        for k, (_, (lo, hi)) in config.CRITERIA.items():
            v = lo + (hi - lo) * min(1, max(0, random.random() * 0.7 + boost * 0.25))
            out[k] = {"j": "mock", "n": int(round(v))}
        out["cx"] = {"j": "mock", "n": random.randint(0, 3)}
        return dict(text=json.dumps(out), tokens_in=100, tokens_out=100, tokens_thinking=0, finish_reason="stop")
    n = random.randint(250, 350) if "AJR" in prompt else random.randint(120, 220)
    txt = ("[ADP] " if "AJR" in prompt else "") + "Especificação simulada. " * n
    return dict(text=txt, tokens_in=len(prompt) // 4, tokens_out=n * 3, tokens_thinking=0, finish_reason="stop")

def call(model, prompt, temperature, system=None, json_mode=False, max_retries=6):
    global _last
    if os.getenv("MOCK_LLM"):
        return _mock(prompt, json_mode)
    
    from openai import APIError, RateLimitError, APIConnectionError, AuthenticationError

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    # Preparar parâmetros
    max_tokens = getattr(config, "MAX_OUTPUT_TOKENS", 8192)
    # deepseek-chat tem limite de saída de 8192 tokens
    if "chat" in model.lower() and max_tokens > 8192:
        max_tokens = 8192

    kwargs = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }

    # deepseek-reasoner NÃO aceita o parâmetro temperature (retorna HTTP 400)
    # Para deepseek-flash e modelos de chat, desativamos o modo thinking para focar 100% dos tokens na resposta
    if "reasoner" not in model.lower():
        kwargs["temperature"] = temperature
        kwargs["extra_body"] = {"thinking": {"type": "disabled"}}

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(max_retries):
        try:
            r = _get_client().chat.completions.create(**kwargs)
            choice = r.choices[0] if r.choices else None
            text = (choice.message.content or "") if choice else ""
            fr = str(choice.finish_reason) if choice else None

            # Extração de thinking/reasoning (deepseek-reasoner / R1)
            reasoning_content = None
            if choice and hasattr(choice, "message"):
                reasoning_content = getattr(choice.message, "reasoning_content", None)
                if reasoning_content is None and hasattr(choice.message, "model_extra") and choice.message.model_extra:
                    reasoning_content = choice.message.model_extra.get("reasoning_content")

            tokens_in = r.usage.prompt_tokens if r.usage else (len(prompt) // 4)
            tokens_out = r.usage.completion_tokens if r.usage else (len(text) // 4)
            tokens_thinking = None
            if r.usage:
                details = getattr(r.usage, "completion_tokens_details", None)
                if details:
                    tokens_thinking = getattr(details, "reasoning_tokens", None)
            if tokens_thinking is None and reasoning_content:
                tokens_thinking = len(reasoning_content) // 4

            return dict(
                text=text,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                tokens_thinking=tokens_thinking,
                finish_reason=fr
            )

        except AuthenticationError as e:
            raise SystemExit(f"Erro de autenticação na API DeepSeek: {e}")
        except RateLimitError as e:
            msg = str(e)
            if "balance" in msg.lower() or "insufficient" in msg.lower():
                raise DailyQuotaExceeded(f"Saldo insuficiente na API DeepSeek: {msg}")
            sleep_time = min(120, 5 * (2 ** attempt) + random.random())
            time.sleep(sleep_time)
            continue
        except APIError as e:
            msg = str(e)
            if "thinking" in msg.lower() and "extra_body" in kwargs:
                kwargs.pop("extra_body", None)
                continue
            status = getattr(e, "status_code", None)
            if status == 402 or "insufficient balance" in msg.lower() or "balance" in msg.lower():
                raise DailyQuotaExceeded(f"Saldo insuficiente na conta DeepSeek: {msg}")
            if status in (429, 500, 502, 503, 504):
                sleep_time = min(120, 5 * (2 ** attempt) + random.random())
                time.sleep(sleep_time)
                continue
            raise
        except APIConnectionError:
            time.sleep(min(60, 3 * (2 ** attempt) + random.random()))
            continue

    raise RuntimeError("Falhou após várias tentativas de conexão com a API DeepSeek")
