---
title: "MVT API"
bookToc: true
navHide: true
---

In order to promote transparency and accountability at crypto trading venues, we are publishing a set of API specifications called Market Venue Transparency API (MVT API). Its goal is to facilitate the collection and analysis of the order-level data enriched with Anonymized Trader IDs.

## Order-level data enriched with Anonymized Trader ID

### Schema

```
{
  "fields": [
    {
      "description": "Data provider anonymized ID",
      "name": "source",
      "type": "string"
    },
    {
      "description": "Market unique identifier - combination of a market venue name and a pair identifier",
      "name": "marketId",
      "type": "string"
    },
    {
      "description": "Timestamp in milliseconds reported by exchange",
      "name": "timestamp",
      "type": "long"
    },
    {
      "description": "Timestamp in milliseconds when event received from exchange",
      "name": "receiveTimestamp",
      "type": "long"
    },
    {
      "description": "Ask orders",
      "name": "asks",
      "type": [
        {
          "items": {
            "description": "Order-level information about the changes in the orderbook",
            "fields": [
              {
                "description": "Order price in the quote currency",
                "name": "price",
                "type": "numeric"
              },
              {
                "description": "Order size in the base currency; absolute value",
                "name": "size",
                "type": "numeric"
              },
              {
                "description": "Anonymized ID of the account initiating the order",
                "name": "accountId",
                "type": "string"
              },
              {

                "description": "Anonymized ID of the subaccount initiating the order",
                "name": "subaccountId",
                "type": "string"
            },
              {
                "description": "Order type",
                "name": "orderType",
                "type": "string"
              },
              {
                "description": "Unique order ID",
                "name": "orderId",
                "type": "string"
              }
            ],
            "name": "OrderDelta",
            "type": "record"
          },
          "type": "array"
        }
      ]
    },
    {
      "description": "Bid orders",
      "name": "bids",
      "type": [
        {
          "items": "OrderDelta",
          "type": "array"
        }
      ]
    }
  ],
  "name": "OrderBookApiStandard",
  "type": "record"
}
```

### Table

| field            | description                                                                         |
| :--------------- | :---------------------------------------------------------------------------------- | ----- | --------------------------------- |
| source           | Data provider anonymized ID                                                         |
| marketId         | Market unique identifier - combination of a market venue name and a pair identifier |
| timestamp        | Timestamp in milliseconds reported by exchange                                      |
| receiveTimestamp | Timestamp in milliseconds when event received from exchange                         |
| asks             | Ask orders                                                                          | price | Order price in the quote currency |
| size             | Order size in the base currency; absolute value                                     |
| accountId        | Anonymized ID of the account initiating the order                                   |
| subaccountId     | Anonymized ID of the subaccount initiating the order                                |
| orderType        | Order type                                                                          |
| orderId          | Unique order ID                                                                     |
| bids             | Bid orders                                                                          | price | Order price in the quote currency |
| size             | Order size in the base currency; absolute value                                     |
| accountId        | Anonymized ID of the account initiating the order                                   |
| subaccountId     | Anonymized ID of the subaccount initiating the order                                |
| orderType        | Order type                                                                          |
| orderId          | Unique order ID                                                                     |

## Trade-level data enriched with Anonymized Trader ID

### Schema

```
{
  "fields": [
    {
      "description": "Data provider anonymized ID",
      "name": "source",
      "type": "string"
    },
    {
      "description": "Market unique identifier - combination of a market venue name and a pair identifier",
      "name": "marketId",
      "type": "string"
    },
    {
      "description": "Timestamp in milliseconds reported by exchange",
      "name": "timestamp",
      "type": "long"
    },
    {
      "description": "Timestamp in milliseconds when event received from exchange",
      "name": "receiveTimestamp",
      "type": "long"
    },
    {
      "description": "Execution price in the quote currency",
      "name": "price",
      "type": "numeric"
    },
    {
      "description": "Order size in the base currency; absolute value",
      "name": "size",
      "type": "numeric"
    },
    {
      "description": "",
      "name": "side",
      "type": "string"
    },
    {
      "description": "",
      "name": "accountId",
      "type": "string"
    },
    {
      "description": "",
      "name": "takerAccountId",
      "type": "string"
    },
    {
      "description": "",
      "name": "orderId",
      "type": "string"
    },
    {
      "description": "",
      "name": "takerOrderId",
      "type": "string"
    }
  ],
  "name": "TradeApiStandard",
  "type": "record"
}
```

### Table

| field            | description                                                                           |
| :--------------- | :------------------------------------------------------------------------------------ |
| source           | Data provider anonymized ID                                                           |
| marketId         | Market unique identifier - combination of a market venue name and a pair identifier   |
| timestamp        | Timestamp in milliseconds reported by exchange                                        |
| receiveTimestamp | Timestamp in milliseconds when event received from exchange                           |
| price            | Execution price in the quote currency                                                 |
| size             | Order size in the base currency; absolute value                                       |
| side             | The side of the market taker (aggressor side)                                         |
| accountId        | A unique identifier of the market maker's account associated with the trade execution |
| takerAccountId   | A unique identifier of the market taker's account associated with the trade execution |
| orderId          | A unique identifier of the market maker's order associated with the trade execution   |
| takerOrderId     | A unique identifier of the market taker's order associated with the trade execution   |
