# Data dictionary

## Source tables

| Table | Grain | Key fields | Purpose |
| --- | --- | --- | --- |
| `customers` | One row per synthetic customer | `customer_id` | Region, acquisition and loyalty context |
| `products` | One row per SKU | `product_id` | Category, list price and standard unit cost |
| `stores` | One row per location | `store_id` | City, region and store format |
| `campaigns` | One row per campaign | `campaign_id` | Flight dates, media channel and spend |
| `orders` | One row per order | `order_id` | Date, channel, status, customer and optional campaign/store |
| `order_lines` | One row per order-product line | `order_id`, `line_number` | Quantity, realized price, cost and discount |

## Canonical calculated measures

| Measure | Definition |
| --- | --- |
| Net revenue | Completed-order `quantity × unit_price × (1 − discount_pct)` |
| Gross profit | Net revenue minus completed-order `quantity × unit_cost` |
| Gross margin | Gross profit divided by net revenue |
| Average order value | Net revenue divided by distinct completed orders |
| Return rate | Returned orders divided by all orders |
| YoY revenue growth | Current-month revenue divided by the same month one year earlier, minus one |
| Attributed ROAS | Revenue linked to a campaign divided by campaign spend; descriptive only |

## Customer segments

Segments use transparent recency, frequency and monetary rules. They are activation hypotheses, not immutable customer labels. Thresholds live in `src/retail_analytics/analytics.py` and should be recalibrated on real business distributions.
