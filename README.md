# Parldl

Download files parallely from a list of URLs in a file.

## Installation

###### Recommended

```bash
pipx install parldl
```
(To install pipx click [here](https://github.com/pypa/pipx#install-pipx))

###### or

```bash
pip install parldl
```

#### Or upgrade by:

```bash
pipx upgrade parldl
```

###### or

```bash
pip install --upgrade parldl
```

## Usage

1. Create a file containing a list of URLs, one URL per line.
2. Run `parldl` with the path to the file as an argument.
3. `parldl` will download the images and save them in a directory provided or in "pardl-downloads" by default.

## Example

```bash
parldl image_urls.txt output_dir
```

```bash
parldl image_urls.txt
```

```
Usage: parldl [OPTIONS] [URL_FILE] [OUTPUT_DIR]

  Download files parallely from a list of URLs in a file

Options:
  -i, --input PATH            File containing newline-separated URLs
  -o, --output PATH           Output directory path
  -m, --max-attempts INTEGER  Maximum number of download attempts
  -p, --parallel INTEGER      Maximum number of parallel downloads
  --help                      Show this message and exit.
```

# Install from source

Poetry is required. For installation click [here](https://python-poetry.org/docs/#installation).

Download the source and install the dependencies by running:

  ```bash
  git clone https://github.com/aqdasak/parldl.git
  cd parldl
  poetry install
  ```

### Run

In the source folder containing pyproject.toml

```bash
poetry shell
```

then cd into the folder containing url file and execute:

```bash
parldl <url_file> <output_dir>
```

## License

This project is licensed under the MIT License.
