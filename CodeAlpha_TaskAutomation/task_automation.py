import re
import shutil
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TITLE_PATTERN = re.compile(r"<title\b[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def move_files() -> None:
    source_text = input("Enter the source folder: ").strip()
    destination_text = input("Enter the destination folder: ").strip()
    if not source_text or not destination_text:
        print("Source and destination folders are required.")
        return

    source = Path(source_text).expanduser()
    destination = Path(destination_text).expanduser()

    if not source.is_dir():
        print(f"Source folder does not exist: {source}")
        return
    try:
        if source.resolve() == destination.resolve():
            print("Source and destination folders must be different.")
            return
        if destination.resolve().is_relative_to(source.resolve()):
            print("Destination cannot be inside the source folder.")
            return
    except OSError as error:
        print(f"Could not validate the folder paths: {error}")
        return

    try:
        destination.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Could not create the destination folder: {error}")
        return
    moved_count = 0
    try:
        for item in source.iterdir():
            if item.is_file():
                target = destination / item.name
                if target.exists():
                    print(f"Skipped existing file: {target.name}")
                    continue
                shutil.move(str(item), str(target))
                moved_count += 1
    except OSError as error:
        print(f"Could not move files: {error}")
        return

    print(f"Moved {moved_count} file(s) to {destination}.")


def extract_emails() -> None:
    source = Path(input("Enter the input .txt file: ").strip()).expanduser()
    output = Path(input("Enter the output file (default: emails.txt): ").strip() or "emails.txt")

    if not source.is_file():
        print(f"Input file does not exist: {source}")
        return
    if source.suffix.lower() != ".txt":
        print("Input file must have a .txt extension.")
        return
    if output.suffix.lower() != ".txt":
        print("Output file must have a .txt extension.")
        return
    if source.resolve() == output.resolve():
        print("Input and output files must be different.")
        return

    try:
        text = source.read_text(encoding="utf-8")
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Could not read the input or prepare the output: {error}")
        return
    emails = sorted(set(EMAIL_PATTERN.findall(text)))
    try:
        output.write_text(
            "\n".join(emails) + ("\n" if emails else ""), encoding="utf-8"
        )
    except OSError as error:
        print(f"Could not save the extracted emails: {error}")
        return
    print(f"Extracted {len(emails)} unique email address(es) to {output}.")


def scrape_title() -> None:
    url = input("Enter the webpage URL: ").strip()
    output = Path(input("Enter the output file (default: page_title.txt): ").strip() or "page_title.txt")

    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        print("Please enter a URL beginning with http:// or https://.")
        return
    if output.suffix.lower() != ".txt":
        print("Output file must have a .txt extension.")
        return

    request = Request(url, headers={"User-Agent": "TaskAutomation/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            html = response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"Could not retrieve the webpage: {error}")
        return

    match = TITLE_PATTERN.search(html)
    if not match:
        print("The webpage does not contain a title.")
        return

    title = re.sub(r"\s+", " ", match.group(1)).strip()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(title + "\n", encoding="utf-8")
    except OSError as error:
        print(f"Could not save the page title: {error}")
        return
    print(f"Page title saved to {output}: {title}")


def main() -> None:
    actions = {
        "1": ("Move files to another folder", move_files),
        "2": ("Extract email addresses from a text file", extract_emails),
        "3": ("Scrape a webpage title", scrape_title),
    }

    print("Task Automation with Python Scripts")
    print("====================================")
    for number, (description, _) in actions.items():
        print(f"{number}. {description}")

    choice = input("Choose an option (1-3): ").strip()
    action = actions.get(choice)
    if action is None:
        print("Invalid choice. Please select 1, 2, or 3.")
        return

    action[1]()


if __name__ == "__main__":
    main()
