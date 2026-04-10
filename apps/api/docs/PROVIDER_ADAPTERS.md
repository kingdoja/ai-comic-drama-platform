# Provider Adapter Layer

## Overview

The provider adapter layer decouples business logic from third-party AI service APIs. Both image generation and TTS follow the same pattern: an abstract base class defines the contract, concrete adapters implement it for each vendor, and a factory creates the right instance from configuration.

```
Business Logic (Stage)
        │
        ▼
ProviderAdapter (abstract)
        │
   ┌────┴────┐
   ▼         ▼
VendorA   VendorB   ← swap via .env, no code changes
```

---

## Image Provider

### Interface

`app/providers/image_provider.py`

```python
class ImageProviderAdapter(ABC):
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1080,
        height: int = 1920,
        style: Optional[str] = None,
        shot_id: Optional[UUID] = None,
        **kwargs,
    ) -> ImageGenerationResult: ...
```

`ImageGenerationResult` fields:

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Whether generation succeeded |
| `image_data` | `bytes \| None` | Raw PNG/JPEG bytes |
| `image_url` | `str \| None` | URL if provider returns one |
| `width` / `height` | `int \| None` | Actual dimensions |
| `format` | `str \| None` | `"png"` or `"jpeg"` |
| `shot_id` | `UUID \| None` | Passed-through for tracking |
| `error` | `str \| None` | Error message on failure |
| `request_id` | `str \| None` | Provider's request ID |
| `generation_time_ms` | `int \| None` | Wall-clock generation time |

### Built-in Adapters

| Class | Provider | Module |
|---|---|---|
| `StableDiffusionAdapter` | Stable Diffusion WebUI (A1111) | `stable_diffusion_adapter.py` |
| `MockImageProvider` | In-process placeholder | `mock_image_provider.py` |

### Configuration

```env
IMAGE_PROVIDER=stable_diffusion   # stable_diffusion | mock
IMAGE_PROVIDER_API_URL=http://localhost:7860
IMAGE_PROVIDER_API_KEY=           # leave empty if not required
IMAGE_PROVIDER_MODEL=sd_xl_base_1.0
IMAGE_PROVIDER_TIMEOUT=120
IMAGE_PROVIDER_MAX_RETRIES=3
```

### Adding a New Image Provider

1. Create `apps/api/app/providers/my_provider_adapter.py`:

```python
from app.providers.image_provider import (
    ImageProviderAdapter,
    ImageGenerationResult,
    ProviderError,
)

class MyProviderAdapter(ImageProviderAdapter):
    def __init__(self, api_key: str, timeout: int = 60):
        super().__init__(provider_name="my_provider")
        self.api_key = api_key
        self.timeout = timeout

    def generate_image(
        self,
        prompt: str,
        negative_prompt=None,
        width: int = 1080,
        height: int = 1920,
        style=None,
        shot_id=None,
        **kwargs,
    ) -> ImageGenerationResult:
        self.validate_parameters(prompt, width, height)

        try:
            # 1. Convert to provider-specific format
            payload = {"prompt": prompt, "size": f"{width}x{height}"}

            # 2. Call provider API
            response = self._call_api(payload)

            # 3. Parse response into ImageGenerationResult
            return ImageGenerationResult(
                success=True,
                image_data=response["image_bytes"],
                width=width,
                height=height,
                format="png",
                shot_id=shot_id,
                request_id=response.get("id"),
            )
        except Exception as e:
            raise ProviderError(
                message=str(e),
                provider_name=self.provider_name,
                is_retryable=True,
            )
```

2. Register in `apps/api/app/providers/image_provider_factory.py`:

```python
from .my_provider_adapter import MyProviderAdapter

class ImageProviderFactory:
    @classmethod
    def create_provider(cls, provider_type=None, **override_params):
        provider_type = provider_type or settings.image_provider
        if provider_type == "my_provider":
            return MyProviderAdapter(
                api_key=settings.image_provider_api_key,
                **override_params,
            )
        # ... existing cases
```

3. Set `IMAGE_PROVIDER=my_provider` in `.env` — no other changes needed.

---

## TTS Provider

### Interface

`app/providers/tts_provider.py`

```python
class TTSProviderAdapter(ABC):
    def synthesize_speech(
        self,
        text: str,
        voice: str,
        language: str = "zh-CN",
        speed: float = 1.0,
        shot_id: Optional[UUID] = None,
        **kwargs,
    ) -> TTSResult: ...
```

