from py2neo import Graph, Node, Relationship, authenticate
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

if username and password:
    authenticate(url.strip('http://'), username, password)

graph = Graph(url + '/db/data/')

class User:
    def __init__(self, gcemail):
        self.gcemail = gcemail

    def find(self):
        user = graph.find_one("Person", "gcemail", self.gcemail)
        return user

    def findnew(self, gcemail):
	new = graph.find_one("Person", "gcemail", gcemail)
	return new

    def register(self, password, fname, lname, postalcode, zcountry):
        if not self.find():
            user = Node("Person", gcemail=self.gcemail, password=bcrypt.encrypt(password), fname=fname, lname=lname, postalcode=postalcode, 
	    zcountry=zcountry, timestamp=timestamp(), date=date())
            graph.create(user)
            return True
        else:
            return False

    def add_person(self, gcemail, password, fname, lname, postalcode, zcountry, relationship):
	if not self.findnew(gcemail):
	    user = self.find()
            person = Node("Person", gcemail=gcemail, password=bcrypt.encrypt(password), fname=fname, lname=lname, postalcode=postalcode, 
	    zcountry=zcountry, timestamp=timestamp(), date=date())
            rel = Relationship(user, "CONNECTED", person)
            graph.create(rel)
	    relationship = relationship.upper()
	    rel = Relationship(user, relationship, person)
            graph.create(rel)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

    def add_post(self, title, tags, text):
        user = self.find()
        post = Node(
            "Post",
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(',')]
        for t in set(tags):
            tag = graph.merge_one("Tag", "name", t)
            rel = Relationship(tag, "TAGGED", post)
            graph.create(rel)

    def like_post(self, post_id):
        user = self.find()
        post = graph.find_one("Post", "id", post_id)
        graph.create_unique(Relationship(user, "LIKED", post))

    def get_recent_posts(self):
        query = """
        MATCH (user:Person)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.gcemail = {gcemail}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT 5
        """

        return graph.cypher.execute(query, gcemail=self.gcemail)

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both blogged about.
        query = """
        MATCH (you:Person)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (they:Person)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE you.gcemail = {gcemail} AND you <> they
        WITH they, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag) AS len
        ORDER BY len DESC LIMIT 3
        RETURN they.gcemail AS similar_user, tags
        """

        return graph.cypher.execute(query, gcemail=self.gcemail)

    def get_commonality_of_user(self, other):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = """
        MATCH (they:Person {gcemail: {they} })
        MATCH (you:Person {gcemail: {you} })
        OPTIONAL MATCH (they)-[:LIKED]->(post:Post)<-[:PUBLISHED]-(you)
        OPTIONAL MATCH (they)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
                       (you)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        RETURN COUNT(DISTINCT post) AS likes, COLLECT(DISTINCT tag.name) AS tags
        """

        return graph.cypher.execute(query, they=other.gcemail, you=self.gcemail)[0]

def get_people_added():
    query = """
    MATCH (user:Person)-[:CONNECTED]->(person:Person)
    RETURN person
    ORDER BY person.timestamp DESC LIMIT 20
    """

#    return graph.cypher.execute(query, gcemail=logged_in_gcemail)
    return graph.cypher.execute(query)

def get_todays_recent_posts():
    query = """
    MATCH (user:Person)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.gcemail AS gcemail, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp DESC LIMIT 5
    """

    return graph.cypher.execute(query, today=date())

def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%Y-%m-%d')
