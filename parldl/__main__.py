import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import click
import requests

Success = bool
Error = str | None


def download_image(url: str, output_dir: Path) -> tuple[Success, Error]:
    """
    Return:
    -------
    success: bool
        True if the download was successful, False otherwise.
    error: str | None
        None if the download was successful, an error message otherwise.
    """

    filename = Path(urlparse(url).path).name
    filepath = output_dir / filename

    try:
        response = requests.get(url, timeout=30)  # Add a timeout
        if response.status_code == 200:
            filepath.write_bytes(response.content)
            return True, None
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


def download_images(urls: list[str], output_dir: Path, *, max_attempts, max_workers):
    def _download_images(urls: list[str]) -> list[str]:
        """
        Return:
        -------
        failed_urls: list[str]
            List of URLs that failed to download.
        """

        success_count = 0
        fail_count = 0
        total_urls = len(urls)

        # Use a deque for maintaining order and allowing duplicates for retries
        pending_urls = deque(urls)
        failed_forever_urls = []
        future_to_url = {}
        url_to_attempts = {url: 1 for url in urls}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while pending_urls or future_to_url:
                # Submit new tasks for pending URLs
                while len(future_to_url) < max_workers and pending_urls:
                    url = pending_urls.popleft()
                    future = executor.submit(download_image, url, output_dir)
                    future_to_url[future] = url

                # Check for completed futures without blocking
                for future in [f for f in future_to_url if f.done()]:
                    success, error = future.result()
                    url = future_to_url.pop(future)

                    if success:
                        success_count += 1
                    elif (
                        error.startswith("HTTP 5")
                        or
                        # Only HTTP 5xx errors are retried
                        not error.startswith("HTTP")
                        and url_to_attempts[url] < max_attempts
                    ):
                        pending_urls.append(url)
                        url_to_attempts[url] += 1
                    else:
                        failed_forever_urls.append(url)
                        fail_count += 1

                print(
                    f" Downloaded: {success_count}/{total_urls}"
                    f" | Processing: {len(future_to_url)}"
                    f" | Pending: {len(pending_urls)}"
                    f" | Failed: {fail_count}",
                    "        ",
                    end="\r",
                    flush=True,
                )

                # Short sleep to prevent CPU spinning
                time.sleep(0.2)

        return failed_forever_urls

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    failed_urls = _download_images(urls)

    fail_count = len(failed_urls)
    success_count = len(urls) - fail_count

    if success_count > 0:
        print(f"\n\n Successfully downloaded: {success_count}")

    if fail_count > 0:
        print(f" Failed to download: {fail_count}")
        print(" Failed:")
        print("", "\n ".join(failed_urls))


@click.command()
@click.argument("url_file", type=click.Path(exists=True), required=False)
@click.argument("output_dir", type=click.Path(), required=False)
@click.option(
    "-i",
    "--input",
    "url_file_opt",
    type=click.Path(exists=True),
    help="File containing newline-separated URLs",
)
@click.option(
    "-o", "--output", "output_dir_opt", type=click.Path(), help="Output directory path"
)
@click.option(
    "-m", "--max-attempts", default=5, help="Maximum number of download attempts"
)
@click.option(
    "-p", "--parallel", default=8, help="Maximum number of parallel downloads"
)
def main(url_file, output_dir, url_file_opt, output_dir_opt, max_attempts, parallel):
    """
    Download files parallely from a list of URLs in a file
    """

    # Determine input file
    if url_file_opt:
        url_file_name = url_file_opt
    elif url_file:
        url_file_name = url_file
    else:
        raise click.UsageError(
            "Input file is required. Use -i or provide it as the first argument."
        )

    # Determine output file
    if output_dir_opt:
        output_dir_name = output_dir_opt
    elif output_dir:
        output_dir_name = output_dir
    else:
        output_dir_name = "pardl-downloads"
        click.echo(f" Using default output directory: {output_dir_name}")

    # Convert paths to Path objects
    url_file_path = Path(url_file_name)
    output_dir_path = Path(output_dir_name)

    # Read URLs from file
    urls = url_file_path.read_text().splitlines()
    urls = {url.strip() for url in urls}
    if "" in urls:
        urls.remove("")
    urls = list(urls)

    # Print the configuration
    print(f" URL file: {url_file_name}")
    print(f" Output directory: {output_dir_name}")
    print(f" Max attempts: {max_attempts}")
    print(f" Parallel downloads: {parallel}\n")

    download_images(
        urls, output_dir_path, max_attempts=max_attempts, max_workers=parallel
    )


if __name__ == "__main__":
    main()
