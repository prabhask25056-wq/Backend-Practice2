import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client




# ---------------- Load environment variables (secrets) ---------------- #
from dotenv import load_dotenv
load_dotenv()




# ---------------- Create Flask App ---------------- #
app = Flask(__name__)
CORS(app)




# ---------------- Supabase connection setup ---------------- #
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)




# ---------------- Default Image ---------------- #
NO_IMAGE_URL = "https://development-and-testing-bucket-abcdxyz1234.s3.ap-south-1.amazonaws.com/no-pictures.png"




# ---------------- ROUTES ---------------- #
@app.route("/")
def base_app():
   return {
       "status": "App is running..."
   }




# Here we read all products
@app.route("/products")
def read_all_products():
   res = supabase.table("products").select("*").execute()
   return {
       "products": res.data
   }




# Here we create a new product in our database
@app.route("/products", methods=["POST"])
def create_product():
  
   data = request.get_json()
  
   if not data or not data.get("title"):
       return {"error": "title is required"}, 400


   if not data.get("price"):
       return {"error": "price is required"}, 400


   if not data.get("rating"):
       return {"error": "rating is required"}, 400


   new_product = {
       "title": data["title"],
       "price": data["price"],
       "rating": data["rating"],
       "thumbnail": data.get("thumbnail", NO_IMAGE_URL),
   }


   res = supabase.table("products").insert(new_product).execute()


   return { "product": res.data }, 201




# Here we delete a product from database by product-id
# for example --> DELETE http://localhost:3000/products/2
# for example --> DELETE http://localhost:3000/products/3
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):


   # Here we check if product exists (optional but good practice)
   check = supabase.table("products").select("*").eq("id", product_id).execute()


   if not check.data:
       return {"error": "Product not found"}, 404


   # Here we delete the product (only if the given product id was correct)
   res = supabase.table("products").delete().eq("id", product_id).execute()


   return {
       "message": "Product deleted successfully",
       "data": res.data
   }






# Here we update a product in database by product-id
# for example --> PUT http://localhost:5001/products/2
@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):


   data = request.get_json()


   if not data:
       return {"error": "No data provided"}, 400


   # Check if product exists
   check = supabase.table("products").select("*").eq("id", product_id).execute()


   if not check.data:
       return {"error": "Product not found"}, 404


   if "price" in data and data["price"] <= 0:
       return {"error": "Invalid price"}, 400


   # Perform update
   res = supabase.table("products").update(data).eq("id", product_id).execute()


   return {
       "message": "Product updated successfully",
       "product": res.data
   }






# ---------------- Run the App ---------------- #
if __name__ == "__main__":
   app.run(port=5001, debug=True)
