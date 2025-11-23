import os
import sys

def main():
	from ui.app import run
	port = int(os.environ.get("PORT", "5000"))
	run(port=port)


if __name__ == "__main__":
	main()
