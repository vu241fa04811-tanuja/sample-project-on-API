from flask import Flask,jsonify,request,render_template
import razorpay

app=Flask(__name__)

payment_client=razorpay.Client(auth=("rzp_test_SuFT7c4tlAXIXQ","jzzGmaGNZVx924PEqYj0knxb"))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/create-order')
def create_order():
    order=payment_client.order.create({
        "amount":10000,
        "currency":"INR"
    })
    return jsonify(order)
    
if __name__=="__main__":
    app.run(debug=True)