# coinmarketcap-pro-exporter
Forked from https://github.com/bonovoxly/coinmarketcap-exporter

A prometheus exporter for https://pro.coinmarketcap.com/.  
Provides Prometheus metrics from the [`Quotes Latest API`](https://pro.coinmarketcap.com/api/v1#operation/getV1CryptocurrencyQuotesLatest) of CoinMarketCap, such as US price, Bitcoin price, etc.

## Setup
1. Get your CoinMarketCap API KEY.  
https://pro.coinmarketcap.com/signup/
2. Please check all the necessary CoinMarketCap Currency IDs.  
[Standards and Conventions](https://pro.coinmarketcap.com/api/v1#section/Standards-and-Conventions)  
For a current list of supported cryptocurrencies use the `/cryptocurrency/map` API call.

    Example:  

    | Currency | CoinMarketCap ID |
    |---|---|
    | Bitcoin | 1 |
    | Ethereum | 1027 |
    | United States Dollar ($) | 2781 |
    | Japanese Yen (¥) | 2797 |

3. Run docker container while listening on localhost:9100:
    ```
    docker build -t coinmarketcap-pro-exporter:latest .

    docker run -e API_KEY=[ CoinMarketCap APIKEY] -e CoinID=[ID1,ID2,ID3...] -p 127.0.0.1:9101:9101 coinmarketcap-pro-exporter:latest
    ```
    or pull image from docker-hub
    ```
    docker run -e API_KEY=[CoinMarketCap APIKEY] -e CoinID=[ID1,ID2,ID3...] -p 9101:9101 naoyain/coinmarketcap-pro-exporter
    ```
# prometheus.yml
API calls must be every 300 seconds over. 
```Yaml
...
scrape_configs:
  - job_name: 'coinmarketcap-pro-exporter'
    # Override the global default and scrape targets from this job every 300 seconds, overwise API calls limits have been reached soon.
    scrape_interval: 300s
    static_configs:
      - targets: ['coinmarketcap-pro-exporter:9101']
```
# Testing the Prometheus Grafana Stack

- In the `prometheus-compose` directory,  
overwrite `[CoinMarketCap API KEY]` and `[CoinMarketCap currency IDs]`

- run:
    ```sh
    docker-compose up
    ```
- Go to <http://localhost:3000>.  Log in as `admin/admin`.
- To import the dashboard, click the "Home" button at the top, then on the right, click "Import Dashboard".
- Enter `3890` in the "Grafana.com Dashboard" field.
- Select the "prometheus" data source.
- Modify the other settings as preferred. Click "Import".
- The new dashboard should be selectable and found at <http://localhost:3000/dashboard/db/coinmarketcap-single>.
- The Prometheus interface can be accessed at <http://localhost:9090>