# gcgraph
Based on neo4j-flask tutorial by Nicole White.

The Global Citizens Graph is not a social networking application.  The purpose is political networking. The idea is that every person who is alive today is a citizen of planet Earth.  The goal is to create a graph of all of humanity. For more information, see globalreferendum2020.org

John Kintree
March 9, 2016

# neo4j-flask
A microblog application written in Python powered by Flask and Neo4j. Extension of Flask's microblog tutorial, [Flaskr](http://flask.pocoo.org/docs/0.10/tutorial/).

## Usage

Make sure [Neo4j](http://neo4j.com/download/other-releases/) is running first!

**If you're on Neo4j >= 2.2, make sure to set environment variables `NEO4J_USERNAME` and `NEO4J_PASSWORD`
to your username and password, respectively:**

```
$ export NEO4J_USERNAME=username
$ export NEO4J_PASSWORD=password
```

Or, set `dbms.security.auth_enabled=false` in `conf/neo4j-server.properties`.

Then:

```
git clone https://github.com/nicolewhite/neo4j-flask.git
cd neo4j-flask
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

[http://localhost:5000](http://localhost:5000)
