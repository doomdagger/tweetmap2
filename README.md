# tweetmap2
Map your Twitter audience. Find where they live, what language they speak and engage them geographically. Share or download your results.

### Elasticsearch Mapping

```bash
curl -XPUT https://<your_es_endpoint>/_template/template_1 -d '
{
    "template": "tweets-*",
    "mappings": {
        "tweet": {
            "properties": {
                "location": {
                    "type": "geo_shape",
                    "tree": "quadtree",
                    "precision": "1m"
                },
                "place_id": {
                    "type": "string"
                },
                "polarity": {
                    "type": "double"
                },
                "subjectivity": {
                    "type": "double"
                },
                "text": {
                    "type": "string"
                },
                "timestamp_ms": {
                    "type": "double"
                },
                "tweet_id": {
                    "type": "string"
                },
                "user_id": {
                    "type": "string"
                },
                "user_profile_image": {
                    "type": "string"
                },
                "username": {
                    "type": "string"
                }
            }
        }
    }
}
'
```

