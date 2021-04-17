# Rocket League + Spotify API

## Prerequisites

- `Python 3.8+`
- `MongoDB`

_included in most Python 3 distributions_

- `setuptools>=42`
- `wheel`

## Running

1. `cd rocketleague-spotify-api`
2. open `src/rocketleague_spotify/data/.env` and change the `MONGO_URL` to your own endpoint if necessary
3. `pip install .` (or `pip install -e .[test]` for development)
4. `python -m rocketleague_spotify` or `python3 -m rocketleague_spotify` depending on your environment

## Testing

To run the tests against the code itself (useful for debugging):

- `pytest .`

To run the tests against a running server (local or remote), set the `TEST_URL` environment variable to your endpoint, with no trailing `/`

On Linux:

- `TEST_URL="http://localhost:8000" pytest .`

On Windows:

- `$env:TEST_URL="http://localhost:8000"; pytest .; Remove-Item Env:\TEST_URL`