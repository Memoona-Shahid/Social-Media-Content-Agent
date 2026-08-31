from fastapi import APIRouter, Depends

from app.dependencies import get_built_prompt
from app.services.prompt_builder import BuiltPrompt

router = APIRouter(prefix="/api", tags=["prompt"])


@router.get("/prompt")
def read_prompt(prompt: BuiltPrompt = Depends(get_built_prompt)) -> dict[str, object]:
    return prompt.to_dict()
