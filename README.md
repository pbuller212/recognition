# Handwriting recognition

This is a simple proof of concept for a veterinary office using OpenAI to transcribe handwritten notes that have been scanned into PDF's and return text, creating the ability to search later.

## Setup and run

1. Clone the repository.
2. Set your api key in a .env file like so:
```
OPENAI_KEY=use-a-better-key
```
3. Run the application
```
uv run main.py
```

## Uploading files

This is just done in the admin at http://localhost:8000/admin

Then by going to http://8000, you can view files, whether they have been submitted, and the results if the file has been tried.
