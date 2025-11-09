import json
from base64 import b64decode
from typing import List

import requests

from src.config.config import config

github_url = config["GITHUB_URL"]
github_token = config["GITHUB_TOKEN"]

headers: dict = {
    "Authorization": "token " + github_token,
    "Accept": "application/vnd.github.v3+json",
}


# Decode a base64 string
def decoding_base64(input_message: str) -> str:
    """
    Args:
        input_message (str): The base64 string

    Returns:
        str: The decoded string
    """
    # Encodes the input message in base64 ASCII
    base64_bytes: bytes = input_message.encode("ascii")

    # Decodes the base64 ASCII
    message_bytes: bytes = b64decode(base64_bytes)

    # Returns the decoded string
    return message_bytes.decode("ascii")


# Get the list of new mangas from GitHub
def get_list_new_manga() -> List[str]:
    """
    Args:

    Returns:
        List[str]: A list of new mangas
    """

    # Get the content of the GitHub file
    r: requests.Response = requests.get(github_url, headers=headers, stream=True)

    # If the request was successful
    if r.status_code == requests.codes.ok:
        # Get the content of the GitHub file
        content_base64: str = json.loads(r.text)["content"].strip()
        # Decode the content
        github_content: str = decoding_base64(content_base64)
        # If the content is not None
        if github_content != "None":
            # Return the list of new mangas
            return list(dict.fromkeys(github_content.splitlines()))
        else:
            # Return an empty list
            return []


# Clear the list of new mangas
def clear_list_new_manga() -> None:
    """
    Args:

    Returns:
        None
    """
    # Get the content of the GitHub file
    r = requests.get(github_url, headers=headers, stream=True)
    # Get the SHA of the file
    sha = json.loads(r.text)["sha"]
    # Tm9uZQ== => None
    input_data = {"message": "Update file", "content": "Tm9uZQ==", "sha": sha}
    # Update the file
    requests.put(github_url, headers=headers, data=json.dumps(input_data))
