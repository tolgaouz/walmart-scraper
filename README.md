# Install Dependencies

```
pip install selenium schedule requests
```

# How it works

This script loads links.txt and zip_codes.txt files and navigates to each link, checks if product is available for instore pickup
by rotating through all the available zip codes.

If a product is available a message is being sent to user on Telegram using their API.
