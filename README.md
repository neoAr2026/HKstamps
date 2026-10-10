# hkstamps — Hong Kong Stamps before 1997

Files
- index.html      the website (open it in any browser; one self-contained page)
- template.html   the page design; edit this, not index.html
- build_site.py   rebuilds index.html from the checklist spreadsheet

Rebuild after changing the spreadsheet
    pip install openpyxl
    python3 build_site.py Hong_Kong_Scott_Checklist.xlsx index.html

Spreadsheet columns the site reads (by header name)
- SG No.          add this column; the site shows it on the left
- Sell price ($)  add this column; your asking price in US$
- Qty held        a stamp shows "Available" only with a sell price AND Qty held >= 2
                  (you keep one, sell the duplicates)
- Status          type Sold to mark a stamp sold

Checkout (in template.html, CONFIG near the top of the script)
- paypalClientId  paste your PayPal SANDBOX client ID to test; live ID when ready
- postage         placeholder US$ amounts for California / rest of US / international
- taxRate         0.0725 = California base sales tax (local district rates add more)

Photos: every stamp page has a placeholder slot. Home-page monarch heads are in img/ (qv, e7, g5, g6, qe2 .jpg); replace them with your own photos and rebuild.
