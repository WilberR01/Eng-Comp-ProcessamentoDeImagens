"""Centralized error handling and user-friendly messages for analysis pipeline.

This module exposes helpers to format exceptions into a small dict that the
UI can present to the user with a suggestion and whether retrying might help.
"""
from typing import Dict


def format_exception(e: Exception) -> Dict[str, str]:
    """Return a structured, user-friendly representation for an exception.

    Keys:
      - message: brief error message
      - suggestion: what the user can try next
      - can_retry: 'yes' or 'no'
    """
    msg = str(e)
    # Basic heuristics to provide suggestions — extend as needed
    suggestion = "Verifique o caminho/arquivo e tente novamente."
    can_retry = "yes"

    if isinstance(e, FileNotFoundError):
        suggestion = "Arquivo não encontrado. Confirme o caminho ou envie o arquivo novamente."
        can_retry = "yes"
    elif isinstance(e, PermissionError):
        suggestion = "Permissão negada. Execute com permissões adequadas ou altere as permissões do arquivo."
        can_retry = "no"
    else:
        # For unknown errors we suggest retry and contacting support if persists
        suggestion = "Ocorreu um erro inesperado. Tente novamente; se ocorrer novamente, verifique os logs."

    return {"message": msg, "suggestion": suggestion, "can_retry": can_retry}
