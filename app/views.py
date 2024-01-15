from flask import Blueprint, request, make_response
import controller
import aux_functions

image_bp = Blueprint('image', __name__, url_prefix='/')


@image_bp.post("/image")
def post_image():
    # Check if there is a body and if it is a json
    if not request.is_json:
        return make_response("Body must be a json", 400)
    
    if not request.json.get("data"):
        return make_response("Field data missing in json", 400)
    
    # check if there is a query parameter named min_confidence
    min_confidence = request.args.get("min_confidence", 80)

    if not min_confidence.isnumeric():
        return make_response("min_confidence must be a number", 400)
    
    data = request.json.get("data")
    min_confidence = int(min_confidence)

    response = controller.process_image(data, min_confidence)   
    
    return make_response(response, 200)

@image_bp.get("/images")
def get_images():
    
    tags = request.args.get("tags", None)
    print(tags)
    min_date = request.args.get("min_date", None)
    max_date = request.args.get("max_date", None)

    if not tags:
        return make_response("tags parameter is missing", 400)
    # Check that all inputs are strings and check that min_date and max_date are valid dates in format YYYY-MM-DD HH:MM:SS
    elif tags and not isinstance(tags, str):
        return make_response("tags must be a string", 400)
    # We convert tags into a list of strings
    else:
        tags = tags.split(",")
        # We remove empty tags and make them all lowercase
        tags = [tag.lower() for tag in tags if tag]
        tags = list(set(tags))
    
    if min_date and not isinstance(min_date, str):
        return make_response("min_date must be a string", 400)
    
    if max_date and not isinstance(max_date, str):
        return make_response("max_date must be a string", 400)
    
    if min_date and not aux_functions.is_valid_date(min_date):
        return make_response("min_date is not a valid date YYYY-MM-DD HH:MM:SS", 400)
    
    if max_date and not aux_functions.is_valid_date(max_date):
        return make_response("max_date is not a valid date. Date must be of format YYYY-MM-DD HH:MM:SS", 400)
    
    response = controller.get_images(tags=tags, min_date=min_date, max_date=max_date)
    
    return make_response(response, 200)

@image_bp.get("/image/<image_id>")
def get_image(image_id):
    # Check that image_id is a string
    if not isinstance(image_id, str):
        return make_response("image_id must be a string", 400)
    
    response = controller.get_image(image_id)
    
    return make_response(response, 200)