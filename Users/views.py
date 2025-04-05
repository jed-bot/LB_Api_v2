from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from mongoDB_connection.settings import mongo_db
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime,timedelta 
from django.conf import settings
import jwt
from .predict import predict_image
import tempfile
import os
import bcrypt
#get method for the fullname and email
def get_users(request):
    if request.method == 'GET':
        try:
            users_collection = mongo_db["users"]
            users = list(users_collection.find({}, {"_id": 0, "password": 0}))  # Exclude password too
            return JsonResponse({"users": users}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
#defining function register user
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_name = data.get('full_name')
            email = data.get('email')
            password = data.get('password')

            # Validation
            if not all([full_name, email, password]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            users_collection = mongo_db["users"]
            
            # Check if user exists
            if users_collection.find_one({"full_name": full_name}):
                return JsonResponse({'error': 'Username already exists'}, status=400)
                
            if users_collection.find_one({"email": email}):
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            # Create user document
            user_data = {
                "full_name": full_name,
                "email": email,
                "password": make_password(password),
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow(),
            }
            
            # Insert into MongoDB
            result = users_collection.insert_one(user_data)
            
            # Return success response
            return JsonResponse({
                "message": "User created successfully",
                "user_id": str(result.inserted_id),
                "full_name": full_name
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # Handle non-POST methods
    return JsonResponse({'error': 'Method not allowed'}, status=405)
#defining function for the log in user
@csrf_exempt
def log_in_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not all([ email, password]):
                return JsonResponse({'error': 'All fields are required'}, status=400)
            # validation
            if not email or not password:
                return JsonResponse({'error':'All fields are required'},status= 400)
            users_collection = mongo_db["users"]
            #Verify email and password
            user = users_collection.find_one({"email": email})

            if not user or not check_password(password, user['password']):
                return JsonResponse({'error': 'Invalid email ot password'},status = 400)
            #Generating bearer token for the users
            token_payload = {
                'user_id' : str(user['_id']),
                'email': user['email'],
                'exp':datetime.utcnow()+timedelta(hours = 3)# the token will expire in 3 hours
            }
            
            token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm = 'HS256')
            return JsonResponse({
                'message': 'Login successful',
                'bearer_token': token,
                "users": {
                    'user_id': str(user['_id']),
                    'full_name': user['full_name'],
                    'email': user['email']
                }
                },status= 200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
#creating a function for reset password
@csrf_exempt
def reset_password(request):
    if request.method == 'PUT':
        try: 
            data= json.loads(request.body)
            email = data.get('email')
            new_password = data.get('new_password')

            if not email:
                return JsonResponse({'error':'Email is required'}, status = 400)

            #validation
            user_collection = mongo_db["users"]
            user = user_collection.find_one({"email":email})

            if not user:
                return JsonResponse({'error':'email not found'}, status = 400)
            #update password
            user_collection.update_one(
                {"_id": user['_id']},
                {
                    "$set": {
                        "password": make_password(new_password),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return JsonResponse({'message': 'Password Updated'},status= 200)
        except Exception as e:
            return JsonResponse({'error':str(e)}, status = 500)
    return JsonResponse({'error': 'Only put method is allowed'})

#creating a function for editing user profile
@csrf_exempt
@csrf_exempt
def edit_profile(request):
    if request.method == 'PUT':
        try:
            # Handle raw PUT data
            try:
                data = json.loads(request.body.decode('utf-8'))
            except:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
            # Required fields
            current_email = data.get('current_email')
            current_password = data.get('current_password')
            
            # Optional fields
            new_full_name = data.get('new_full_name')
            new_email = data.get('new_email')
            new_password = data.get('new_password')

            # Validate required fields
            if not all([current_email, current_password]):
                return JsonResponse({'error': 'Current email and password are required'}, status=400)

            # Find user
            user = mongo_db['users'].find_one({'email': current_email})
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Verify password
            if not check_password(current_password, user['password']):
                return JsonResponse({'error': 'Invalid current password'}, status=401)

            # Prepare updates
            update_data = {'updated_at': datetime.utcnow()}
            
            if new_full_name:
                update_data['full_name'] = new_full_name
            
            if new_email and new_email != current_email:
                if mongo_db['users'].find_one({'email': new_email, '_id': {'$ne': user['_id']}}):
                    return JsonResponse({'error': 'Email already in use'}, status=400)
                update_data['email'] = new_email
            
            if new_password:
                update_data['password'] = make_password(new_password)

            # Update database
            mongo_db['users'].update_one(
                {'_id': user['_id']},
                {'$set': update_data}
            )

            return JsonResponse({'message': 'Profile updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only PUT requests are allowed'}, status=405)#creating a delete account funtion
@csrf_exempt
def delete_account(request):
    if request.method == 'DELETE':
        try:
            # 1. Parse request
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

            if not all([email, password]):
                return JsonResponse({'error': 'Email and password required'}, status=400)

            # 2. Find user
            users_collection = mongo_db["users"]
            user = users_collection.find_one({"email": email})
            
            # 3. Verify user exists FIRST
            if user is None:  # Explicit None check
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
            # 4. Verify password
            if not check_password(password, user['password']):
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

            # 5. Delete if all checks pass
            result = users_collection.delete_one({"_id": user['_id']})
            
            if result.deleted_count == 1:
                return JsonResponse({'message': 'Account deleted'}, status=200)
            return JsonResponse({'error': 'Deletion failed'}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only DELETE allowed'}, status=405)
#Creating a dunction for image prediction
@csrf_exempt
def classify(request):
    if request.method == 'POST':
        try:
            # Debug: Check what's coming in the request
            print("Request content type:", request.content_type)
            print("Request files:", request.FILES)
            print("Request POST data:", request.POST)

            # Check for image in both FILES and POST
            image_file = request.FILES.get('image') or request.POST.get('image')
            
            if not image_file:
                return JsonResponse(
                    {'error': 'Please provide an image file with key "image"'},
                    status=400
                )

            # Define your class labels (must match model training order)
            class_labels = [
                'Bitter_m', 'Calamansi', 'Eggplant', 'Garlic', 'Ginger',
                'Okra', 'Onion', 'Pork', 'Potato', 'Squash', 'Tomato'
            ]

            # Handle image processing
            if isinstance(image_file, str):
                # Base64 image processing
                import base64
                from io import BytesIO
                from PIL import Image
                from keras.preprocessing import image
                
                try:
                    img_data = image_file.split(',')[1] if ',' in image_file else image_file
                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(BytesIO(img_bytes))
                    img_array = image.img_to_array(img) / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    
                    # Get predictions
                    model = load_model("ingredient_classifier_200_epochs.h5")
                    raw_preds = model.predict(img_array)[0]
                except Exception as e:
                    return JsonResponse(
                        {'error': f'Invalid base64 image: {str(e)}'},
                        status=400
                    )
            else:
                # Regular file upload processing
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    for chunk in image_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                try:
                    raw_preds = predict_image(tmp_path)  # Your existing predict function
                finally:
                    os.unlink(tmp_path)

            # Format predictions with labels and percentages
            paired_predictions = list(zip(class_labels, raw_preds))
            sorted_predictions = sorted(paired_predictions, key=lambda x: x[1], reverse=True)[:3]  # Top 3
            
            formatted_predictions = [
                {
                    "ingredient": label,
                    "confidence": float(confidence),
                    "percentage": f"{float(confidence)*100:.2f}%"
                }
                for label, confidence in sorted_predictions
            ]

            return JsonResponse({
                'predictions': formatted_predictions,
                'message': 'Successfully processed image'
            })

        except Exception as e:
            return JsonResponse(
                {'error': f'Server error: {str(e)}'},
                status=500
            )
    
    return JsonResponse(
        {'error': 'Only POST method allowed'},
        status=405
    )