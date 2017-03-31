import tweepy
import elasticsearch
import os
import sys
import collections
import datetime
import time
import requests

TWITTER_PARAMS = ["CONSUMER_KEY","CONSUMER_SECRET","ACCESS_TOKEN",
"ACCESS_TOKEN_SECRET"]

def main(args):
    print("hello webinar")
    use_elasticsearch = os.getenv("USE_ELASTICSEARCH", False) == "True"
    if use_elasticsearch:
        listener = create_elasticlistener()
    else:
        listener = ConsoleListener()

    terms = args or ["trump", "usa", "obama", "docker", "vm"]
    api = get_twitter_api()
    stream = tweepy.Stream(auth=api.auth, listener=listener)
    print("starting with the terms {0}".format(",".join(terms)))

    stream.filter(track=terms, async=False)

def get_twitter_api():
    for param in TWITTER_PARAMS:
        if not os.getenv(param):
            print("{0} env param is missing".format(param))
            sys.exit(1)
    auth = tweepy.OAuthHandler(os.getenv("CONSUMER_KEY"),
                               os.getenv("CONSUMER_SECRET"))
    auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET"))
    api = tweepy.API(auth)
    return api


class ElasticListener(tweepy.StreamListener):
    def __init__(self, elasticsearh_host):
        super().__init__()
        self.elastic_client = elasticsearch.Elasticsearch(
            hosts=[elasticsearh_host],
            http_auth=("elastic", "changeme"))
        self.verify_index()
        print("elastic listener started")

    def verify_index(self):
        verified = False
        while not verified:
            pass
            try:
                self.elastic_client.get(index="tweets", id=1)
                verified = True
            except:
                try:
                    self.elastic_client.create(index="tweets",
                                           doc_type="tweets",
                                           body=index_body,
                                           id=1)
                    verified = True
                except:
                    time.sleep(5)

    def on_status(self, status):
        timestamp = datetime.datetime.utcfromtimestamp(int(status.timestamp_ms) / 1000)
        try:
            tweet = {
                "timestamp": timestamp,
                "entities": status._json["entities"],
                "text": status._json["text"],
                "coordinates": status._json["coordinates"],
                "user": status._json["user"],
                "created_at": status.created_at,
            }
            self.elastic_client.index("tweets", body=tweet, doc_type="tweets")
        except Exception as e:
            print(e)
            pass


class ConsoleListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__()
        self.statistics = collections.Counter()
        self.hash_tags = collections.Counter()
        print("console initialized")

    def on_status(self, status):
        self.statistics["tweets"] += 1
        for hashtag in status.entities["hashtags"]:
            hashtag_text = hashtag["text"]
            self.hash_tags[hashtag_text] += 1
        if self.statistics["tweets"] % 100 == 0:
            self.print()

    def print(self):
        print(str(self) + " " * 100)  # , end="\r")

    def __str__(self):
        return ">>> Tweets: {0}, Top hashtag {1} ".format(
            self.statistics["tweets"],
            self.hash_tags.most_common(5)
        )


def create_elasticlistener():
    while True:
        try:
            elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
            if requests.get("http://elastic:changeme@{0}:9200/".format(
                    elasticsearch_host)).status_code != 200:
                time.sleep(20)
                continue
            print("connecting to ",elasticsearch_host)
            return ElasticListener(elasticsearch_host)
        except:
            time.sleep(5)




index_body = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "_default_": {
            "_all": {
                "enabled": True
            },
            "properties": {
                "@timestamp": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss.SSS"
                },
                "timestamp": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss.SSS"
                },
                "createdAd": {
                    "type": "date",
                },
                "text": {
                    "type": "text"
                },
                "user": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "text"
                        }
                    }
                },
                "coordinates": {
                    "type": "object",
                    "properties": {
                        "coordinates": {
                            "type": "geo_point"
                        }
                    }
                },
                "entities": {
                    "type": "object",
                    "properties": {
                        "hashtags": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "text",
                                    "fielddata": True
                                }
                            }
                        }
                    }
                },
                "retweeted_status": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "text"
                        }
                    }
                }
            },
            "dynamic_templates": [
                {
                    "string_template": {
                        "match": "*",
                        "match_mapping_type": "string",
                        "mapping": {
                            "type": "keyword"
                        }
                    }
                }
            ]
        }
    }
}

if __name__ == "__main__":
    main(sys.argv[1:])
