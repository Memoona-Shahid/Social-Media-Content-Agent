from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response

from app.dependencies import get_built_prompt, require_built_prompt
from app.services.generator import (
    GeneratorError,
    generate_post,
    get_generation,
    save_generation,
    set_generation_error,
)
from app.services.prompt_builder import BuiltPrompt

router = APIRouter(tags=["generate"])


def _redirects_for(source: str) -> tuple[str, str]:
    if source == "output":
        return "/output?generated=1", "/output?error=1"
    return "/output?generated=1", "/compose?error=1"


@router.post("/generate", response_model=None)
def generate_from_form(
    request: Request,
    prompt: BuiltPrompt = Depends(get_built_prompt),
    source: str = Form("compose"),
) -> Response:
    success_url, error_url = _redirects_for(source)
    if not prompt.ready:
        set_generation_error(
            request.session,
            "Capture a topic and save a brand voice before generating.",
        )
        return RedirectResponse(url=error_url, status_code=status.HTTP_303_SEE_OTHER)

    try:
        result = generate_post(prompt)
    except GeneratorError as exc:
        set_generation_error(request.session, str(exc))
        return RedirectResponse(url=error_url, status_code=status.HTTP_303_SEE_OTHER)

    save_generation(request.session, result)
    return RedirectResponse(url=success_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/api/generate")
def generate_from_api(
    request: Request,
    prompt: BuiltPrompt = Depends(require_built_prompt),
) -> dict[str, object]:
    try:
        result = generate_post(prompt)
    except GeneratorError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    save_generation(request.session, result)
    return {"ok": True, **result.to_dict()}


@router.get("/api/generation")
def read_generation(request: Request) -> dict[str, object]:
    result = get_generation(request.session)
    if result is None:
        return {"generated": False, "content": ""}
    return {"generated": True, **result.to_dict()}
