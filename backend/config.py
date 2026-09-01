import os


def get_env_var(variable: str) -> str:
    value = os.getenv(variable)

    if value is None:
        raise RuntimeError("An error occured. Please try again.")

    return value
