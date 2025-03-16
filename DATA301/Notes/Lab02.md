![[Pasted image 20250316223832.png]]
![[Pasted image 20250316223944.png]]

### 1. Top Ten Error Endpoints
```python
not_200 = data[data['response'] != 200] 
# I stated that it filters for records where the 'response' column is not equal to 200. This assumes the presence of a 'response' column with HTTP response codes.

endpoint_counts = not_200.groupby('url')['url'].count()
# I explained that it groups records by the 'url' column, implying that this column contains the requested URLs.

top_ten_err_URLs = endpoint_counts.nlargest(10)
# - This line selects the top 10 endpoints with the highest error counts using the `nlargest()` method.- top_ten_err_URLs`: This variable now contains a Dask Series with the top 10 error-prone endpoints and their corresponding error counts.

endpoint_sum = endpoint_counts.sum()
# - This line calculates the total number of errors across all endpoints by applying the `sum()` function to the `endpoint_counts` Series. `endpoint_sum`: This variable stores the total number of errors as a Dask scalar.
```
