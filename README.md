# Historical Flow of Funds (Financial Accounts) Data Downloader

The `fof` module contains python functions that make it easy to download and parse historical Flow of Funds data. The Fed Board makes it avaiable in SDMX (XML variant) format. This module will parse it into a more user-friendly CSV, which can then be read by any statistical application.

It is lightweight. The only dependency is `requests`, and even it can be avoided by parsing a previously downloaded and unzipped dataset.

Example usage is in the `example.ipynb` Jupyter notebook.

Additional examples showing what the data looks like and how to use it are in `wrangling_examples.ipynb`. TO run this, you will need `pandas`.

I've debugged this extensively, but use at your own risk. I won't be able to answer questions or otherwise provide support.
