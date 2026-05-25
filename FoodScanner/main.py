from camera import start_camera
from config import GEMINI_API_KEY


def main():
    if not GEMINI_API_KEY:
        print("Missing GEMINI_API_KEY in .env")
        return

    start_camera()


if __name__ == "__main__":
    main()