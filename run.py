import os

from dotenv import load_dotenv

from zshort import app

if __name__ == "__main__":
    import uvicorn

    load_dotenv()
    if not all(os.environ.get(f"MONGO_{x}") for x in ["HOST", "USER", "PASS"]):
        print(
            "Missing MongoDB connection data! Make sure MONGO_HOST, "
            "MONGO_USER, and MONGO_PASS are defined in .env"
        )
        exit(1)
    uvicorn.run(app, host="0.0.0.0", port=8000)
