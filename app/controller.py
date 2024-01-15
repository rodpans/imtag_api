from imagekitio import ImageKit
import random
import string
import json
import os

from sqlalchemy import create_engine, text
import requests

import base64

PICTURES_PATH =  os.environ.get('PICTURES_PATH')

class Image_processor:
    def __init__(self, base64_image):
        self.base64_image = base64_image
        self.image_id = ''.join(random.choices(string.digits + string.ascii_lowercase, k=36))
        self.image_name = self.image_id + ".jpg"
        # load credentials from json file
        with open('credentials.json') as f:
            credentials = json.load(f)
        
        self.imagekit = ImageKit(
                            public_key = credentials.get("ImageKit_credentials", {}).get("public_key"),
                            private_key = credentials.get("ImageKit_credentials", {}).get("private_key"),
                            url_endpoint = credentials.get("ImageKit_credentials", {}).get("url_endpoint")
                            )
        
        self.Imaga_credentials = credentials.get("Imaga_credentials", {})

        self.db_user = os.environ.get('DATABASE_USER')
        self.db_password = os.environ.get('DATABASE_PASSWORD')
        self.db_host = os.environ.get('DATABASE_HOST')
        self.db_name = os.environ.get('DATABASE_NAME')

        self.engine = create_engine(f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}")

    def upload_image(self):
        # Generate a random filename for the image of 32 chars
        self.upload_info = self.imagekit.upload(file=self.base64_image, file_name= self.image_name)
    
    def delete_image(self):
        self.delete = self.imagekit.delete_file(file_id=self.upload_info.file_id)
    
    def get_tags(self, min_confidence = 80):
        response = requests.get(f"https://api.imagga.com/v2/tags?image_url={self.upload_info.url}", auth=(self.Imaga_credentials["public_key"], self.Imaga_credentials["private_key"]))
        self.tags = [
            {
                "tag": t["tag"]["en"],
                "confidence": t["confidence"]
            }
            for t in response.json()["result"]["tags"]
            if t["confidence"] > min_confidence
        ]

    def save_image_to_folder(self):
        with open(f"{PICTURES_PATH}/{self.image_name}", "wb") as file:
            # Transform base64 to binary and save it to folder
            file.write(base64.b64decode(self.base64_image))
    
    def insert_image_to_database(self):
        with self.engine.connect() as conn:
            result = conn.execute(text(f"INSERT INTO pictures (id, path) VALUES ('{self.image_id}','{self.image_name}')"))
            # Get values for default column date
            result = conn.execute(text(f"SELECT date FROM pictures WHERE id = '{self.image_id}'"))
            self.date = result.fetchone()[0]
        
            for tags_data in self.tags:
                tag = tags_data["tag"]
                confidence = tags_data["confidence"]
                result = conn.execute(text(f"INSERT INTO tags (tag, picture_id, confidence) VALUES ('{tag}', '{self.image_id}', {confidence})"))
            conn.commit()
    
    def confirmation(self):
        # Get size of file in path in kb
        output_dictionary = {
            "image_id": self.image_id,
            "size": os.path.getsize(f"{PICTURES_PATH}/{self.image_name}") / 1000,
            "date": self.date,
            "tags": self.tags,
            "data": self.base64_image
        }
        return output_dictionary
    
def process_image(base64_image: str, min_confidence = 80):
    image_processor = Image_processor(base64_image)
    image_processor.upload_image()
    image_processor.get_tags(min_confidence)
    image_processor.delete_image()
    image_processor.save_image_to_folder()
    image_processor.insert_image_to_database()
    return image_processor.confirmation()

def get_images(engine = None, tags:list = None, min_date:str = None, max_date:str = None):

    if not engine:
        db_user = os.environ.get('DATABASE_USER')
        db_password = os.environ.get('DATABASE_PASSWORD')
        db_host = os.environ.get('DATABASE_HOST')
        db_name = os.environ.get('DATABASE_NAME')

        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

    if not tags: 
        return []

    query = """
            SELECT p.id, p.path, t.tag, t.confidence, t.date
            FROM pictures p
            JOIN tags t ON p.id = t.picture_id
            WHERE p.id IN (
                SELECT picture_id 
                FROM tags 
                WHERE tag IN (__tags__)
                GROUP BY picture_id 
                HAVING COUNT(DISTINCT tag) = __ntags__
            )
            __mindate__ __maxdate__
            ORDER BY p.id, t.date;
            """

    tag_string = ", ".join([f"'{tag}'" for tag in tags])
    ntags = len(tags)

    query = query.replace("__tags__", tag_string)
    query = query.replace("__ntags__", str(ntags))

    if min_date:
        query = query.replace("__mindate__", f"AND p.date >= '{min_date}'")
    else:
        query = query.replace("__mindate__", "")
    
    if max_date:
        query = query.replace("__maxdate__", f"AND p.date <= '{max_date}'")
    else:
        query = query.replace("__maxdate__", "")

    with engine.connect() as conn:
        result = conn.execute(text(query))
        result = result.fetchall()

    output = {}
    for id, path, tag, confidence, date in result:
        if id not in output.keys():
            try:
                image_size = os.path.getsize(f"{PICTURES_PATH}/{path}") / 1000
            except FileNotFoundError:
                image_size = None

            output[id] = {
                "id": id,
                "size": image_size,
                "path": path,
                "date": date,
                "tags": [{tag : confidence}]
            }
        else:
            output[id]["tags"].append({tag : confidence})

    # We convert the dictionary to a list
    output = list(output.values())
    
    return output

def get_image(id:str, engine = None):

    if not engine:
        db_user = os.environ.get('DATABASE_USER')
        db_password = os.environ.get('DATABASE_PASSWORD')
        db_host = os.environ.get('DATABASE_HOST')
        db_name = os.environ.get('DATABASE_NAME')

        engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")


    query_string = f"""SELECT p.id, p.path, p.date, t.tag, t.confidence 
                    FROM pictures p 
                    LEFT JOIN tags t 
                    ON p.id = t.picture_id 
                    WHERE p.id = '{id}'"""
    
    with engine.connect() as conn:
        result = conn.execute(text(query_string))
        result = result.fetchall()

    if not result:
        return {}

    for id, path, date, tag, confidence in result:
        if 'output' in locals():
            output["tags"].append({tag : confidence})
        else:
            try:
                image_size = os.path.getsize(f"{PICTURES_PATH}/{path}") / 1000
            except FileNotFoundError:
                image_size = None
            
            # Load image as base64
            with open(f"{PICTURES_PATH}/{path}", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                encoded_string = encoded_string.decode('utf-8')

            output = {
                "id": id,
                "size": image_size,
                "date": date,
                "tags": [{tag : confidence}],
                "data": encoded_string
            }
    return output


if __name__ == "__main__":
    ## Read image test.jpg and encode it to base64
    with open("testimage.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    # Run other operations