`TTSResult` fields:

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Whether synthesis succeeded |
| `audio_data` | `bytes \| None` | Raw MP3/WAV bytes |
| `audio_format` | `str \| None` | `"mp3"` or `"wav"` |
| `duration_ms` | `int \| None` | Audio duration |
| `sample_rate` | `int \| None` | Hz |
| `channels` | `int \| None` | 1 = mono, 2 = stereo |
| `shot_id` | `UUID \| None` | Passed-through for tracking |
| `error` | `str \| None` | Error message on failure |
| `request_id` | `str \| None` | Provider's request ID |
| `character_count` | `int \| None` | Characters synthesized (cost tracking) |

### Built-in Adapters

| Class | Provider | Module |
|---|---|---|
| `AzureTTSAdapter` | Azure Cognitive Services TTS | `azure_tts_adapter.py` |
| `MockTTSProvider` | In-process silence generator | `mock_tts_provider.py` |

### Configuration

```env
TTS_PROVIDER=mock                          # azure | mock
TTS_AZURE_SUBSCRIPTION_KEY=<your-key>
TTS_AZURE_REGION=eastus
TTS_DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
TTS_DEFAULT_LANGUAGE=zh-CN
TTS_OUTPUT_FORMAT=audio-16khz-128kbitrate-mono-mp3
TTS_TIMEOUT=30
TTS_MAX_RETRIES=3
```

### Adding a New TTS Provider

1. Create `apps/api/app/providers/elevenlabs_adapter.py`:

```python
from app.providers.tts_provider import TTSProviderAdapter, TTSResult, TTSProviderError

class ElevenLabsAdapter(TTSProviderAdapter):
    def __init__(self, api_key: str, timeout: int = 30):
        super().__init__(provider_name="elevenlabs")
        self.api_key = api_key
        self.timeout = timeout

    def synthesize_speech(
        self,
        text: str,
        voice: str,
        language: str = "zh-CN",
        speed: float = 1.0,
        shot_id=None,
        **kwargs,
    ) -> TTSResult:
        self.validate_parameters(text, speed)

        try:
            # 1. Convert to ElevenLabs format
            payload = {"text": text, "voice_id": voice, "model_id": "eleven_multilingual_v2"}

            # 2. Call API
            audio_bytes = self._call_api(payload)

            # 3. Return standardised result
            return TTSResult(
                success=True,
                audio_data=audio_bytes,
                audio_format="mp3",
                shot_id=shot_id,
                character_count=len(text),
            )
        except Exception as e:
            raise TTSProviderError(
                message=str(e),
                provider_name=self.provider_name,
                is_retryable=True,
            )
```

2. Register in `apps/api/app/providers/tts_provider_factory.py`:

```python
from .elevenlabs_adapter import ElevenLabsAdapter

class TTSProviderFactory:
    @classmethod
    def create_provider(cls, provider_type=None, **override_params):
        provider_type = provider_type or settings.tts_provider
        if provider_type == "elevenlabs":
            return ElevenLabsAdapter(
                api_key=settings.tts_azure_subscription_key,  # reuse key field or add new
                **override_params,
            )
        # ... existing cases
```

3. Set `TTS_PROVIDER=elevenlabs` in `.env`.

---

## Error Handling

Both `ProviderError` and `TTSProviderError` carry an `is_retryable` flag:

| `is_retryable` | Trigger | Action |
|---|---|---|
| `True` | Network timeout, 429 rate-limit, 5xx | Exponential backoff retry (up to `MAX_RETRIES`) |
| `False` | 400 bad request, 401/403 auth error | Fail immediately, log error |

```python
try:
    result = provider.generate_image(prompt=prompt)
except ProviderError as e:
    if e.is_retryable:
        logger.warning(f"Retryable error from {e.provider_name}: {e}")
    else:
        logger.error(f"Permanent error from {e.provider_name}: {e}")
```

## Requirements Coverage

| Requirement | Description |
|---|---|
| 3.1 / 6.1 | Unified adapter interface |
| 3.2 / 6.2 | Parameter conversion |
| 3.3 / 6.3 | Response normalisation |
| 3.4 / 6.4 | Error recording with `request_id` |
| 3.5 / 6.5 | Provider switching via config only |
