# Docker webinar

### Running the twitter_elastic as console
1. Build the image: *docker build -t webinar-twitter:latest .*
2. Create a twitter.env file. Use twitter credentials ( https://iag.me/socialmedia/how-to-create-a-twitter-app-in-8-easy-steps/ )  
The env file should be as following:  
CONSUMER_KEY=[consumer key here]  
CONSUMER_SECRET=[consumer secret]  
ACCESS_TOKEN=[access token key]  
ACCESS_TOKEN_SECRET=[access token secret]  
ELASTICSEARCH_HOST=elasticsearch  
3. Run the container: *docker run -it --env-file twitter.env webinar-twitter

### Running the Elasticsearch, Kibana and twitter_elastic
1. Create the twitter.env as described in the section above
2. Use docker-compose up
3. Import into Kibana the twitter_visulazations.json and the twitter_kibana.json
