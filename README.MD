# Pursuit Take Home

### A web scraper that identifies and prioritizes the highest-value links on a page

1. Allows adjustable keywords and importance criteria
2. Provides data access with a basic API
3. Employs scalable architecture

### This readme will provide an overview of the entire project
- Additional, more granular info can be found in docs/

# Quickstart 🚀
Follow these steps to run the project locally using Docker. 
### 1. Setup

#### Navigate to the ```app/``` directory and create a .env

```
cd app/
touch .env
```

#### fill .env with 
```
OPENAI_API_KEY=your-api-key
REDIS_URL="redis://redis:6379/0"
``` 
- The Redis url is local for this example

### 2. Running 

#### Ensure the Docker daemon is running: so have the desktop app open

#### Ensure your in the ```pursuit/``` directory 

```
cd pursuit/
```

#### Build the docker containers and start the service
```
docker compose build
docker compose up
```

#### Access the api at 

`http://0.0.0.0:8000 or localhost:8000`

#### For interactive documentation, go to the docs endpoint in the browser
` localhost:8000/docs`
- You can also view the **main.py** file and inspect the endpoints there

### (IMPORANT) this project ships with example data in the SQLite database
- to see what type of data this project has to offer, just GET the **/api/source-pages** , **/api/target-pages**, and **/api/statistics** endpoints: no OpenAI key needed! 


### 3. Cleanup 
#### When finished, stop containers

``` 
docker compose down
```

#### To clean up images, networks, volumes associated with this project

``` 
docker compose -f docker-compose.yml down --volumes --rmi local 
docker rmi redis:7-alpine
```

# High Level App Flow

1. ### User sends POST request to /scrape-url endpoint 

2. ### Server hands off to celery worker queue
    - Job is queued for background processing, does not block subsequent API requests
    - Creates a placeholder SourcePage table row
    - returns a UUID that can be used to access the job result at a later time
3. ### Celery task 
    - First places the original url into the **SourcePages** table, marked as **"PROCESSING"**
    - Scrapes all websites linked to from the original url
    - determines their relevance, keywords, filetype, and stores data in the **TargetPages** table
    - Once scraping is done, marks original url in SourcePages as **"COMPLETE"**
    - If an error occured, marks it as **"FAILED"**
4. ### Data API
    - see the api.md file and interactive api docs for descriptions
    

# Technology

1.  ### Relevance Heuristic
    - Relevance score determined by ChatGPT API querries. In this example I use GPT 3.5 turbo as it's the cheapest one i can use while prototyping, but other models can be used if desired
2.  ### Scapy Scraper
    - High performance web crawling framework 
    - Is given a starting website (root node) and performs a **depth first search** on the link graph
    - The maximum depth is specified as 2 here, but it can be changed to whatever
    - In essence, it will visit every hyperlink on the root page, extract its main text using **[Trafilatura](https://trafilatura.readthedocs.io/en/latest/index.html)**, and feed that into ChatGPT to rank its relvance 
3. ### **Celery**
    - Distrubuted task queue that allows for asynchronous execution of tasks
    - In this implementation, **Redis** is used as the message broker, although something like **RabbitMQ, Kafka, or ZeroMQ** could be used for this as well
    - A request is placed in a queue until one of the celery workers is available and can pick it up 
    - This allows for the user to send upwards of **thousands** of website scraping requests to the url endpoint, and come back later once its finished
        - **This is assuming the scaling suggestions are implemented** 


# Scaling Suggestions
1. ### Swap to PostgreSQL
    - SQlite is used here for simplicity, but the **high number of writes** needed for a production workload would require a more robust database like PostgreSQL
2. ### Increace # of Workers
    - Horizontally scale Celery by increacing the number of workers
    - Ideally, this can be done automatically based on the load experienced
3. ### Modify Celery Multithreading
    - As is, there is a bug with Celery and Scrapy that prevents a celery worker from performing more than 1 task total.
    - This is caused ```twisted.internet.reactor```, which Celery and Scrapy both try to control 
    - This causes the reactor state to become broken for a given worker, and as such further tasks with that worker will do nothing
    - This can be simply solved by adding the setting \
    ```--max-tasks-per-child=1``` which recreates a new worker process after 1 crawl
    - The overhead for this is not ideal, and should be solved with a multithreading library
4. ### Extend possible filetypes
    - As of now, this only works with html pages because the text extractor is only for html pages
    - There are packages that allow converstion of documents to html that can then be filtered which can be used 
5. ### Implement proxy rotation
    - I have the crawler set slow enough that it doesent trigger any ip banning, but for robustness we could add ip roation in the middlewares.py file in the crawler folder to mitigate this if it an isssue
6. ### Optimize the Heuristic
    - I used the chatgpt api method to determine relevance, but i think a ML model along with this scraping could work better. 
    - That would require a whole new development process but a promising idea
    - Maybe the LLM could be given, as contenxt, and example of a 10/10 relevance text and a 1/10 relevance text
    - these text could also generated by a seperate ChatGPT API query 
        