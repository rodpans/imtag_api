# imtag_api

Before following up, this API uses two services: ImageKit and Imaga, one for temporary picture storage and the other one for tag identification.
You can easily replace them by your own custom solutions, but as this is a test I do not want to spend time doing that. YoloV5 can be an easy alternative to Imaga.
To use those services you must provide credentials, so you must create a file named **credentials.json** inside app folder and provide your credentials with the following format.
```
{
    "ImageKit_credentials" : {
        "public_key" : "",
        "private_key" : "",
        "url_endpoint" : ""

    },

    "Imaga_credentials" : {
        "public_key" : "",
        "private_key" : "",
        "url_endpoint" : ""
    }
}
```
This app is designed to be deployed using docker compose. You can just get it up and running by moving to your directory folder:

```
cd /your_path_to_the_app
docker compose up
```

After this you can start using the API endpoints

# API Endpoints

## 1. POST /image

This endpoint is used for processing images.

### Request

- **Method:** POST
- **URL:** `/image`
- **Body:** JSON containing a field `data`.
- **Query Parameter:** `min_confidence` (optional, defaults to 80 if not provided).

### Body Format

```json
{
  "data": "<image-data>"
}
```

## 2. GET /images

This endpoint retrieves images based on tags and date filters.

### Request

- **Method:** GET
- **URL:** `/images`
- **Query Parameters:** 
  - `tags`: A comma-separated string of tags. This parameter is required.
  - `min_date`: Minimum date filter in the format `YYYY-MM-DD HH:MM:SS`. This parameter is optional.
  - `max_date`: Maximum date filter in the format `YYYY-MM-DD HH:MM:SS`. This parameter is optional.

### Response

- **Status Code:** 
  - 200: Success.
  - 400: Bad request.
- **Content:** A list of images that match the specified criteria.

### Error Handling

- Returns a 400 status code if the `tags` parameter is missing or not a string.
- Returns a 400 status code if `min_date` or `max_date` are not valid strings or not in the correct format.

## 3. GET /image/<image_id>

This endpoint retrieves a specific image by its unique identifier.

### Request

- **Method:** GET
- **URL:** `/image/<image_id>`
- **URL Parameters:** 
  - `image_id`: The unique identifier of the image. This parameter is required.

### Response

- **Status Code:** 
  - 200: Success.
  - 400: Bad request.
- **Content:** The image data corresponding to the provided `image_id`.

### Error Handling

- Returns a 400 status code if `image_id` is not a string.
